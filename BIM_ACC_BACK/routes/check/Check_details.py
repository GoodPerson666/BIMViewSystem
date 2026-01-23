import sqlite3
import json
from flask import jsonify, Blueprint

check_details_bp = Blueprint('check_details', __name__)

# 第一部分：规范类型识别
def recognize_rules_type_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规范来源,规范内容,识别类型, 规则序号 from 结果_1_规范类型识别 "
    # 返回结果('建筑设计防火规范', '耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。', '属性约束类')
    rows = conn.execute(sql).fetchall()
    return rows


# 第二部分：规范实体识别
def recognize_rules_properties_front_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 实体文本,实体类型,规则序号 from 结果_2_规范实体识别_前 "
    rows = conn.execute(sql).fetchall()
    # 返回结果为('柱','建筑物构'件','28'),
    return rows


def recognize_rules_properties_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 实体文本,实体类型,规则序号 from 结果_2_规范实体识别"
    rows = conn.execute(sql).fetchall()
    # 返回结果为('柱','建筑物构'件','28'),
    return rows


# 第三部分：IFC类型识别、IFC实体属性识别
def ifc_class_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select guid, ifc_type, name  from IFC实体 limit 500"
    rows = conn.execute(sql).fetchall()
    return rows

def properties_set_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select guid, property_set_name, property_name from IFC属性集 limit 500"
    rows = conn.execute(sql).fetchall()
    return rows

# 第四部分：规范实体与条文对齐
def entities_to_rules():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "SELECT 规范内容, GROUP_CONCAT(规范实体, ', ') AS 同一规范下的所有实体 FROM 结果_4_实体类型对齐 GROUP BY 规范内容 "
    rows = conn.execute(sql).fetchall()
    return rows


# 第五部分：实体对齐
def entity_strength_front_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,规范实体文本,ifc_guid,ifc_entity_with_type from 结果_4_实体对齐_前"
    rows = conn.execute(sql).fetchall()
    return rows

def entity_strength_new_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,规范实体文本,ifc_guid,ifc_entity_with_type from 结果_4_实体对齐_新增 "
    rows = conn.execute(sql).fetchall()
    return rows

def entity_strength_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,规范实体文本,ifc_guid,ifc_entity_with_type from 结果_4_实体对齐 "
    rows = conn.execute(sql).fetchall()
    return rows

# 第六部分：实体对齐增强构建元组
def tuple_set_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,规范实体组,IFC实体组 from 结果_5_规范元素组 "
    rows = conn.execute(sql).fetchall()
    return rows

# 第七部分：选择策略和相关属性
def choose_strategy_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select * from 结果_6_规范属性选择策略  "
    rows = conn.execute(sql).fetchall()
    return rows

def relate_entities_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,ifc_guid,property_set_name,property_name,property_value from 结果_7_相关属性"
    rows = conn.execute(sql).fetchall()
    return rows

# 第八部分：合规性审查
def compliance_check_results():
    list = []
    guid = []
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select * from 结果_8_合规性审查 limit 100 "
    cursor = conn.execute(sql)
    rows = cursor.fetchall()

    for row in rows:
        guid_json = json.loads(row[2])
        guid = guid_json[1]['guid']
        list.append((row[0], row[1], guid, row[5]))
    return list


def check_details():
    outputs=[
        # 结果1
        recognize_rules_type_results(),
        # 结果2
        recognize_rules_properties_front_results(),
        recognize_rules_properties_results(),
        # 结果3
        ifc_class_results(),
        properties_set_results(),
        #结果4
        entities_to_rules(),
        #结果5
        entity_strength_front_results(),
        entity_strength_new_results(),
        entity_strength_results(),
        #结果6
        tuple_set_results(),
        # 结果7
        choose_strategy_results(),
        relate_entities_results(),
        #结果8
        compliance_check_results()
    ]
    return outputs


@check_details_bp.route('/check/rusults/details', methods=['POST'])
def get_check_results():
    """
    审查结果接口
    返回格式：{
        "code": 200,
        "msg": "success",
        "outputs": [...]  # 对应前端需要的输出数据
    }
    """
    try:
        # 生成审查结果
        outputs = check_details()

        # 返回JSON响应
        return jsonify({
            'code': 200,
            'msg': 'success',
            'outputs': outputs
        }), 200

    except Exception as e:
        # 异常处理
        return jsonify({
            'code': 500,
            'msg': f'服务器错误：{str(e)}',
            'outputs': []
        }), 500