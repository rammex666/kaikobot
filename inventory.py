from db_utils import get_equipmentdb, get_inventorydb, get_playerdb
import random
from items import *


def add_item_to_inventory(owner_id, name, quantity, quality, level, xp, type, damage, durability, description, rarity):
    inventorydb = get_inventorydb()
    item = {"owner_id": owner_id, "name": name, "quantity": quantity, "quality": quality, "level": level, "xp": xp,
            "type": type, "damage": damage, "durability": durability, "description": description, "rarity": rarity}
    inventorydb.insert_one(item)


def get_items_by_owner(owner_id):
    inventorydb = get_inventorydb()
    return list(inventorydb.find({"owner_id": owner_id}))


def generate_item(owner_id):
    player = get_playerdb().find_one({"_id": owner_id})
    level = player["level"]
    itemgenerate = random.randint(1, 100)
    if itemgenerate > 93:
        if level <= 5:
            items = getitemlv5()
        elif level <= 10:
            items = getitemlv10()
        elif level <= 20:
            items = getitemlv20()
        elif level >= 90:
            items = getitemlv90()
        new_item = random.choice(items)
        new_item["owner_id"] = owner_id
        same_type_items = [item for item in get_items_by_owner(owner_id) if
                           item['type'] == new_item['type']]
        if len(same_type_items) == 25:
            return {"status": "invfull", "item": new_item}
        add_item_to_inventory(**new_item)

        return {"status": "success", "item": new_item}
    else:
        return {"status": "failed"}


def equip_item(player_id, item_id, item_type):
    inventorydb = get_inventorydb()
    equipmentdb = get_equipmentdb()
    item = inventorydb.find_one({"owner_id": player_id, "_id": item_id})
    if item is not None:
        equipmentdb.update_one({"_id": player_id}, {"$set": {item_type: item_id}}, upsert=True)


def get_equipped_items(player_id):
    equipmentdb = get_equipmentdb()
    player_equipment = equipmentdb.find_one({"_id": player_id})
    if player_equipment is not None:
        return player_equipment
    else:
        return None
