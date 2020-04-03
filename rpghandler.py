import hangups
from hangups import hangouts_pb2
from hangups.hangouts_pb2 import ParticipantId

import asyncio
from text_2048 import run_game
import random
from collections import defaultdict
from datetime import datetime, tzinfo
import json
import math
import sys

from utils import *


class Handler:
    def __init__(self):
        self.keywords = {
            "good bot": "nyaa, thanku~~",
            "bad bot": "nuu dun pweese~~ >.<",
            "headpat": "uwu thanku",
            "yamete": "kudasai!~~",
            "ping": "pong",
            "pong": "ping",
            "saber": "hi",
            "yes": "no",
            "no": "yes"
        }
        self.commands = {
            "/help": self.help,
            "/rename": self.rename,
            "/say": self.say,
            "/quit": self.quit,
            "/reset": self.reset,
            "/id": self.id,
            "/2048": self.play_2048,
            "/remove": self.remove,
            "/sync": self.sync,
            "/save_data": self.save_data,
            "/set": self.set,
            "/register": self.register,
            "/inv": self.inv,
            "/warp": self.warp,
            "/equipped": self.equipped,
            "/stats": self.stats,
            "/rest": self.rest,
            "/fight": self.fight,
            "/atk": self.atk
        }
        self.images = {
            "/gay": "images/gay.jpg",
            "/math": "images/math.jpg",
            "/praise": "images/praise.jpg",
            "/goddammit": "images/goddammit.jpg",
            "/heymister": "images/heymister.png"
        }

        self.cooldowns = defaultdict(dict)
        self.admins = [
            114207595761187114730,  # joseph
            106637925595968853122,  # chendi
            ]
        self.ignore = [
                105849946242372037157,
                11470746254329358783, # saberbot
                104687919952293193271 # chendibot
                ]

        with open("data.json") as f:
            self.data = json.load(f)

        self.userData = self.data["users"]

        random.seed(datetime.now())

    # utility
    async def help(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        f = open("text/help.txt", 'r')
        contents = f.read()
        await conv.send_message(toSeg(contents))
        f.close()

    async def rename(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.rename(event.text.split(' ', 1)[1])
        except Exception as e:
            await conv.send_message(toSeg("Format: /rename {name}"))

    async def say(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.send_message(toSeg(event.text.split(' ', 1)[1]))
        except Exception as e:
            await conv.send_message(toSeg("Format: /say {message}"))

    async def id(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            await conv.send_message(toSeg(user.id_[0]))
        except Exception as e:
            await conv.send_message(toSeg(str("Something went wrong!")))

    # rpg 
    async def register(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if cooldown(self.cooldowns, user, event, 5):
            return

        if userID in self.userData:
            await conv.send_message(toSeg("You are already registered!"))
            return

        try:
            self.userData[userID] = user
            self.userData[userID] = {}
            self.userData[userID]["balance"] = 0
            self.userData[userID]["name"] = user.full_name
            self.userData[userID]["lifetime_balance"] = 0
            self.userData[userID]["vit"] = 100
            self.userData[userID]["hp"] = 100
            self.userData[userID]["atk"] = 5
            self.userData[userID]["def"] = 5
            self.userData[userID]["xp"] = 0
            self.userData[userID]["lvl"] = 1
            self.userData[userID]["room"] = "village" 
            self.userData[userID]["equipped_armor"] = 0
            self.userData[userID]["equipped_weapon"] = 1
            self.userData[userID]["inventory_size"] = 8
            self.userData[userID]["fighting"] = {}
            self.userData[userID]["inventory"] = [
                                        {"name": "Starter Armor", "type": "armor", "rarity": "common", "modifier": "boring"},
                                        {"name": "Starter Weapon", "type": "weapon", "rarity": "common", "modifier": "boring"}
                                    ]

            save("data.json", self.data)

            await conv.send_message(toSeg("Successfully registered!"))
        except Exception as e:
            await conv.send_message(toSeg("Failed to register!"))
            await conv.send_message(toSeg(str(e)))
            print(e)

    async def inv(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        inv = ""

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))
            return

        for item in self.userData[userID]["inventory"]:
            inv += item["rarity"] + " " + item["modifier"] + " " + item["name"] + '\n'
            inv = inv.title()

        await conv.send_message(toSeg(inv))

    async def warp(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        inv = ""
        text = event.text.lower()
        rooms = self.data["rooms"]
        users = self.userData

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))

        elif len(text.split()) != 2:
            await conv.send_message(toSeg("Invalid arguments! /warp {room}"))

        elif self.userData[userID]["fighting"]:
            await conv.send_message(toSeg("You can't warp while in a fight!"))

        elif text.split()[1] not in rooms:
            await conv.send_message(toSeg("That room doesn't exist!"))

        elif rooms[text.split()[1]]["required_lvl"] > users[userID]["lvl"]:
            await conv.send_message(toSeg("Your level is not high enough to warp there!"))

        elif text.split()[1] == users[userID]["room"]:
            await conv.send_message(toSeg("You are already in that room!"))

        else:
            users[userID]["room"] = text.split()[1]
            save("data.json", self.data)
            await conv.send_message(toSeg("Successfully warped!"))

    async def equipped(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        equipped = ""

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))
            return

        userInfo = self.userData[userID]
        userArmor = userInfo["inventory"][userInfo["equipped_armor"]]
        userWeapon = userInfo["inventory"][userInfo["equipped_weapon"]]

        equipped += "Weapon: " + (userWeapon["rarity"] + " " + userWeapon["modifier"] + " " + userWeapon["name"]).title() + '\n'
        equipped += "Armor: " + (userArmor["rarity"] + " " + userArmor["modifier"] + " " + userArmor["name"]).title()

        await conv.send_message(toSeg(equipped))

    async def fight(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        rooms = self.data["rooms"]

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))

        playerRoom = self.userData[userID]["room"]

        if playerRoom == "village":
            await conv.send_message(toSeg("Don't fight in the village..."))

        elif self.userData[userID]["fighting"]:
            await conv.send_message(toSeg("You are already fighting " + self.userData[userID]["fighting"]["name"] + "!"))

        else:
            enemy = random.choice(rooms[playerRoom]["enemies"])
            enemyData = self.data["enemies"][enemy]
            await conv.send_message(toSeg(enemy + " has approached to fight!"))
            await conv.send_message(toSeg("Vit: " + str(enemyData["vit"]) + "\nAtk: " + str(enemyData["atk"]) + "\nDef: " + str(enemyData["def"])))

            self.userData[userID]["fighting"]["name"] = enemy
            self.userData[userID]["fighting"]["hp"] = enemyData["vit"]
            save("data.json", self.data)

    async def atk(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        rooms = self.data["rooms"]

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))

        elif not self.userData[userID]["fighting"]:
            await conv.send_message(toSeg("You need to be in a fight!"))

        else:
            enemy = self.userData[userID]["fighting"]

            userWeapon = self.userData[userID]["inventory"][self.userData[userID]["equipped_weapon"]]
            baseDamage = self.data["items"]["weapons"][userWeapon["rarity"]][userWeapon["name"]]["atk"] 
            modifierDamage = self.data["modifiers"][userWeapon["modifier"]]["atk"]

            damage_dealt = (baseDamage + baseDamage * modifierDamage) * (self.userData[userID]["atk"]/self.data["enemies"][enemy["name"]]["def"])

            if random.randint(0, 1):
                damage_dealt += math.sqrt(damage_dealt/2)
            else:
                damage_dealt -= math.sqrt(damage_dealt/2)

            damage_dealt = round(damage_dealt, 1)

            enemy["hp"] -= damage_dealt
            enemy["hp"] = round(enemy["hp"], 1)

            await conv.send_message(toSeg("You dealt " + str(damage_dealt) + " damage to " + enemy["name"] + "!"))
            if enemy["hp"] <= 0:
                await conv.send_message(toSeg(enemy["name"] + " is now dead!"))

                xp_range = self.data["rooms"][self.userData[userID]["room"]]["xp_range"]
                xp_earned = random.randint(xp_range[0], xp_range[1])
                # gold_range = self.data["rooms"][self.userData[userID]["room"]]["gold_range"]
                # gold_earned = random.randint(gold_range[0], gold_range[1])

                gold_earned = round(self.data["enemies"][enemy["name"]]["vit"]/10) + random.randint(1, 10)

                await conv.send_message(toSeg("You earned " + str(xp_earned) + " xp and " + str(gold_earned) + " gold!"))
                await self.give_xp(conv, userID, xp_earned)

                self.userData[userID]["balance"] += gold_earned
                self.userData[userID]["lifetime_balance"] += gold_earned

                self.userData[userID]["fighting"] = {}
                save("data.json", self.data)
                return

            userArmor = self.userData[userID]["inventory"][self.userData[userID]["equipped_armor"]]
            baseDefense = self.data["items"]["armor"][userArmor["rarity"]][userArmor["name"]]["def"]
            modifierDefense = self.data["modifiers"][userArmor["modifier"]]["def"]

            damage_taken = self.data["enemies"][enemy["name"]]["atk"]/(baseDefense + baseDefense * modifierDefense)

            if random.randint(0, 1):
                damage_taken += math.sqrt(damage_taken/2)
            else:
                damage_taken -= math.sqrt(damage_taken/2)

            damage_taken = round(damage_taken, 1)

            self.userData[userID]["hp"] -= damage_taken

            await conv.send_message(toSeg(enemy["name"] + " dealt " + str(damage_taken) + " to you!"))
            await conv.send_message(toSeg("You have " + str(self.userData[userID]["hp"]) + " hp left and " + enemy["name"] + " has " + str(enemy["hp"]) + "!"))

            save("data.json", self.data)
            if self.userData[userID]["hp"] <= 0:
                await conv.send_message(toSeg("You were killed by " + enemy["name"] + "..."))
                self.userData[userID]["fighting"] = {}
                self.userData[userID]["hp"] = self.userData[userID]["vit"]
                save("data.json", self.data)
                return

    async def rest(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]
        text = ""

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))

        elif self.userData[userID]["room"] != "village":
            await conv.send_message(toSeg("You have to rest in the village!"))

        else:
            self.userData[userID]["hp"] = self.userData[userID]["vit"]
            text += "You feel well rested...\n"
            text += "Your health is back up to " + str(self.userData[userID]["vit"]) + "!"
            await conv.send_message(toSeg(text))


    async def stats(self, bot, event):
        user, conv = getUserConv(bot, event)
        userID = user.id_[0]

        if userID not in self.userData:
            await conv.send_message(toSeg("You are not registered!"))

        userStats = self.userData[userID]
        await conv.send_message(toSeg("HP: " + str(userStats["hp"]) + "\nVIT: " + str(userStats["vit"]) + "\nATK: " + str(userStats["atk"]) + "\nDEF: " + str(userStats["def"])))

    # chendi's stuff
    async def play_2048(self, bot, event):
        user, conv = getUserConv(bot, event)
        game_text = run_game(event.text)
        await conv.send_message(toSeg(game_text))
        save_games()

    async def yes_no(self, bot, event):
        user, conv = getUserConv(bot, event)
        text = event.text
        if isIn(self.admins, user):
            text = "yes" if text == "yes" else "no"
        else:
            text = "no" if text == "yes" else "yes"
        await conv.send_message(toSeg(text))

    async def say_something(self, bot, event):
        pass

    # admin 
    async def quit(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 30):
            return

        try:
            if isIn(self.admins, user):
                await conv.send_message(toSeg("Saber out!"))
                await bot.client.disconnect()
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            await conv.send_message(toSeg(str(e)))

    async def reset(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            arg1 = '/' + event.text.lower().split()[1]
            if isIn(self.admins, user):
                if arg1 in self.cooldowns[user]:
                    self.cooldowns[user][arg1] = datetime.min.replace(tzinfo=None)
                else:
                    await conv.send_message(toSeg("Format: /reset {command}"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except Exception as e:
            await conv.send_message(toSeg("Format: /reset {command}"))
            await conv.send_message(toSeg(str(e)))

    async def save_data(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            if isIn(self.admins, user):
                save("data.json", self.data)

                await conv.send_message(toSeg("Successfully saved!"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            await conv.send_message(toSeg(str(e)))

    async def sync(self, bot, event):
        user, conv = getUserConv(bot, event)
        key = event.text.lower().split()[1]
        value = event.text.split(' ', 2)[2]

        if value.isdigit():
            value = int(value)

        try:
            if isIn(self.admins, user):
                for user in self.userData:
                    self.userData[user][key] = value

                save("data.json", self.data)

                await conv.send_message(toSeg("Synced all values!"))
                return
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        
        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            await conv.send_message(toSeg(str(e)))
            print(e)

    async def remove(self, bot, event):
        user, conv = getUserConv(bot, event)
        key = event.text.lower().split()[1]

        try:
            if isIn(self.admins, user):
                for user in self.userData:
                    self.userData[user].pop(key, None)

                save("data.json", self.data)

                await conv.send_message(toSeg("Removed key!"))
                return
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))

        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            await conv.send_message(toSeg(str(e)))
            print(e)

    async def set(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            userID = event.text.split()[1]
            key = event.text.lower().split()[2]
            value = event.text.split(' ', 3)[3]

            if value.isdigit():
                value = int(value)

            if isIn(self.admins, user):
                if userID in self.userData:
                    self.userData[userID][key] = value

                    save("data.json", self.data)

                    await conv.send_message(toSeg("Set value!"))
                    return
                else:
                    await conv.send_message(toSeg("That user isn't registered!"))
                    return

            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))

        except Exception as e:
            await conv.send_message(toSeg("Format: /set {userID} {key} {value}"))
            print(e)

    # not commands but also doesn't fit in utils
    async def give_xp(self, conv, userID, xp_earned):
        notify_level = 0
        self.userData[userID]["xp"] += xp_earned

        while True:
            next_lvl = self.userData[userID]["lvl"] + 1
            xp_required = round(4 * ((next_lvl ** 4)/5))
            
            if self.userData[userID]["xp"] >= xp_required:
                self.userData[userID]["lvl"] += 1
                self.userData[userID]["xp"] -= xp_required
                notify_level = 1
            
            else:
                break

        if notify_level:
            await conv.send_message(toSeg("You are now level " + str(self.userData[userID]["lvl"]) + "!"))

        save("data.json", self.data)
