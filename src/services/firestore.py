import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os


class Firestore:

    class __Firestore:
        def __init__(self):
            cred = credentials.Certificate(os.getcwd() + '/src/config/credentials/service-account.json')
            firebase_admin.initialize_app(cred)
            self._db = firestore.client()

        def insert_stock(self, account_type, email, stock):
            doc_ref = self._db.collection('stocks').document(email)
            doc_dict = doc_ref.get().to_dict()
            if stock not in doc_dict[account_type]:
                doc_dict[account_type].append(stock)
            doc_ref.set(doc_dict)
            return 'ok'

        def get_user_stocks(self, email):
            user_stocks = self._db.collection(u'stocks').document(email).get()
            return user_stocks.to_dict() if user_stocks.to_dict() else {'pea': [], 'titres': []}

        def delete_stock(self, account, email, symbol):
            doc_ref = self._db.collection('stocks').document(email)
            doc_dict = doc_ref.get().to_dict()
            for idx, stock in enumerate(doc_dict[account]):
                if stock['symbol'] == symbol:
                    del doc_dict[account][idx]
                    break
            doc_ref.set(doc_dict)
            return "ok"

    instance = None

    def __init__(self):
        if not Firestore.instance:
            Firestore.instance = Firestore.__Firestore()

    def __getattr__(self, name):
        return getattr(self.instance, name)
