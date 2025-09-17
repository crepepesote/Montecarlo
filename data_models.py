class Team:
    def __init__(self, name):
        self.name = name

class Player:
    def __init__(self, name, team, is_male, original_endurance, experience):
        self.name = name
        self.team = team
        self.is_male = is_male
        self.original_endurance = original_endurance
        self.experience = experience
        self.total_points = 0

class Shot:
    def __init__(self, player, score, shot_number, type):
        self.player = player
        self.score = score
        self.shot_number = shot_number
        self.type = type # los tipos son: "NS" (normal), "LS" (de sorteo), "ES" (extra para ganador individual)

class LuckValue:
    def __init__(self, player, value):
        self.player = player
        self.value = value

class EnduranceValue:
    def __init__(self, player, value):
        self.player = player
        self.value = value

class Round:
    def __init__(self, round_number, shots, luck_values, endurance_values, winner_player, winner_team):
        self.round_number = round_number
        self.shots = shots
        self.luck_values = luck_values # son dos, una para cada jugador con mas suerte de cada equipo
        self.endurance_values = endurance_values # uno para cada jugador, este es el que se debe modificar, no el del jugador
        self.winner_player = winner_player
        self.winner_team = winner_team

class Game:
    def __init__(self, game_number, rounds, winner_team, winner_player, luckiest_player):
        self.game_number = game_number
        self.rounds = rounds
        self.winner_team = winner_team
        self.winner_player = winner_player
        self.luckiest_player = luckiest_player