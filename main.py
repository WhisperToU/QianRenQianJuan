# 重构后的主 Flask 后端入口文件
# 整合各功能模块：出题、打印、批改、题库管理

from flask import Flask
from routes.questions import questions_bp
from routes.printing import printing_bp
from routes.correction import correction_bp
from routes.assign import assign_bp
from flask_cors import CORS
from routes.students import students_bp
from routes.classes import classes_bp


app = Flask(__name__)
CORS(app)

# 注册功能模块（Blueprints）
app.register_blueprint(questions_bp, url_prefix='/questions')
app.register_blueprint(printing_bp, url_prefix='/printing')
app.register_blueprint(correction_bp, url_prefix='/correction')
app.register_blueprint(assign_bp, url_prefix='/assign')
app.register_blueprint(students_bp, url_prefix='/students')
app.register_blueprint(classes_bp, url_prefix='/classes')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
