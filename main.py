from flask import Flask, jsonify
from flask_cors import CORS
from src.blueprints import finance, stocks_users

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
app.register_blueprint(finance, url_prefix="/api/finance")
app.register_blueprint(stocks_users, url_prefix="/api/stock_users")


@app.route('/_ah/warmup')
def warmup():
    return jsonify({'message': 'ok'}), 200


if __name__ == '__main__':
    app.run()
