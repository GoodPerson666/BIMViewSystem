from flask import Flask
from flask_cors import CORS  # 解决跨域问题

# 导入 Blueprint
from routes.check.CheckRusults import check_results_bp
from routes.check.Check_details import check_details_bp
# from routes.ifcRules.analysis_rules import analysis_bp
from routes.ifcRules.analysis_rules_csv import analysis_bp

from routes.ifcRules.uploads import upload_bp
from routes.ifcRules.Rule_route import getRules_bp
from routes.ifcView.find_rules import findRules_bp


from routes.ifcView.Compliance_route import compliance_bp
from routes.ifcView.NonCompliance_route import Noncompliance_bp
from routes.ifcView.Normal_route import normal_bp

# 初始化 Flask 应用

app = Flask(__name__)
CORS(app)  # 启用跨域支持

#审查结果
app.register_blueprint(normal_bp)
app.register_blueprint(compliance_bp)
app.register_blueprint(Noncompliance_bp)

app.register_blueprint(getRules_bp)
app.register_blueprint(findRules_bp)

app.register_blueprint(upload_bp)
app.register_blueprint(analysis_bp)
# app.register_blueprint(analysis_csv_bp)

app.register_blueprint(check_details_bp)
# 合规性审查
app.register_blueprint(check_results_bp)



if __name__ == '__main__':
    # 运行 Flask 应用
    app.run(debug=True)