import os
from flask import Blueprint, request, jsonify

# 创建蓝图
upload_bp = Blueprint('upload', __name__)

# 配置上传路径和允许的文件类型
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'json','csv'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route('/rules/uploads', methods=['POST'])
def upload_file():
    """处理文件上传请求（保留原始文件名）"""
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "未找到文件"}), 400

    file = request.files['file']

    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({"success": False, "message": "未选择文件"}), 400

    # 检查文件类型是否允许
    if file and allowed_file(file.filename):
        original_filename = file.filename

        # 拼接保存路径
        file_path = os.path.join(UPLOAD_FOLDER, original_filename)
        file.save(file_path)

        return jsonify({
            "success": True,
            "message": "文件上传成功（保留原始文件名）",
            "original_filename": original_filename,  # 前端上传时的原始文件名
            "saved_filename": original_filename,  # 服务器保存的文件名（安全处理后，通常和原始名一致）
            "path": file_path
        }), 200

    return jsonify({
        "success": False,
        "message": f"不支持的文件类型，允许的类型: {', '.join(ALLOWED_EXTENSIONS)}"
    }), 400