from flask import Flask, jsonify
from flask_cors import CORS
from src.blueprints import finance, stocks_users, lesechos_news

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
app.register_blueprint(finance, url_prefix="/api/finance")
app.register_blueprint(stocks_users, url_prefix="/api/stock_users")
app.register_blueprint(lesechos_news, url_prefix="/api/news")


@app.route('/_ah/warmup')
def warmup():
    return jsonify({'message': 'ok'}), 200


if __name__ == '__main__':
    app.run()
