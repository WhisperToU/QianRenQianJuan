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
app.register_blueprint(questions_bp, url_prefix='/questions')#支持数据库的增删改查
app.register_blueprint(printing_bp, url_prefix='/printing')#支持根据题目ID集合生成docx试卷与答案
app.register_blueprint(correction_bp, url_prefix='/correction')#面向教师铲鲟学生历史答题记录
app.register_blueprint(assign_bp, url_prefix='/assign')#支持给学生分配试题
app.register_blueprint(students_bp, url_prefix='/students')#获取数据库中学生信息
app.register_blueprint(classes_bp, url_prefix='/classes')#获取数据库中班级信息

if __name__ == '__main__':
    app.run(debug=True, port=5000)
