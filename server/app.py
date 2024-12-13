from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy


load_dotenv()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'html'))
    
    load_dotenv()

    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.secret_key = os.getenv('SECRET_KEY')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:" 
        f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:3306/"
        f"{os.getenv('DB_NAME')}"
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    try:
        db.init_app(app)
    except Exception:
        print(Exception)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'user_controller.login'

    from controllers.user_controller import user_controller
    from controllers.file_controller import file_controller
    from controllers.image_controller import image_controller
    app.register_blueprint(user_controller, url_prefix='/auth')
    app.register_blueprint(file_controller, url_prefix='/docs')
    app.register_blueprint(image_controller, url_prefix='/image')

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(user_id)

    @app.route('/')
    def index():
        return render_template('home.html')
    return app




