from flask import Blueprint, jsonify, request
import os
import json
import pymysql

# 创建蓝图
analysis_bp = Blueprint('analysis', __name__)

# 数据库基础配置（不含具体数据库名）
BASE_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # 替换为你的密码
    'port': 3306,
    'charset': 'utf8mb4'
}


def create_database(db_name):
    """创建指定名称的数据库（如果不存在）"""
    # 连接时不指定数据库
    conn_config = BASE_DB_CONFIG.copy()
    if 'database' in conn_config:
        del conn_config['database']

    conn = pymysql.connect(**conn_config)
    try:
        with conn.cursor() as cursor:
            # 处理数据库名中的特殊字符
            safe_db_name = db_name.replace('-', '_').replace(' ', '_')
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{safe_db_name}`")
        conn.commit()
        return safe_db_name
    finally:
        conn.close()


def create_tables(db_name):
    """为指定数据库创建数据表结构"""
    # 复制基础配置并添加数据库名
    db_config = BASE_DB_CONFIG.copy()
    db_config['database'] = db_name

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            # 创建章节表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_code VARCHAR(20) NOT NULL,
                section_name VARCHAR(100) NOT NULL,
                UNIQUE KEY uk_section_code (section_code)
            )
            """)

            # 创建子章节表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subsections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                section_id INT NOT NULL,
                subsection_code VARCHAR(20) NOT NULL,
                subsection_name VARCHAR(100) NOT NULL,
                FOREIGN KEY (section_id) REFERENCES sections(id),
                UNIQUE KEY uk_subsection_code (subsection_code)
            )
            """)

            # 创建条款表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS provisions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subsection_id INT NOT NULL,
                provision_code VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (subsection_id) REFERENCES subsections(id),
                UNIQUE KEY uk_provision_code (provision_code)
            )
            """)
        conn.commit()
    finally:
        conn.close()


def insert_data(db_name, data=None):
    """向指定数据库插入数据，从/insert_data目录下寻找同名JSON文件"""
    # 构建JSON文件路径
    json_file_path = os.path.join('insert_data',f'{db_name}.json')

    # 检查insert_data目录是否存在
    if not os.path.exists('insert_data'):
        print("insert_data目录不存在")
        return False

    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        print(f"找不到对应的数据文件: {json_file_path}")
        return False

    # 读取JSON数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        data = json_data['data']  # 使用文件中的data数据
    except json.JSONDecodeError:
        print(f"{json_file_path}格式错误")
        return False
    except KeyError:
        print(f"{json_file_path}中缺少data字段")
        return False
    except Exception as e:
        print(f"读取{json_file_path}出错: {str(e)}")
        return False

    db_config = BASE_DB_CONFIG.copy()
    db_config['database'] = db_name

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            # 插入章节数据（参考规则导入.py的插入逻辑）
            for section in data:
                section_code = section['section']
                section_name = section['section_name']

                # 插入章节
                cursor.execute("""
                INSERT IGNORE INTO sections (section_code, section_name)
                VALUES (%s, %s)
                """, (section_code, section_name))

                # 获取章节ID
                cursor.execute("SELECT id FROM sections WHERE section_code = %s", (section_code,))
                section_id = cursor.fetchone()[0]

                # 处理子章节
                for subsection in section['section_contents']:
                    subsection_code = subsection['subsection']
                    subsection_name = subsection['subsection_name']

                    # 插入子章节
                    cursor.execute("""
                    INSERT IGNORE INTO subsections (section_id, subsection_code, subsection_name)
                    VALUES (%s, %s, %s)
                    """, (section_id, subsection_code, subsection_name))

                    # 获取子章节ID
                    cursor.execute("""
                    SELECT id FROM subsections 
                    WHERE section_id = %s AND subsection_code = %s
                    """, (section_id, subsection_code))
                    subsection_id = cursor.fetchone()[0]

                    # 处理条款
                    for provision in subsection['subsection_contents']:
                        provision_code = provision['subsubsection']
                        content = provision['subsubsection_contents']

                        # 插入条款
                        cursor.execute("""
                        INSERT IGNORE INTO provisions (subsection_id, provision_code, content)
                        VALUES (%s, %s, %s)
                        """, (subsection_id, provision_code, content))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"插入数据出错: {str(e)}")
        return False
    finally:
        conn.close()


@analysis_bp.route('/rules/database/<db_name>/search', methods=['GET'])
def search_database(db_name):
    """根据关键词搜索数据库中的条款"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({
            'status': 'error',
            'message': '搜索关键词不能为空'
        }), 400

    db_config = BASE_DB_CONFIG.copy()
    db_config['database'] = db_name

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 关联查询并添加模糊搜索条件
            sql = """
            SELECT 
                s.section_code AS section_id,
                s.section_name AS section_name,
                p.provision_code AS item_id,
                p.content AS content
            FROM sections s
            LEFT JOIN subsections sub ON s.id = sub.section_id
            LEFT JOIN provisions p ON sub.id = p.subsection_id
            WHERE p.id IS NOT NULL 
              AND (p.content LIKE %s OR s.section_name LIKE %s OR sub.subsection_name LIKE %s)
            ORDER BY 
                s.section_code,
                sub.subsection_code,
                p.provision_code
            """
            # 构建模糊搜索参数
            search_param = f'%{keyword}%'
            cursor.execute(sql, (search_param, search_param, search_param))
            results = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'database': db_name,
            'data': results,
            'count': len(results)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'搜索数据库失败: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()


@analysis_bp.route('/rules/analysis', methods=['GET'])
def analyze_rules():
    """处理规则分析的接口"""
    # 定义uploads目录路径（确保该目录存在）
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        return jsonify({
            'status': 'error',
            'message': f'uploads目录不存在，请先创建{uploads_dir}目录'
        }), 400

    # 获取uploads目录下的所有文件
    try:
        files = [f for f in os.listdir(uploads_dir)
                 if os.path.isfile(os.path.join(uploads_dir, f))]
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'读取uploads目录失败: {str(e)}'
        }), 500

    if not files:
        return jsonify({
            'status': 'warning',
            'message': 'uploads目录下没有文件'
        }), 200

    result = []
    # 处理每个文件（不跳过非JSON文件）
    for file_name in files:
        # 处理数据库名（去除扩展名，替换特殊字符）
        db_name = os.path.splitext(file_name)[0].replace('-', '_').replace(' ', '_')
        file_path = os.path.join(uploads_dir, file_name)

        try:
            # 执行数据库操作
            create_database(db_name)
            create_tables(db_name)
            # 调用修改后的insert_data，不需要传递data参数
            insert_success = insert_data(db_name)

            if insert_success:
                result.append({
                    'file': file_name,
                    'status': 'success',
                    'database': db_name,
                    'message': '数据处理成功'
                })
            else:
                result.append({
                    'file': file_name,
                    'status': 'insert_error',
                    'database': db_name,
                    'message': '数据库和表已创建，但数据插入失败'
                })

        except Exception as e:
            # 尝试创建数据库即使其他步骤出错
            try:
                create_database(db_name)
                create_tables(db_name)
            except:
                pass
            result.append({
                'file': file_name,
                'status': 'error',
                'database': db_name if 'db_name' in locals() else None,
                'message': f'处理文件时出错: {str(e)}'
            })

    return jsonify({
        'status': 'completed',
        'total_files': len(files),
        'results': result
    }), 200


# 获取规范条文数据库
@analysis_bp.route('/rules/databases', methods=['GET'])
def get_databases():
    """获取所有规范数据库列表"""
    conn_config = BASE_DB_CONFIG.copy()
    if 'database' in conn_config:
        del conn_config['database']

    try:
        conn = pymysql.connect(**conn_config)
        with conn.cursor() as cursor:
            # 查询所有数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()

            # 过滤出我们创建的规范数据库（假设以'rules_'前缀区分）
            rule_databases = []
            for db in databases:
                db_name = db[0]
                # 排除系统数据库和其他无关数据库
                if db_name not in ['information_schema', 'mysql', 'performance_schema', 'sys', 'bim', 'mybatis','gb_t_51234_2017']:
                    rule_databases.append(db_name)

        return jsonify({
            'status': 'success',
            'databases': rule_databases
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取数据库列表失败: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

#  获取数据库规范条文详细信息
@analysis_bp.route('/rules/database/<db_name>', methods=['GET'])
def get_database_info(db_name):
    """获取指定数据库的检索信息（扁平化结构，只包含所需字段）"""
    db_config = BASE_DB_CONFIG.copy()
    db_config['database'] = db_name

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 关联查询获取所有条款信息，只保留所需字段
            sql = """
            SELECT 
                s.section_code AS section_id,  -- 章节编号
                s.section_name AS section_name,  -- 章节名称
                p.provision_code AS item_id,  -- 条款编号
                p.content AS content  -- 条款内容
            FROM sections s
            LEFT JOIN subsections sub ON s.id = sub.section_id
            LEFT JOIN provisions p ON sub.id = p.subsection_id
            WHERE p.id IS NOT NULL  -- 只保留有条款的记录
            ORDER BY 
                s.section_code,  -- 按章节编号排序
                sub.subsection_code,  -- 按子章节编号排序
                p.provision_code  -- 按条款编号排序
            """
            cursor.execute(sql)
            provisions = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'database': db_name,
            'data': provisions
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取数据库信息失败: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()


# 数据动态检索
@analysis_bp.route('/rules/database/<db_name>/search', methods=['GET'])
def search_rules(db_name):
    """根据关键词搜索数据库中的条款"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({
            'status': 'error',
            'message': '搜索关键词不能为空'
        }), 400

    db_config = BASE_DB_CONFIG.copy()
    db_config['database'] = db_name

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 关联查询并添加模糊搜索条件
            sql = """
            SELECT 
                s.section_code AS section_id,
                s.section_name AS section_name,
                p.provision_code AS item_id,
                p.content AS content
            FROM sections s
            LEFT JOIN subsections sub ON s.id = sub.section_id
            LEFT JOIN provisions p ON sub.id = p.subsection_id
            WHERE p.id IS NOT NULL 
              AND (p.content LIKE %s OR s.section_name LIKE %s OR sub.subsection_name LIKE %s)
            ORDER BY 
                s.section_code,
                sub.subsection_code,
                p.provision_code
            """
            # 构建模糊搜索参数
            search_param = f'%{keyword}%'
            cursor.execute(sql, (search_param, search_param, search_param))
            results = cursor.fetchall()

        return jsonify({
            'status': 'success',
            'database': db_name,
            'data': results,
            'count': len(results)
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'搜索数据库失败: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()