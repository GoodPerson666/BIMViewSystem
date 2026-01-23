from flask import Blueprint, jsonify, request, current_app
import os
import json
import sqlite3
from sqlite3 import Error

# 创建蓝图
analysis_bp = Blueprint('analysis', __name__)

# 定义数据库存储根目录
DB_ROOT_DIR = 'rules_db'


# SQLite连接工具函数
def get_db_connection(db_path):
    """创建并返回SQLite数据库连接"""
    conn = None
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # 连接SQLite数据库（不存在则自动创建）
        conn = sqlite3.connect(db_path)
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        # 设置返回结果为字典格式
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        current_app.logger.error(f"数据库连接错误: {e}")
        return None


def get_db_path(db_name):
    """获取数据库文件的完整路径（存储到rules_db目录）"""
    # 拼接rules_db目录下的数据库文件路径
    return os.path.join(DB_ROOT_DIR, f"{db_name}.db")


def create_database(db_name):
    """创建指定名称的SQLite数据库（文件形式，不存在则自动创建）"""
    db_path = get_db_path(db_name)
    # 只需尝试连接即可创建空数据库文件
    conn = get_db_connection(db_path)
    if conn:
        conn.close()
        return db_name
    return None


def create_tables(db_name):
    """为指定SQLite数据库创建数据表结构"""
    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # 创建章节表（SQLite的自增主键使用INTEGER PRIMARY KEY AUTOINCREMENT）
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS sections
                       (
                           id           INTEGER PRIMARY KEY AUTOINCREMENT,
                           section_code TEXT NOT NULL,
                           section_name TEXT NOT NULL,
                           UNIQUE (section_code)
                       )
                       """)

        # 创建子章节表
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS subsections
                       (
                           id              INTEGER PRIMARY KEY AUTOINCREMENT,
                           section_id      INTEGER NOT NULL,
                           subsection_code TEXT    NOT NULL,
                           subsection_name TEXT    NOT NULL,
                           FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE CASCADE,
                           UNIQUE (subsection_code)
                       )
                       """)

        # 创建条款表
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS provisions
                       (
                           id             INTEGER PRIMARY KEY AUTOINCREMENT,
                           subsection_id  INTEGER NOT NULL,
                           provision_code TEXT    NOT NULL,
                           content        TEXT    NOT NULL,
                           FOREIGN KEY (subsection_id) REFERENCES subsections (id) ON DELETE CASCADE,
                           UNIQUE (provision_code)
                       )
                       """)

        conn.commit()
        return True
    except Error as e:
        current_app.logger.error(f"创建表失败: {e}")
        return False
    finally:
        if conn:
            conn.close()


def insert_data(db_name, data=None):
    """向指定SQLite数据库插入数据，从/insert_data目录下寻找同名JSON文件"""
    # 构建JSON文件路径
    json_file_path = os.path.join('insert_data', f'{db_name}.json')

    # 检查insert_data目录是否存在
    if not os.path.exists('insert_data'):
        current_app.logger.error("insert_data目录不存在")
        return False

    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        current_app.logger.error(f"找不到对应的数据文件: {json_file_path}")
        return False

    # 读取JSON数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        data = json_data['data']  # 使用文件中的data数据
    except json.JSONDecodeError:
        current_app.logger.error(f"{json_file_path}格式错误")
        return False
    except KeyError:
        current_app.logger.error(f"{json_file_path}中缺少data字段")
        return False
    except Exception as e:
        current_app.logger.error(f"读取{json_file_path}出错: {str(e)}")
        return False

    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # 插入章节数据
        for section in data:
            section_code = section['section']
            section_name = section['section_name']

            # 插入章节（SQLite的INSERT OR IGNORE）
            cursor.execute("""
                           INSERT OR IGNORE INTO sections (section_code, section_name)
                           VALUES (?, ?)
                           """, (section_code, section_name))

            # 获取章节ID
            cursor.execute("SELECT id FROM sections WHERE section_code = ?", (section_code,))
            section_id = cursor.fetchone()[0]

            # 处理子章节
            for subsection in section['section_contents']:
                subsection_code = subsection['subsection']
                subsection_name = subsection['subsection_name']

                # 插入子章节
                cursor.execute("""
                               INSERT OR IGNORE INTO subsections (section_id, subsection_code, subsection_name)
                               VALUES (?, ?, ?)
                               """, (section_id, subsection_code, subsection_name))

                # 获取子章节ID
                cursor.execute("""
                               SELECT id
                               FROM subsections
                               WHERE section_id = ?
                                 AND subsection_code = ?
                               """, (section_id, subsection_code))
                subsection_id = cursor.fetchone()[0]

                # 处理条款
                for provision in subsection['subsection_contents']:
                    provision_code = provision['subsubsection']
                    content = provision['subsubsection_contents']

                    # 插入条款
                    cursor.execute("""
                                   INSERT OR IGNORE INTO provisions (subsection_id, provision_code, content)
                                   VALUES (?, ?, ?)
                                   """, (subsection_id, provision_code, content))

        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        current_app.logger.error(f"插入数据出错: {str(e)}")
        return False
    finally:
        if conn:
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

    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return jsonify({
            'status': 'error',
            'message': '数据库连接失败'
        }), 500

    try:
        cursor = conn.cursor()
        # 关联查询并添加模糊搜索条件（SQLite的LIKE）
        sql = """
              SELECT s.section_code   AS section_id, \
                     s.section_name   AS section_name, \
                     p.provision_code AS item_id, \
                     p.content        AS content
              FROM sections s
                       LEFT JOIN subsections sub ON s.id = sub.section_id
                       LEFT JOIN provisions p ON sub.id = p.subsection_id
              WHERE p.id IS NOT NULL
                AND (p.content LIKE ? OR s.section_name LIKE ? OR sub.subsection_name LIKE ?)
              ORDER BY s.section_code, \
                       sub.subsection_code, \
                       p.provision_code \
              """
        # 构建模糊搜索参数
        search_param = f'%{keyword}%'
        cursor.execute(sql, (search_param, search_param, search_param))
        results = cursor.fetchall()

        # 转换Row对象为字典
        result_list = [dict(row) for row in results]

        return jsonify({
            'status': 'success',
            'database': db_name,
            'data': result_list,
            'count': len(result_list)
        }), 200

    except Error as e:
        current_app.logger.error(f"搜索数据库失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'搜索数据库失败: {str(e)}'
        }), 500
    finally:
        if conn:
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
    # 处理每个文件
    for file_name in files:
        # 处理数据库名（去除扩展名，替换特殊字符）
        db_name = os.path.splitext(file_name)[0].replace('-', '_').replace(' ', '_')
        file_path = os.path.join(uploads_dir, file_name)

        try:
            # 执行数据库操作
            create_database(db_name)
            create_tables(db_name)
            # 调用insert_data，不需要传递data参数
            insert_success = insert_data(db_name)

            if insert_success:
                result.append({
                    'file': file_name,
                    'status': 'success',
                    'database': db_name,
                    'message': '数据处理成功',
                    'db_path': get_db_path(db_name)
                })
            else:
                result.append({
                    'file': file_name,
                    'status': 'insert_error',
                    'database': db_name,
                    'message': '数据库和表已创建，但数据插入失败',
                    'db_path': get_db_path(db_name)
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
                'message': f'处理文件时出错: {str(e)}',
                'db_path': get_db_path(db_name) if 'db_name' in locals() else None
            })

    return jsonify({
        'status': 'completed',
        'total_files': len(files),
        'results': result
    }), 200


# 获取规范条文数据库
@analysis_bp.route('/rules/databases', methods=['GET'])
def get_databases():
    """获取所有规范数据库列表（rules_db目录下的.db文件）"""
    try:
        # 确保rules_db目录存在
        os.makedirs(DB_ROOT_DIR, exist_ok=True)

        # 列出rules_db目录下所有.db文件
        db_files = [f for f in os.listdir(DB_ROOT_DIR)
                    if os.path.isfile(os.path.join(DB_ROOT_DIR, f))
                    and f.endswith('.db')]

        # 提取数据库名（去除.db后缀）
        rule_databases = [os.path.splitext(f)[0] for f in db_files]

        return jsonify({
            'status': 'success',
            'databases': rule_databases
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取数据库列表失败: {str(e)}'
        }), 500


# 获取数据库规范条文详细信息
@analysis_bp.route('/rules/database/<db_name>', methods=['GET'])
def get_database_info(db_name):
    """获取指定数据库的检索信息（扁平化结构，只包含所需字段）"""
    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return jsonify({
            'status': 'error',
            'message': '数据库连接失败'
        }), 500

    try:
        cursor = conn.cursor()
        # 关联查询获取所有条款信息
        sql = """
              SELECT s.section_code   AS section_id, \
                     s.section_name   AS section_name, \
                     p.provision_code AS item_id, \
                     p.content        AS content
              FROM sections s
                       LEFT JOIN subsections sub ON s.id = sub.section_id
                       LEFT JOIN provisions p ON sub.id = p.subsection_id
              WHERE p.id IS NOT NULL
              ORDER BY s.section_code, \
                       sub.subsection_code, \
                       p.provision_code \
              """
        cursor.execute(sql)
        provisions = cursor.fetchall()

        # 转换Row对象为字典
        provision_list = [dict(row) for row in provisions]

        return jsonify({
            'status': 'success',
            'database': db_name,
            'data': provision_list
        }), 200

    except Error as e:
        current_app.logger.error(f"获取数据库信息失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取数据库信息失败: {str(e)}'
        }), 500
    finally:
        if conn:
            conn.close()


@analysis_bp.route('/rules/database/<db_name>/search', methods=['GET'])
def search_rules(db_name):
    """根据关键词搜索数据库中的条款"""
    # 直接调用已实现的search_database函数
    return search_database(db_name)