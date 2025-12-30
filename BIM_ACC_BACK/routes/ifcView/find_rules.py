from flask import Blueprint, request, jsonify
import sqlite3

findRules_bp = Blueprint('findRules', __name__)


@findRules_bp.route('/ifcView/findRules', methods=['POST'])
def findRules():
    # 连接到数据库
    conn = sqlite3.connect(r'instance/data.db')
    cursor = conn.execute("select 规则序号,规范来源,条款编号,规范内容 from 输入_规范列表 ")
    rows = cursor.fetchall()
    conn.close()  # 记得关闭连接
    return jsonify(rows)


# 新增模糊查询接口
@findRules_bp.route('/ifcView/searchRules', methods=['GET'])
def search_rules():
    try:
        keyword = request.args.get('keyword', '', type=str)

        conn = sqlite3.connect(r'instance/data.db')
        cursor = conn.cursor()

        cursor.execute(
            "select 规则序号,规范来源,条款编号,规范内容 from 输入_规范列表 where 内容 like ?",
            (f'%{keyword}%',)
        )

        rows = cursor.fetchall()
        conn.close()

        return jsonify(rows)
    except Exception as e:
        print(f"查询错误: {str(e)}")
        return jsonify([]), 500