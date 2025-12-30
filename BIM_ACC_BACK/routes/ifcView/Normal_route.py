import json

from flask import Blueprint, request, jsonify
import sqlite3
normal_bp = Blueprint('normal', __name__)

@normal_bp.route('/ifcView/normal', methods=['POST'])

def normal():
    list = []
    guid_list = []

    # 连接到数据库
    conn = sqlite3.connect(r'instance/data.db')
    cursor = conn.execute("select * from 结果_8_合规性审查 where judgment_result = '不适用'")
    rows = cursor.fetchall()
    for row in rows:
        list.append(row[2])

    conn.close()

    for item in list:
        list_json = json.loads(item)
        guid_list.append(list_json[1]['guid'])
    return jsonify(guid_list)