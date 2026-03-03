# 用于返回样例数据

import random
import time
from flask import jsonify, Blueprint

check_results_bp = Blueprint('check_results', __name__)

def generate_check_results():

    outputs = [
        '''1）规范来源：建筑设计防火规范；规范内容：耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。规范类型识别结果为：属性约束类。''',
        '''2）规范内容：耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。规范实体识别结果（规范实体-实体类型）为：防火墙-建筑物构件；厂房-建筑物。''',
        '''3）IFC类型为IfcWall的IFC构件（guid，name（IFC类型））有： 0cauBN0lX9uQLK9JxG0zwB，基本墙:常规 - 200mm:221983(IfcWall)；04M84dkEz8GhpqWbHUDGAV，基本墙:常规 - 200mm:243846(IfcWall)；1Dkc0PZSH8QhoXanFZjEP0，基本墙:常规 - 200mm:237969(IfcWall)；IFC类型为IfcBuilding的IFC构件（guid，name（IFC类型））有： 2OibT2UMLBYgfonVRELIuz，(IfcBuilding)''',
        '''4）规范内容：耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。防火墙-建筑物构件的IFC类层级对齐结果为：IfcWall，匹配原因：防火墙作为建筑物构件，最适合映射为IfcWall，因为IFC中的IfcWall专门用于表示墙体构件，符合耐火等级要求的描述。；厂房-建筑物的IFC类层级对齐结果为：IfcBuilding，匹配原因：厂房作为一个建筑物的整体，可以直接映射为IfcBuilding，因为该规范实体描述的是建筑物的性质和功能。''',
        '''5）在IFC实例层级对齐中，与防火墙-建筑物构件对齐的IFC构件有0cauBN0lX9uQLK9JxG0zwB，基本墙:常规 - 200mm:221983(IfcWall)，其匹配原因为：[LLM修正] 在IFC实体中，存在"消防系统"属性集，其中明确指出耐火极限为3.47。这表明该墙体具备一定的防火性能，虽然没有直接标示为防火墙，但耐火极限可以被视为判断其适用于防火墙的依据，因此该判断理由不成立。并且，"是否承重"的属性表示该墙是承重的，进一步证明其结构功能符合防火墙的典型要求。在IFC实例层级对齐中，与厂房-建筑物对齐的IFC构件有2OibT2UMLBYgfonVRELIuz，(IfcBuilding)，其匹配原因为：在IFC实体信息中，虽然没有直接出现"厂房"这一词汇，但在"标识数据"属性集中存在"建筑名称": "工业厂房"，其中的"厂房"与规范实体"厂房"语义等效。因此，这一IFC实体可以被认定为等同于规范实体"厂房"。''',
        '''6）规范内容：耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。规范实体组为[{"text": "厂房","type": "建筑物"},{"text": "防火墙","type": "建筑物构件"}]，对应的IFC实体组为[{"guid": "2OibT2UMLBYgfonVRELIuz","type":"(IfcBuilding)"},{"guid":"0cauBN0lX9uQLK9JxG0zwB","type": "基本墙:常规 - 200mm:221983(IfcWall)"}]。''',
        '''7）规范内容：耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。高相关属性集选择结果为：厂房：工厂耐火等级（选择原因：该属性直接相关于厂房的耐火等级要求，根据规范内容，其防火墙的耐火极限应符合特定等级的标准。）、火灾危险性（选择原因：火灾危险性与耐火设计息息相关，了解火灾危险性有助于确定防火墙的详细设计与耐火极限要求。）；防火墙：耐火极限（选择原因：耐火墙的耐火极限是直接关系到规范内容的核心属性，符合规范要求的耐火限度至关重要。）、是否是防火墙（选择原因：该属性确认该墙体的功能是否为防火墙，确保符合设计和规范要求。）具体属性内容：2OibT2UMLBYgfonVRELIuz工厂耐火等级：三级；火灾危险性：丙级。0cauBN0lX9uQLK9JxG0zwB耐火极限：3.47。''',
        '''8）规范内容：耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。IFC实体组为[{"guid": "2OibT2UMLBYgfonVRELIuz","type":"(IfcBuilding)"},{"guid":"0cauBN0lX9uQLK9JxG0zwB","type": "基本墙:常规 - 200mm:221983(IfcWall)"}]。判断结果：合规。判断原因：根据规范要求，耐火等级为三级的厂房，其防火墙的耐火极限不低于3h。对应的IFC实体2OibT2UMLBYgfonVRELIuz ((IfcBuilding))具备了工厂耐火等级的属性，值为"三级"，满足规范要求中的耐火等级条件。接下来查看对应的IFC实体0cauBN0lX9uQLK9JxG0zwB (基本墙:常规 - 200mm:221983(IfcWall))，其具备耐火极限属性，值为'3.47'，满足规范要求的耐火极限不低于3h。因此判断该规范适用。接下来的合规性分析，IFC实体2OibT2UMLBYgfonVRELIuz的工厂耐火等级为'三级'，0cauBN0lX9uQLK9JxG0zwB的耐火极限为'3.47'，均满足规范要求，故判定为合规。''',
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



