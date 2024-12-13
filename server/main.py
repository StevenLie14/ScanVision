from app import create_app,db
from flask_migrate import Migrate
import os
from livereload import Server

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        try:
            print(app.config['SQLALCHEMY_DATABASE_URI'])
            db.create_all()
        except Exception:
            print(Exception)
    server = Server(app.wsgi_app)
    server.watch(os.path.join(os.path.dirname(__file__), '..', 'html'))
    server.watch(os.path.join(os.path.dirname(__file__), '..', 'static'))

    server.serve(host="0.0.0.0", port=5500)

