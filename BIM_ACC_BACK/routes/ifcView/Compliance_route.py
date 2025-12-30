import json

from flask import Blueprint, request, jsonify
import sqlite3
compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/ifcView/compliance', methods=['POST'])

def compliance():
    list = []
    guid_list = []

    # 连接到数据库
    conn = sqlite3.connect(r'instance/data.db')
    cursor = conn.execute("select * from 结果_8_合规性审查 where judgment_result = '合规'")
    rows = cursor.fetchall()
    for row in rows:
        list.append(row[2])

    conn.close()

    for item in list:
        list_json = json.loads(item)
        guid_list.append(list_json[1]['guid'])
    return jsonify(guid_list)