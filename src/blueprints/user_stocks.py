from flask import Blueprint, request, jsonify
from ..services import Firestore

stocks_users = Blueprint('stocks_user', __name__)


@stocks_users.route('/<account_type>/<email>', methods=['POST'])
def insert(account_type, email):
    fs_service = Firestore()
    stocks = request.get_json()
    fs_service.insert_stock(account_type, email, stocks)
    return {'message': 'ok'}, 200


@stocks_users.route('/<email>')
def get_all(email):
    fs_service = Firestore()
    return jsonify({'stocks': fs_service.get_user_stocks(email)}), 200
