"""
manager for economy
"""
import economy.classes as classes
import utils


class EconomyManager():
    """manager for economy"""

    save_file = "the_bot/economy/save_data.json"

    def __init__(self):
        self.users = classes.users
        self.load_game()
        self.commands = {
            "leaderboard": self.leaderboard,
            "shop": self.shop,
            "give": self.give,
            "profile": self.profile
        }

    def run_game(self, userID, commands):
        """runs the game"""
        command = next(commands)
        output_text = ""
        if command == "help":
            return "help text"
        if command == "register":
            return self.register(userID, commands)
        elif userID not in self.users.keys():
            return "You are not registered! Use register"

        user = self.users[userID]
        if command not in ("prestige", "prestige_upgrade"):
            user.confirmed_prestige = False
            user.confirmed_upgrade = False
        if command in self.commands:
            function_ = self.commands[command]
            output_text = function_(user, commands)
        elif command in classes.EconomyUser.commands:
            function_ = classes.EconomyUser.commands[command]
            output_text = function_(user, commands)
        else:
            output_text = "Invalid command"

        return output_text

    def leaderboard(self, playing_user, commands):
        """returns leaderboard"""
        user_balances = {user: user.lifetime_balance for user in self.users.values()}
        leaderboard_text = "Ranking by balance earned in this lifetime:\n"

        sorted_users = [user for user in sorted(list(user_balances.items()), key=lambda x: x[1], reverse=True)]
        print(sorted_users)

        for rank in range(5):
            user_balance = utils.get_item_safe(sorted_users, (rank, ))
            if user_balance:
                user, balance = user_balance
                leaderboard_text += f"{rank + 1}. {user.name}: {balance}\n"
        playing_user_rank = sorted_users.index((playing_user, playing_user.lifetime_balance))
        if playing_user_rank > 5:
            leaderboard_text += f"\n{playing_user_rank + 1}. {playing_user.name}(you): {playing_user.lifetime_balance}\n"

        return leaderboard_text

    def shop(self, user, commands):
        """returns shop"""
        shop_list = []
        for type_name, items in classes.shop_items.items():
            items_text = [type_name]
            player_item = user.items[type_name]
            if player_item == len(items):
                items_text = f"You already have the highest level {type_name}"
            else:
                for i in range(player_item + 1, len(items)):
                    item = items[i]
                    items_text.append(utils.description(item.name().title(), f"{item.price} saber dollars"))
            shop_list.append(items_text)

        return utils.join_items(*shop_list, is_description=True, description_mode="long")

    def save_game(self):
        """saves the game"""
        data = {userID: player.__dict__ for userID, player in self.users.items()}
        utils.save(self.save_file, data)

    def load_game(self):
        """loads the game"""
        data = utils.load(self.save_file)
        for userID, user_data in data.items():
            self.users[int(userID)] = classes.EconomyUser(
                name=user_data["name"],
                balance=user_data["balance"],
                lifetime_balance=user_data["lifetime_balance"],
                prestige=user_data["prestige"],
                items=user_data["items"],
            )

    def register(self, userID, commands):
        """registers a user"""
        name = next(commands)
        if userID in self.users:
            return "You are already registered!"
        if not name:
            return "you must provide a name"
        self.users[userID] = classes.EconomyUser(name)
        return "Successfully registered!"

    def give(self, giving_user, commands):
        """gives money to another user"""
        reciveing_user = next(commands)
        money = next(commands)
        output_text = ""

        if not reciveing_user:
            output_text += "You must specfiy a user or ID"
        elif not money:
            output_text += "You must specify an amount"
        elif not money.isdigit():
            output_text += "You must give an integer amount of Saber Dollars"
        else:
            money = int(money)

            for user in self.users.values():
                if reciveing_user == user.name:
                    reciveing_user = user
                    break

            if reciveing_user.isdigit() and int(reciveing_user) in self.users:
                reciveing_user = self.users[int(reciveing_user)]
            if reciveing_user.id() not in self.users:
                output_text += "That user has not registered!"
            elif reciveing_user.id() == giving_user.id():
                output_text += "That user is you!"
            else:
                if money < 0:
                    output_text += "You can't give negative money!"
                elif giving_user.balance < money:
                    output_text += "You don't have enough money to do that!"
                else:
                    giving_user.change_balance(- money)
                    reciveing_user.change_balance(money)

                    output_text += utils.join_items(
                        f"Successfully given {money} Saber Dollars to {reciveing_user.name}.",
                        f"That user now has {reciveing_user.balance} Saber Dollars."
                    )
        return output_text

    def profile(self, user, commands):
        """returns user profiles"""
        output_text = ""
        user_name = next(commands)
        possible_users = []

        for possible_user in self.users.values():
            if user_name in possible_user.name:
                possible_users.append(possible_user)
        if user_name.isdigit() and int(user_name) in self.users:
            possible_users.append(self.users[int(user_name)])
        elif user_name == "self":
            possible_users.append(user)
        if not possible_users:
            output_text += "No users go by that name!"

        elif len(possible_users) > 1:
            output_text += f"{len(possible_users)} user(s) go by that name:\n"

        for user in possible_users:
            output_text += user.profile()
        return utils.newline(output_text)
