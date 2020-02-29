from flask import Blueprint, request, jsonify
from ..services import Firestore

stocks_users_blueprint = Blueprint('stocks_user', __name__)


@stocks_users_blueprint.route('/<account_type>/<email>', methods=['POST'])
def insert(account_type, email):
    fs_service = Firestore()
    stocks = request.get_json()
    fs_service.insert_stock(account_type, email, stocks)
    return {'message': 'ok'}, 200


@stocks_users_blueprint.route('/<email>')
def get_all(email):
    fs_service = Firestore()
    return jsonify({'stocks': fs_service.get_user_stocks(email)}), 200


@stocks_users_blueprint.route('/<account_type>/<email>/<symbol>', methods=['DELETE'])
def delete(account_type, email, symbol):
    fs_service = Firestore()
    fs_service.delete_stock(account_type, email, symbol)
    return {'message': 'ok'}, 200
