"""
functions shared between games that don't fit in utils
"""
import utils
import math

HANGOUTS_CHAR_LIMIT = 2000


def profile(self, player, commands):
    """returns player profiles"""
    PLAYERS_PER_PAGE = 5
    players = self.players
    output_text = ""
    player_name = next(commands)
    page = utils.default(next(commands), 1)
    try:
        page = int(page)
    except TypeError:
        page = 1

    # create list of players
    possible_players = []
    for possible_player in players.values():
        if player_name in possible_player.name:
            possible_players.append(possible_player)
    if player_name.isdigit() and int(player_name) in players:
        possible_players.append(players[int(player_name)])
    elif player_name == "self":
        possible_players.append(player)
    elif player_name == "all":
        possible_players = list(players.values())

    # input validation
    if not possible_players:
        return "No players go by that name/id!"

    if len(possible_players) > 1:
        output_text += utils.newline(
            f"{len(possible_players)} player(s) go by that name:")
    try:
        possible_players_slice = possible_players[
            (page - 1) * PLAYERS_PER_PAGE: page * PLAYERS_PER_PAGE
        ]
    except IndexError:
        if page * 5 > len(possible_players):
            possible_players_slice = possible_players[0:]
        else:
            possible_players_slice = possible_players[(page - 1) * PLAYERS_PER_PAGE:]

    output_text += utils.join_items(
        *[
            player.profile()
            for player in possible_players_slice
        ], separator="\n" * 2
    ) + f"{page}/{math.ceil(len(possible_players) / PLAYERS_PER_PAGE)}"
    return output_text


def get_players(players, player_name, running_player=None, single=False):
    possible_players = []
    for possible_player in players.values():
        if (
            (not single and player_name in possible_player.name)
            or (single and player_name == possible_player.name)
        ):
            possible_players.append(possible_player)

    if player_name.isdigit() and int(player_name) in players:
        possible_players.append(players[int(player_name)])
    elif player_name == "self" and running_player:
        possible_players.append(running_player)
    return utils.default(possible_players[0], possible_players, single)
