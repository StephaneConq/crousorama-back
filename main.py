from flask import Flask, jsonify
from flask_cors import CORS
from src.blueprints import finance_blueprint, stocks_users_blueprint, news_blueprint, calendar_blueprint

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
app.register_blueprint(finance_blueprint, url_prefix="/api/finance")
app.register_blueprint(stocks_users_blueprint, url_prefix="/api/stock_users")
app.register_blueprint(news_blueprint, url_prefix="/api/news")
app.register_blueprint(calendar_blueprint, url_prefix="/api/agenda")


@app.route('/_ah/warmup')
def warmup():
    return jsonify({'message': 'ok'}), 200


if __name__ == '__main__':
    app.run()
