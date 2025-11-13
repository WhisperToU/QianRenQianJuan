# 重构后的主 Flask 后端入口文件
# 整合各功能模块：出题、打印、批改、题库管理

from flask import Flask
from routes.questions import questions_bp
from routes.printing import printing_bp
from routes.correction import correction_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 注册功能模块（Blueprints）
app.register_blueprint(questions_bp, url_prefix='/questions')
app.register_blueprint(printing_bp, url_prefix='/printing')
app.register_blueprint(correction_bp, url_prefix='/correction')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
