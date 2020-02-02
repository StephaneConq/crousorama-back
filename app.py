from flask import Flask
from flask_cors import CORS
from src.blueprints import finance

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
app.register_blueprint(finance, url_prefix="/api/finance")


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
