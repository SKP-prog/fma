from pymongo import MongoClient


def update_db(rows):
    client = MongoClient("localhost", 27017)
    db = client['HLJ']
    table = db['Main']
    table.insert_many(rows)


def get_db():
    client = MongoClient("localhost", 27017)
    db = client['HLJ']
    table = db["Main"]
    return table.find({})
