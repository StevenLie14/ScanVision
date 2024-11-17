from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from livereload import Server
from server.controllers.user_controller import user_controller
from server.models.user import db,User


load_dotenv()

app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'html'))

login_manager = LoginManager(app)
login_manager.login_view = 'user_controller.login'

app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/"
    f"{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(user_controller, url_prefix='/auth')

db.init_app(app)
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template('home.html')

if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch(os.path.join(os.path.dirname(__file__), '..', 'html'))
    server.watch(os.path.join(os.path.dirname(__file__), '..', 'static'))

    server.serve()
