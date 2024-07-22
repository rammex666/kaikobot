from pymongo import MongoClient

client = MongoClient("mongodb+srv://rammex:C3gP2ZCYfobrCLr1@kaikodb.92gz2dv.mongodb.net/")

db = client["kaikodb"]

player_db = db["players"]

inventory_db = db["inventory"]

equipment_db = db["equipment"]


def get_equipmentdb():
    return equipment_db


def get_inventorydb():
    return inventory_db


def get_playerdb():
    return player_db
