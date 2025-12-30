import json
import sqlite3
from flask import Blueprint, request, jsonify

getRules_bp = Blueprint('getRules', __name__)

@getRules_bp.route('/ifcView/getRules', methods=['GET'])
def getRules():
    guid = request.args.get('guid')          # 从查询参数取
    if not guid:
        return jsonify({'success': False, 'message': '缺少 guid'}), 400

    try:
        conn = sqlite3.connect(r'instance/data.db')

        sql = '''
                    SELECT
              b.规范内容,
              a.judgment_result
            FROM
              结果_8_合规性审查 a
            INNER JOIN
              输入_规范列表 b
            ON
              a.规则序号 = b.规则序号
            WHERE
              a.IFC实体组 LIKE ?
        '''

        rows = conn.execute(sql, (f'%{guid}%',)).fetchall()
        conn.close()

        data = [{'内容': r[0], '判断结果': r[1]} for r in rows]
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500