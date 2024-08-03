from pymongo import MongoClient

client = MongoClient("")

db = client["kaikodb"]

player_db = db["players"]

inventory_db = db["inventory"]

equipment_db = db["equipment"]

shop_db = db["shop"]


def get_equipmentdb():
    return equipment_db


def get_inventorydb():
    return inventory_db


def get_playerdb():
    return player_db

def get_shopdb():
    return shop_db
