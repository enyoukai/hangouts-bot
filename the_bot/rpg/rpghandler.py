import random
from collections import defaultdict
from datetime import datetime
import json  # u shouldn't need this cause its in utils.py
import math
from utils import *
from the_bot.rpg.rpg_classes import *


class RPGHandler:

    save_file = "the_bot/data.json"
    admins = (
        114207595761187114730,  # joseph
        106637925595968853122,  # chendi
    )

    users = {

    }

    def __init__(self):
        self.commands = {
            "remove": self.remove,
            "sync": self.sync,
            "save_data": self.save_data,
            "set": self.set,
            "register": self.register,
            "inventory": self.inventory,
            "warp": self.warp,
            "equipped": self.equipped,
            "stats": self.stats,
            "rest": self.rest,
            "xp": self.xp,
            "fight": self.fight,
            "atk": self.atk,
            "heal": self.heal
        }
        self.admin_commands = {

        }

        

        self.cooldowns = defaultdict(dict)

        self.data = utils.load(self.save_file)
        self.userData = self.data["users"]

        random.seed(datetime.now())

    # rpg
    def rpg_process(self, userID, event_text):
        commands = clean(event_text)
        commands = trim(commands)
        command = get_item_safe[commands]
        if not command:
            # u might want to replace this with basic help text
            # or the curent state of the game, incase they forgot
            # eg. "u r in the village, enter help for help"
            return "you must enter a command"

        elif command not in self.commands:
            return "That command doesn't exist!"

        elif command != "register" and userID not in self.userData:
            return "You are not registered! Use register"
        user = self.users[userID]
        commands = trim(commands)
        return self.commands[command](user, commands)
        save(self.save_file, self.data)

    def register(self, user, command):
        userID = get_key(self.users, user)
        if userID in self.users:
            return "You are already registered!"
        self.users[userID] = User("placeholder name")

        save(self.save_file, self.data)
        return "Successfully registered!"

    def inventory(self, userID, command):
        inventory_text = ""

        for item in self.userData[userID]["inventory"]:
            inventory_text += item.description()

        return inventory_text

    def warp(self, userID, command):
        inv = ""
        rooms = self.data["rooms"]
        users = self.userData
        room = get_item_safe(commands)
        if not room:
            return "Invalid argument! use warp {room}"

        if self.userData[userID]["fighting"]:
            return "You can't warp while in a fight!"

        elif room not in rooms:
            return "That room doesn't exist!"

        elif rooms[room]["required_lvl"] > users[userID]["lvl"]:
            return "Your level is not high enough to warp there!"

        elif room == users[userID]["room"]:
            return "You are already in that room!"

        users[userID]["room"] = room
        save(self.save_file, self.data)
        return "Successfully warped!"


    def equipped(self, userID, command):
        equipped = ""
        userInfo = self.userData[userID]

        for type_, index in userInfo["equipped"].items():
            item = userInfo["inventory"][index]
            equipped += f"{type_}: {item.description()}"

        return equipped.title()

    def xp(self, userID, command):
        return f"LVL: {self.userData[userID]['lvl']} | {self.userData[userID]['xp']}/{round(4 * (((self.userData[userID]['lvl'] + 1)** 4)/5))}"


    def fight(self, userID, command):
        rooms = self.data["rooms"]
        text = ""

        playerRoom = self.userData[userID]["room"]

        # DO NOT let an if elif chain happen here
        if playerRoom == "village":
            return "Don't fight in the village..."

        elif self.userData[userID]["fighting"]:
            return f"You are already fighting {self.userData[userID]['fighting']['name']}!"

        else:
            enemy = random.choice(rooms[playerRoom]["enemies"])
            enemyData = self.data["enemies"][enemy]

            text += f"{enemy} has approached to fight!\n"
            text += f"Vit: {enemyData['vit']}\nAtk: {enemyData['atk']}\nDef: {enemyData['def']}"

            self.userData[userID]["fighting"]["name"] = enemy
            self.userData[userID]["fighting"]["hp"] = enemyData["vit"]

            save(self.save_file, self.data)
            return text

    def atk(self, userID, command):
        rooms = self.data["rooms"]
        text = ""

        if not self.userData[userID]["fighting"]:
            return "You need to be in a fight!"

        else:
            enemy = self.userData[userID]["fighting"]

            userWeapon = self.userData[userID]["inventory"][self.userData[userID]["equipped_weapon"]]
            baseDamage = self.data["items"]["weapons"][userWeapon["rarity"]][userWeapon["name"]]["atk"]
            modifierDamage = self.data["modifiers"][userWeapon["modifier"]]["atk"]

            damage_dealt = (baseDamage + baseDamage * modifierDamage) * (self.userData[userID]["atk"] / self.data["enemies"][enemy["name"]]["def"])

            multiplier = random.choice((1, -1))
            damage_dealt += multiplier * math.sqrt(damage_dealt / 2)

            damage_dealt = round(damage_dealt, 1)

            enemy["hp"] -= damage_dealt
            enemy["hp"] = round(enemy["hp"], 1)

            text += "You dealt " + str(damage_dealt) + " damage to " + enemy["name"] + "!\n"

            if enemy["hp"] <= 0:
                text += enemy["name"] + " is now dead!\n"

                xp_range = self.data["rooms"][self.userData[userID]["room"]]["xp_range"]
                xp_earned = random.randint(xp_range[0], xp_range[1])
                # gold_range = self.data["rooms"][self.userData[userID]["room"]]["gold_range"]
                # gold_earned = random.randint(gold_range[0], gold_range[1])

                gold_earned = round(self.data["enemies"][enemy["name"]]["vit"] / 10) + random.randint(1, 10)

                text += "You earned " + str(xp_earned) + " xp and " + str(gold_earned) + " gold!"
                text += self.give_xp(userID, xp_earned)

                self.userData[userID]["balance"] += gold_earned
                self.userData[userID]["lifetime_balance"] += gold_earned

                self.userData[userID]["fighting"] = {}
                save(self.save_file, self.data)
                return text

            userArmor = self.userData[userID]["inventory"][self.userData[userID]["equipped_armor"]]
            baseDefense = self.data["items"]["armor"][userArmor["rarity"]][userArmor["name"]]["def"]
            modifierDefense = self.data["modifiers"][userArmor["modifier"]]["def"]

            damage_taken = self.data["enemies"][enemy["name"]]["atk"] / (baseDefense + baseDefense * modifierDefense)

            multiplier = random.choice((1, -1))
            damage_taken += multiplier * math.sqrt(damage_taken / 2)

            damage_taken = round(damage_taken, 1)

            self.userData[userID]["hp"] -= damage_taken
            self.userData[userID]["hp"] = round(self.userData[userID]["hp"], 1)

            text += enemy["name"] + " dealt " + str(damage_taken) + " to you!\n"
            text += "You have " + str(self.userData[userID]["hp"]) + " hp left and " + enemy["name"] + " has " + str(enemy["hp"]) + "!"

            save(self.save_file, self.data)
            if self.userData[userID]["hp"] <= 0:
                text += "\nYou were killed by " + enemy["name"] + "..."

                self.userData[userID]["fighting"] = {}
                self.userData[userID]["hp"] = self.userData[userID]["vit"]

            return text
            save(self.save_file, self.data)

    def rest(self, userID, command):
        text = ""

        if self.userData[userID]["room"] != "village":
            return "You have to rest in the village!"

        else:
            self.userData[userID]["hp"] = self.userData[userID]["vit"]
            text += "You feel well rested...\n"
            text += f"Your health is back up to {self.userData[userID]['vit']}!"
            save(self.save_file, self.data)
            return text

    def stats(self, userID, command):
        userStats = self.userData[userID]
        return f"HP: {userStats['hp']}\nVIT: {userStats['vit']}\nATK: {userStats['atk']}\nDEF: {userStats['def']}\nMP: {userStats['mp']}"

    def save_data(self, userID, command):
        if userIn(self.admins, user):
            save(self.save_file, self.data)

            return "Successfully saved!"
        else:
            return "bro wtf u can't use that"

    def sync(self, userID, command):
        key = command.split()[1]
        value = command.split()[2]

        if value.isdigit():
            value = int(value)

        if userIn(self.admins, user):
            for user in self.userData:
                self.userData[user][key] = value

            save(self.save_file, self.data)

            return "Synced all values!"
        else:
            return "bro wtf u can't use that"

    def remove(self, userID, command):
        key = command.split()[1]

        if userIn(self.admins, user):
            for user in self.userData:
                self.userData[user].pop(key, None)

            save(self.save_file, self.data)

            return "Removed key!"
        else:
            return "bro wtf u can't use that"

    def set(self, userID, commands):
        # i rewrote this, check improvement_examples.py
        command_list = utils.clean(commands)
        userID, key, value = get_item_safe(command_list, (1, 2, 3))

        if value.isdigit():
            value = int(value)

        if userIn(self.admins, user):
            if userID in self.userData:
                self.userData[userID][key] = value

                save(self.save_file, self.data)

                return "Set value!"
            else:
                return "That user isn't registered!"

        else:
            return "bro wtf u can't use that"

    # not commands but also doesn't fit in utils
    def give_xp(self, userID, xp_earned):
        notify_level = 0
        self.userData[userID]["xp"] += xp_earned

        while True:
            next_lvl = self.userData[userID]["lvl"] + 1
            xp_required = round(4 * ((next_lvl ** 4) / 5))

            if self.userData[userID]["xp"] >= xp_required:
                self.userData[userID]["lvl"] += 1
                self.userData[userID]["xp"] -= xp_required
                notify_level = 1

            else:
                break

        if notify_level:
            return "You are now level " + str(self.userData[userID]["lvl"]) + "!"

        else:
            return ""

        save(self.save_file, self.data)
