from flask import Flask, render_template
from dotenv import load_dotenv
import os
from livereload import Server

load_dotenv()

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'html'), instance_relative_config=True)

@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    app.debug = True

    server = Server(app.wsgi_app)

    server.watch(os.path.join(os.path.dirname(__file__), '..', 'html'))

    server.serve()
