import random
import sqlite3
import time
from flask import jsonify, Blueprint

check_results_bp = Blueprint('check_results', __name__)


# 查询有多少种ifc实体（如门、窗、墙等等）
def ifc_class_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select guid, ifc_type, name  from IFC实体 where guid='2TJvWVuN51mepwyN3rKIGl'"
    rows = conn.execute(sql).fetchall()
    # 返回结果('0CFRT$QsDD89xIDV$SU1iU', 'IfcSlab', '组合楼梯:楼梯:230353 Landing 1')
    return rows[0]


# 查询实体数量（包含多少个guid）
def entity_check_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select count(guid) from IFC实体"
    rows = conn.execute(sql).fetchone()
    return rows[0]


# 查询具体属性个数(查询每个构建对应的属性)
def properties_check_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select count(*) from IFC属性集"
    rows = conn.execute(sql).fetchone()
    return rows[0]


# 查询指定guid的实体名称
def properties_set_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select property_name from IFC属性集 where guid='2TJvWVuN51mepwyN3rKIGl'"
    rows = conn.execute(sql).fetchall()
    return rows


def recognize_rules_type_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规范来源,规范内容,识别类型, 规则序号 from 结果_1_规范类型识别"
    # 返回结果('建筑设计防火规范', '耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。', '属性约束类')
    rows = conn.execute(sql).fetchall()
    return rows


def recognize_rules_properties_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 实体文本,实体类型,规则序号 from 结果_2_规范实体识别_前"
    rows = conn.execute(sql).fetchall()
    # 返回结果为('柱','建筑物构'件','28'),
    return rows


# 实体对齐增强
def entity_strength_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,规范实体文本,ifc_guid,ifc_entity_with_type from 结果_4_实体对齐_新增"
    rows = conn.execute(sql).fetchall()
    return rows


# 构建元组
def tuple_set_results():
    conn = sqlite3.connect(r'instance/data.db')
    sql = "select 规则序号,规范实体组,IFC实体组 from 结果_5_规范元素组"
    rows = conn.execute(sql).fetchall()
    return rows


def generate_check_results():
    recognize_rules = recognize_rules_type_results()[3]
    recognize_rules_properties = recognize_rules_properties_results()[3]
    ifc_class = ifc_class_results()
    entity_check = entity_check_results()
    properties_check = properties_check_results()
    properties_set = properties_set_results()
    entity_strength = entity_strength_results()[0]
    tuple_set = tuple_set_results()[0]
    outputs = [
        f'生成内容：规范类型如下 ——> 规范来源：{recognize_rules[0]}；规范内容：{recognize_rules[1]}；识别类型：{recognize_rules[2]}；规则序号：{recognize_rules[3]}...共计8条',
        f'生成内容：规范实体如下 ——> 实体文本：{recognize_rules_properties[0]}；实体类型：{recognize_rules_properties[1]}；规则序号：{recognize_rules_properties[2]}',
        f'生成内容：识别实体  ——> guid:{ifc_class[0]},ifc_tpye:{ifc_class[1]},name:{ifc_class[2]}',
        f'生成内容：完成实体属性识别、对齐 ，guid为：2TJvWVuN51mepwyN3rKIGl 的构建包含{properties_set}等。{entity_check} 个实体共{properties_check} 条关系映射。',
        f'生成内容：完成规范实体与条文对齐 ——> 根据条文“耐火等级为三级的厂房，其柱的耐火极限不低于2h”，对齐到实体“厂房”、“柱”...',
        f'生成内容：完成规范实体与IFC属性增强对齐，新增:规则序号:{entity_strength[0]}；规范实体文本:{entity_strength[1]}；ifc_guid:{entity_strength[2]}；ifc_entity_with_type:{entity_strength[3]}',
        f'生成内容：构建实体对齐元组 ——> 规则序号：{tuple_set[0]}；规范实体组：{tuple_set[1]}；IFC实体组：{tuple_set[2]} '
    ]
    return outputs


@check_results_bp.route('/check/rusults', methods=['POST'])
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
        # 模拟接口处理耗时（1-2秒），贴近真实业务处理
        time.sleep(random.uniform(1, 2))

        # 生成审查结果
        outputs = generate_check_results()

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



