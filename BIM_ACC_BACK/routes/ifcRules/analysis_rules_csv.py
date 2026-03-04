from flask import Blueprint, jsonify, request, current_app
import os
import json
import sqlite3
from sqlite3 import Error
import csv  # 新增CSV处理模块

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
    """为指定SQLite数据库创建适配CSV的新数据表结构"""
    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # 创建适配CSV的规则表（替代原有三级结构）
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS rules
                       (
                           id               INTEGER PRIMARY KEY AUTOINCREMENT,
                           rule_serial      INTEGER NOT NULL, -- 规则序号
                           standard_source  TEXT    NOT NULL, -- 规范来源
                           clause_number    TEXT    NOT NULL, -- 条款编号
                           subclause_number TEXT    NOT NULL, -- 条款子句序号
                           content          TEXT    NOT NULL, -- 规范内容
                           UNIQUE (rule_serial, standard_source, clause_number, subclause_number)
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
    """向指定SQLite数据库插入CSV数据，从/insert_data目录下寻找同名CSV文件"""
    # 构建CSV文件路径
    csv_file_path = os.path.join('uploads', f'{db_name}.csv')

    # 检查insert_data目录是否存在
    if not os.path.exists('uploads'):
        current_app.logger.error("uploads目录不存在")
        return False

    # 检查CSV文件是否存在
    if not os.path.exists(csv_file_path):
        current_app.logger.error(f"找不到对应的数据文件: {csv_file_path}")
        return False

    # 读取CSV数据
    try:
        csv_data = []
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # 使用DictReader读取CSV，第一行作为表头
            reader = csv.DictReader(f)
            # 验证表头是否符合要求
            required_headers = ['规则序号', '规范来源', '条款编号', '条款子句序号', '规范内容']
            if not all(header in reader.fieldnames for header in required_headers):
                current_app.logger.error(f"{csv_file_path}表头不符合要求，需要包含: {required_headers}")
                return False

            # 读取每一行数据
            for row in reader:
                csv_data.append({
                    'rule_serial': int(row['规则序号']),
                    'standard_source': row['规范来源'].strip(),
                    'clause_number': row['条款编号'].strip(),
                    'subclause_number': row['条款子句序号'].strip(),
                    'content': row['规范内容'].strip()
                })
    except ValueError as e:
        current_app.logger.error(f"{csv_file_path}中规则序号不是数字: {str(e)}")
        return False
    except Exception as e:
        current_app.logger.error(f"读取{csv_file_path}出错: {str(e)}")
        return False

    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # 批量插入CSV数据
        for row in csv_data:
            cursor.execute("""
                           INSERT OR IGNORE INTO rules
                           (rule_serial, standard_source, clause_number, subclause_number, content)
                           VALUES (?, ?, ?, ?, ?)
                           """, (
                               row['rule_serial'],
                               row['standard_source'],
                               row['clause_number'],
                               row['subclause_number'],
                               row['content']
                           ))

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
    """根据关键词搜索数据库中的规则（适配新表结构）"""
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
        # 适配新表结构的搜索SQL
        sql = """
              SELECT rule_serial      AS rule_id,
                     standard_source  AS source,
                     clause_number    AS clause_id,
                     subclause_number AS subclause_id,
                     content          AS content
              FROM rules
              WHERE (content LIKE ?
                  OR standard_source LIKE ?
                  OR clause_number LIKE ?
                  OR subclause_number LIKE ?)
              ORDER BY rule_serial
              """
        # 构建模糊搜索参数
        search_param = f'%{keyword}%'
        cursor.execute(sql, (search_param, search_param, search_param, search_param))
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
    """处理规则分析的接口（适配CSV文件）"""
    # 定义uploads目录路径（确保该目录存在）
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        return jsonify({
            'status': 'error',
            'message': f'uploads目录不存在，请先创建{uploads_dir}目录'
        }), 400

    # 获取uploads目录下的所有CSV文件
    try:
        files = [f for f in os.listdir(uploads_dir)
                 if os.path.isfile(os.path.join(uploads_dir, f))
                 and f.endswith('.csv')]  # 只处理CSV文件
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'读取uploads目录失败: {str(e)}'
        }), 500

    if not files:
        return jsonify({
            'status': 'warning',
            'message': 'uploads目录下没有CSV文件'
        }), 200

    result = []
    # 处理每个CSV文件
    for file_name in files:
        # 处理数据库名（去除扩展名，替换特殊字符）
        db_name = os.path.splitext(file_name)[0].replace('-', '_').replace(' ', '_')
        file_path = os.path.join(uploads_dir, file_name)

        try:
            # 执行数据库操作
            create_database(db_name)
            create_tables(db_name)

            # 先将CSV文件复制到insert_data目录（方便insert_data函数读取）
            import shutil
            os.makedirs('insert_data', exist_ok=True)
            target_path = os.path.join('insert_data', f'{db_name}.csv')
            shutil.copy2(file_path, target_path)

            # 调用insert_data插入CSV数据
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
    """获取指定数据库的规则信息（适配新表结构）"""
    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)

    if not conn:
        return jsonify({
            'status': 'error',
            'message': '数据库连接失败'
        }), 500

    try:
        cursor = conn.cursor()
        # 适配新表结构的查询SQL
        sql = """
              SELECT rule_serial      AS rule_id,
                     standard_source  AS source,
                     clause_number    AS clause_id,
                     subclause_number AS subclause_id,
                     content          AS content
              FROM rules
              ORDER BY rule_serial
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
    # 直接调用已实现的search_database函数
    return search_database(db_name)