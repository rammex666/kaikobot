box_types = {
    "Common Box": {
        "cost": 50,
        "items": [
            {"name": "Common Sword", "quantity": 1, "quality": "F", "level": 1, "xp": 0, "type": "primary",
             "damage": 10, "durability": 100, "description": "A common Sword.", "rarity": "common"},
            {"name": "Common Shield", "quantity": 1, "quality": "F", "level": 1, "xp": 0, "type": "secondary",
             "damage": 0, "durability": 100, "description": "A common Shield.", "rarity": "common"}
        ]
    },
    "Rare Box": {
        "cost": 500,
        "items": [
            {"name": "Rare Helmet", "quantity": 1, "quality": "D", "level": 5, "xp": 0, "type": "helmet", "damage": 0,
             "durability": 500, "description": "A rare Helmet.", "rarity": "rare"},
            {"name": "Rare Chestplate", "quantity": 1, "quality": "D", "level": 5, "xp": 0, "type": "chestplate",
             "damage": 0, "durability": 500, "description": "A rare Chestplate.", "rarity": "rare"}
        ]
    },
    "Legendary Box": {
        "cost": 4000,
        "items": [
            {"name": "Legendary Sword", "quantity": 1, "quality": "S", "level": 100, "xp": 0, "type": "primary",
             "damage": 100, "durability": 1000, "description": "A legendary sword made by the creator.",
             "rarity": "legendary"},
            {"name": "Legendary Shield", "quantity": 1, "quality": "S", "level": 100, "xp": 0, "type": "secondary",
             "damage": 0, "durability": 1500, "description": "A legendary shield made by the creator.",
             "rarity": "legendary"}
        ]
    }
}


def get_box():
    return box_types
