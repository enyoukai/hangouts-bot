"""
manager for 2048 games
"""
import utils
from game_2048.classes import Game, games


class Manager2048:
    """manager for 2048 game"""
    save_file = "the_bot/game_2048/save_data.json"
    game_management_commands = [
        "create {game_name}", "{game_name}", "rename {old_name} {new_name}", "delete {game_name}", "games",
    ]
    reserved_words = (
        Game.game_commands + list(Game.modes.keys()) +
        [value for values in list(Game.movement.values()) for value in values] +
        game_management_commands +
        ["2048", "/2048", "current game"]
    )
    help_texts = {
        "help": "",  # avoids probelems with referencing itself
        "gamemodes": utils.join_items(
            *[(mode_name, mode.description) for mode_name, mode in Game.modes.items()],
            is_description=True
        ),
        "move": utils.join_items(
            *[[direction] + list(commands) for direction, commands in Game.movement.items()],
            is_description=True
        ),
        "scores": utils.join_items(
            *[(mode_name, mode.high_score) for mode_name, mode in Game.modes.items()],
            is_description=True
        ),
        "reserved": utils.description("reserved", *reserved_words)
    }
    help_texts["help"] = utils.join_items(
        ("in-game commands", *list(Game.game_commands)),
        ("game management", *game_management_commands),
        ("informational", *list(help_texts)),
        is_description=True, description_mode="long"
    )
    # needs to be here because resereved_words is declared first
    reserved_words += list(help_texts)

    def __init__(self):
        self.load_game()

    def create_game(self, game_name):
        """creates a new game in games dict"""
        games[game_name] = Game()
        return games[game_name]

    def verify_name(self, *names):
        """verifies a name for a game"""
        for name in names:
            if name in self.reserved_words:
                return "game names cannot be reserved words"
            elif not name:
                return "games must have names"
            elif name in games.keys():
                return "names must be unique, note that names are NOT case-sensitive"
        return "valid"

    def run_game(self, user, commands):
        """runs the game based on commands"""
        output_text = ""
        command = next(commands)
        play_game_name = ""

        # processing commands
        if command == "create":
            new_game_name = next(commands)
            valid = self.verify_name(new_game_name)
            if valid == "valid":
                self.create_game(new_game_name)
                play_game_name = new_game_name
            else:
                output_text = valid


        elif command == "rename":
            old_name = next(commands)
            new_name = next(commands)
            valid = self.verify_name(new_name)
            if valid != "valid":
                output_text = valid
            if old_name not in games.keys():
                output_text = "that game does not exist"
            games[new_name] = games.pop(old_name)
            play_game_name = new_name
            output_text = f"renamed {old_name} to {new_name}"

        elif command == "delete":
            delete_game_name = next(commands)
            if not delete_game_name:
                output_text = "you must give the name of the game"
            elif delete_game_name not in games.keys():
                output_text = "that game does not exist"
            else:
                if games["current game"] == games[delete_game_name]:
                    games["current game"] = None
                del games[delete_game_name]
                output_text = f"{delete_game_name} deleted"

        elif command == "games":
            output_text += utils.join_items(
                *[
                    (game_name, game.mode.name(), game.score)
                    for game_name, game in games.items()
                    if game_name != "current game"
                ],
                is_description=True
            )

        elif command in games:
            games["current game"] = games[command]

        elif command in self.help_texts:
            output_text += self.help_texts[command]

        else:
            # moves the generator back one command because the command was not used
            commands.send(-1)

        if not play_game_name:
            play_game_name = "current game"
        games["current game"] = games[play_game_name]

        if not output_text:
            if games[play_game_name]:
                output_text = games[play_game_name].play_game(commands)
            else:
                output_text = "no game selected"
        return output_text

    def load_game(self):
        """loads games from a json file"""
        data = utils.load(self.save_file)
        for game_name, game_data in data["games"].items():
            games[game_name] = Game(**game_data)
        for mode_name, mode in Game.modes.items():
            mode.high_score = data["scores"][mode_name]

    def save_game(self):
        """saves games to a json file"""
        games_dict = dict()
        for game_name, game in games.items():
            if game_name == "current game" or (game is None):
                continue
            games_dict[game_name] = {
                "board": [cell.value for cell in game.board.cells],
                "has_won": game.has_won,
                "mode": game.mode.name(),
                "score": game.score
            }
        high_scores = {mode_name: mode.high_score for mode_name, mode in Game.modes.items()}
        data = {"games": games_dict, "scores": high_scores}
        utils.save(self.save_file, data)
