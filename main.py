# Main Flask application entrypoint
from flask import Flask
from flask_cors import CORS

from routes.questions import questions_bp
from routes.printing import printing_bp
from routes.correction import correction_bp
from routes.assign import assign_bp
from routes.students import students_bp
from routes.classes import classes_bp
from routes.ai_public import ai_public_bp
from routes.ai_secure import ai_secure_bp
from routes.auth import auth_bp
from routes.conversations import conversations_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(questions_bp, url_prefix="/questions")
app.register_blueprint(printing_bp, url_prefix="/printing")
app.register_blueprint(correction_bp, url_prefix="/correction")
app.register_blueprint(assign_bp, url_prefix="/assign")
app.register_blueprint(students_bp, url_prefix="/students")
app.register_blueprint(classes_bp, url_prefix="/classes")
app.register_blueprint(ai_public_bp, url_prefix="/ai/public")  # no-auth chat
app.register_blueprint(ai_secure_bp, url_prefix="/ai/secure")  # auth-required AI
app.register_blueprint(conversations_bp, url_prefix="/conversations")
app.register_blueprint(auth_bp, url_prefix="/auth")

if __name__ == "__main__":
  app.run(debug=True, port=5000, use_reloader=False)
