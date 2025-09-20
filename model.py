import json
import math
import time
from numbs_aux import generate_numbers, test_numbers
from data_models import *

GAMES_AMOUNT = 10000
PLAYERS_PER_TEAM = 5
ROUNDS_PER_GAME = 10

class Model:
    def __init__(self):
        self.nums_configurations = []
        self.nums_index = 0
        self.numbers = []
        self.current_number = 0
        self.load_configurations()
        self.load_index()

    def set_presenter(self, presenter):
        self.presenter = presenter

    def start_simulation(self):
        # Iniciar medición de tiempo
        start_time = time.time()
        
        self.generate_sim_numbers()
        self.teams : list[Team] = self.generate_teams()
        self.players : list[Player] = []
        for team in self.teams:
            for i in range(PLAYERS_PER_TEAM):
                self.players.append(self.generate_player(team, f"Jugador {i+1} {team.name}"))
        
        # Tiempo después de generar números y jugadores
        setup_time = time.time() - start_time
        
        self.games : list[Game] = []
        games_start_time = time.time()
        
        for i in range(GAMES_AMOUNT):
            rounds : list[Round] = []
            for j in range(ROUNDS_PER_GAME):
                luck_values = self.generate_players_luck_values()
                shots, endurance_values = self.generate_shots_and_endurance_values(luck_values, rounds)
                winner_player, winner_team = self.calculate_winner(shots)
                rounds.append(Round(j+1,shots, luck_values, endurance_values, winner_player, winner_team))
            winner_player, winner_team, luckiest_player = self.calculate_game_winner(rounds)
            self.games.append(Game(i+1, rounds, winner_team, winner_player, luckiest_player))
        
        # Tiempo de generación de juegos
        games_generation_time = time.time() - games_start_time
        
        # Calcular resultados
        analysis_start_time = time.time()
        
        luckiest_player_per_game = self.calculate_luckiest_player_per_games()
        more_experienced_player = self.calculate_more_experienced_player()
        winner_team_total = self.calculate_team_winner()
        winner_gender_per_game = self.calculate_winner_gender_per_game()
        winner_gender_total = self.calculate_winner_gender_total()
        points_vs_games_per_player = self.calculate_points_vs_games_per_player()
        team_score_distribution = self.calculate_team_score_distribution()
        special_shots_analysis = self.calculate_special_shots_analysis()
        tied_rounds_analysis = self.calculate_tied_rounds_analysis()
        
        # Tiempo de análisis
        analysis_time = time.time() - analysis_start_time
        
        # Tiempo total
        total_time = time.time() - start_time
        
        # Calcular métricas de eficiencia
        efficiency_metrics = self.calculate_efficiency_metrics(
            total_time, setup_time, games_generation_time, analysis_time
        )
        
        results = {
            "luckiest_player_per_game": luckiest_player_per_game,
            "more_experienced_player": more_experienced_player,
            "winner_team_total": winner_team_total,
            "winner_gender_per_game": winner_gender_per_game,
            "winner_gender_total": winner_gender_total,
            "points_vs_games_per_player": points_vs_games_per_player,
            "team_score_distribution": team_score_distribution,
            "special_shots_analysis": special_shots_analysis,
            "tied_rounds_analysis": tied_rounds_analysis,
            "efficiency_metrics": efficiency_metrics
        }
        self.presenter.show_results(results)

    def generate_teams(self): 
        team1 = Team(name="Team A")
        team2 = Team(name="Team B")
        return [team1, team2]

    def generate_player(self, team, name):
        if self.get_pseudorandom_number() < 0.5:
            is_male = True
        else:
            is_male = False
        # Cambio: Resistencia inicial usando distribución uniforme U(25, 45)
        original_endurance = int(25 + (45 - 25) * self.get_pseudorandom_number())
        # Cambio: Experiencia inicial fija en 10
        experience = 10
        player = Player(name, team, is_male, original_endurance, experience)
        return player
    
    def generate_players_luck_values(self): 
        players_luck = []
        for player in self.players:
            # Cambio: Suerte usando distribución normal N(μ=1.5, σ=1)
            # Usamos Box-Muller para generar distribución normal
            luck_value = self.generate_normal_random(1.5, 1.0)
            # Aseguramos que sea positivo
            luck_value = max(0.1, luck_value)
            players_luck.append({"value": luck_value, "player": player}) 
        team_a_players = [player for player in players_luck if player["player"].team.name == "Team A"]
        team_b_players = [player for player in players_luck if player["player"].team.name == "Team B"]
        team_a_players.sort(key=lambda p: p["value"], reverse=True)
        team_b_players.sort(key=lambda p: p["value"], reverse=True)
        top_lucky_player_team_a = team_a_players[0] 
        top_lucky_player_team_b = team_b_players[0] 
        top_lucky_players = [
            LuckValue(top_lucky_player_team_a["player"], top_lucky_player_team_a["value"]), 
            LuckValue(top_lucky_player_team_b["player"], top_lucky_player_team_b["value"])
        ]
        return top_lucky_players
    
    def generate_normal_random(self, mu, sigma):
        """Genera número aleatorio con distribución normal usando Box-Muller"""
        u1 = self.get_pseudorandom_number()
        u2 = self.get_pseudorandom_number()
        
        # Proteger contra valores extremos que causarían error de dominio
        # Asegurar que u1 esté en el rango (0, 1) excluyendo los extremos
        u1 = max(1e-10, min(1 - 1e-10, u1))
        u2 = max(1e-10, min(1 - 1e-10, u2))
        
        # Box-Muller transform
        z0 = (-2 * math.log(u1))**0.5 * math.cos(2 * math.pi * u2)
        return mu + sigma * z0
   
    def generate_shots_and_endurance_values(self, luck_values: list[LuckValue], rounds: list[Round]):
        shots: list[Shot] = []
        endurance_values: list[EnduranceValue] = []
        points_total_rd = []
        for player in self.players:
            endurance = self.generatePlayer_endurance(player, rounds)
            current_endurance = endurance.value
            # normal shots
            pts = { "player": player, "points": 0 }
            while current_endurance >= 5:
                shot = self.do_shot(player, len(shots) + 1)
                shots.append(shot)
                current_endurance -= 5
                player.total_points += shot.score
                pts["points"] += shot.score
            endurance_values.append(endurance)
            points_total_rd.append(pts)
        
        # luck shots
        luckiest_players = [player for player in self.players if player.name == luck_values[0].player.name 
                            or player.name == luck_values[1].player.name]
        
        # Verificar jugadores con lanzamientos especiales en últimas 3 rondas (para obtener disparo adicional)
        if len(rounds) >= 3:
            names_list = []
            for round in list(filter(lambda value: (len(rounds) + 1) - value.round_number <= 3, rounds)):
                lvs = round.luck_values
                names_list.extend([lv.player.name for lv in lvs])
            for name in set(names_list):
                if len(list(filter(lambda name_l: name_l == name, names_list))) == 3:
                    luckiest_players.append(list(filter(lambda player: player.name == name, self.players))[0])
        
        # Disparos de suerte
        for player in luckiest_players:
            shot = self.do_shot(player, len(shots) + 1, "LS")
            shots.append(shot)
            player.total_points += shot.score
        
        # Verificar jugadores con lanzamientos especiales en 2 rondas consecutivas (disparo adicional)
        if len(rounds) >= 2:
            # Verificar las últimas 2 rondas
            last_two_rounds = rounds[-2:]
            for player in self.players:
                has_special_shots_consecutive = True
                for round_check in last_two_rounds:
                    player_in_luck = any(lv.player.name == player.name for lv in round_check.luck_values)
                    if not player_in_luck:
                        has_special_shots_consecutive = False
                        break
                
                if has_special_shots_consecutive:
                    # Dar disparo adicional
                    shot = self.do_shot(player, len(shots) + 1, "AS")  # AS = Additional Shot
                    shots.append(shot)
                    player.total_points += shot.score
        
        # extra shots
        max_pts = max([pts["points"] for pts in points_total_rd])
        max_pst_list = list(filter(lambda pts: pts["points"] == max_pts, points_total_rd))
        if len(max_pst_list) > 1:
            while len(set([pts["points"] for pts in max_pst_list])) != len(max_pst_list):
                for stl in max_pst_list:
                    player = stl["player"]
                    shot = self.do_shot(player, len(shots) + 1, "ES")
                    shots.append(shot)
                    player.total_points += shot.score
                    stl["points"] += shot.score
        return shots, endurance_values

    def do_shot(self, player: Player, n_shot: int, type = "NS"):
        num = self.get_pseudorandom_number()
        if player.is_male:
            score = self.calculate_score_male(num)
        else:
            score = self.calculate_score_female(num)
        return Shot(player, score, n_shot, type)
    
    def generatePlayer_endurance(self, player: Player, rounds: list[Round]):
        if not rounds:
            endurance = player.original_endurance
        else:
            last_endurance = list(filter(lambda value:value.player.name == player.name, 
                                            rounds[len(rounds) - 1].endurance_values))[0]
            
            # Calcular cuánta resistencia se gastó en la ronda anterior
            endurance_spent = player.original_endurance - last_endurance.value if len(rounds) == 1 else \
                             list(filter(lambda value:value.player.name == player.name, 
                                        rounds[len(rounds) - 2].endurance_values))[0].value - last_endurance.value
            
            # Jugadores con experiencia >= 19 (9+ puntos ganados, ya que empiezan con 10)
            if player.experience >= 19:
                # Solo pierden 1 punto en una sola ronda
                endurance = player.original_endurance - 1
            else:
                # Recuperación normal: total gastado menos 1, 2 o 3 unidades aleatoriamente
                random_reduction = self.get_random_reduction()
                recovery = max(0, endurance_spent - random_reduction)
                endurance = last_endurance.value + recovery
                
        return EnduranceValue(player, max(0, endurance))
    
    def get_random_reduction(self):
        """Retorna 1, 2 o 3 aleatoriamente para la reducción de recuperación"""
        rand = self.get_pseudorandom_number()
        if rand < 0.33:
            return 1
        elif rand < 0.66:
            return 2
        else:
            return 3

    def calculate_score_male(self, score):
        # Cambio: Nuevas probabilidades para hombres
        if score <= 0.15:  # 15%
            return 10
        elif score <= 0.45:  # 30% (15% + 30%)
            return 9
        elif score <= 0.92:  # 47% (45% + 47%)
            return 8
        else:  # 8% restante
            return 0
        
    def calculate_score_female(self, score):
        # Cambio: Nuevas probabilidades para mujeres
        if score <= 0.25:  # 25%
            return 10
        elif score <= 0.65:  # 40% (25% + 40%)
            return 9
        elif score <= 0.95:  # 30% (65% + 30%)
            return 8
        else:  # 5% restante
            return 0

    def calculate_winner(self, shots:list[Shot]):
        points_total_rd = [{"player":player, "points": 0} for player in self.players]
        team_a_points = 0
        team_b_points = 0
        for shot in shots:
            if shot.player.team.name == "Team A" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                team_a_points += shot.score
            if shot.player.team.name == "Team B" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                team_b_points += shot.score
            points_total_rd[self.players.index(shot.player)]["points"] += shot.score if shot.type == "NS" or shot.type == "ES" or shot.type == "AS" else 0
        winner_player = list(filter(lambda value: value["points"] == max([pts["points"] for pts in points_total_rd]), points_total_rd))[0]["player"]
        winner_team = None
        if team_a_points != team_b_points:
            max_tm_name = "Team A" if team_a_points > team_b_points else "Team B"
            winner_team = list(filter(lambda tm: tm.name == max_tm_name, self.teams))[0]
        list(filter(lambda player: player.name == winner_player.name, self.players))[0].experience += 3
        return winner_player, winner_team

    def calculate_game_winner(self, rounds:list[Round]):
        team_a_points = 0
        team_b_points = 0
        for round in rounds:
            for shot in round.shots:
                if shot.player.team.name == "Team A" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                    team_a_points += shot.score
                if shot.player.team.name == "Team B" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                    team_b_points += shot.score
        max_tm_name = "Team A" if team_a_points > team_b_points else "Team B"
        winner_team = list(filter(lambda tm: tm.name == max_tm_name, self.teams))[0]
        rds_winners = []
        lks_winners = []
        for round in rounds:
            for luck_value in round.luck_values:
                if luck_value.player.name in [lk_w['player'].name for lk_w in lks_winners]:
                    list(filter(lambda lk_w: lk_w['player'].name == luck_value.player.name, lks_winners))[0]['amount'] += 1
                else:
                    lks_winners.append({"player": luck_value.player, "amount": 1})
            if round.winner_player.name in [rd_w['player'].name for rd_w in rds_winners]:
                list(filter(lambda rd_w: rd_w['player'].name == round.winner_player.name, rds_winners))[0]['amount'] += 1
            else:
                rds_winners.append({"player": round.winner_player, "amount": 1})
        winner_player = list(filter(lambda rd_w: rd_w['amount'] == max([rd_w['amount'] for rd_w in rds_winners]), rds_winners))[0]['player']
        luckiest_player = list(filter(lambda lk_w: lk_w['amount'] == max([lk_w['amount'] for lk_w in lks_winners]), lks_winners))[0]['player']
        return winner_player, winner_team, luckiest_player

    def calculate_luckiest_player_per_games(self):
        luck_counts = {}
        for game in self.games:
            luckiest_player = game.luckiest_player
            if luck_counts.get(luckiest_player) == None:
                luck_counts[luckiest_player] = 0
            luck_counts[luckiest_player] += 1
        luckiest_player_overall = max(luck_counts, key=luck_counts.get)
        return {
            "player": luckiest_player_overall,
            "amount_luck": luck_counts[luckiest_player_overall]
        }

    def calculate_more_experienced_player(self):
        most_experienced_player = max(self.players, key=lambda player: player.experience)
        return {
            "player": most_experienced_player,
            "amount_experienced": most_experienced_player.experience
        }

    def calculate_team_winner(self):
        count_wins_team_a = 0
        count_wins_team_b = 0
        final_winner_team: Team = None
        final_players_win_points:list = []
        for game in self.games:
            count_wins_team_a += game.winner_team.name == 'Team A'
            count_wins_team_b += game.winner_team.name  == 'Team B'
        if count_wins_team_a > count_wins_team_b:
            final_winner_team = self.teams[0]
        else: 
            final_winner_team = self.teams[1]
        for player in self.players:
            if player.team.name == final_winner_team.name:
                final_players_win_points.append({"player":player.name, "points":player.total_points})
        return {"team":final_winner_team, "player_points": final_players_win_points}

    def calculate_winner_gender_per_game(self):
        count_wins_male = 0
        count_wins_female = 0
        count_win = 0
        gender_win = ''
        for game in self.games:
            if game.winner_player.is_male:
                count_wins_male += 1
            else:
                count_wins_female +=1
        if count_wins_male > count_wins_female:
            gender_win = 'Hombres'
            count_win = count_wins_male
        else:
            gender_win = 'Mujeres'
            count_win = count_wins_female
        return {"gender": gender_win  , "amount_wins":count_win }

    def calculate_winner_gender_total(self):
        male_wins = 0
        female_wins = 0
        for game in self.games:
            for round_game in game.rounds:
                winner_player = round_game.winner_player
                if winner_player.is_male:
                    male_wins += 1
                else:
                    female_wins += 1
        winner_gender = "Hombres" if male_wins > female_wins else "Mujeres"
        return {
            "gender": winner_gender,
            "total_rounds_won": max(male_wins, female_wins)
        }

    def calculate_points_vs_games_per_player(self):
        players_with_points: list = [{"player": player, "points": []} for player in self.players]
        for game in self.games:
            game_points = {player.name: 0 for player in self.players}
            for round_game in game.rounds:
                for shot in round_game.shots:
                    game_points[shot.player.name] += shot.score
            for player_points in players_with_points:
                player_name = player_points["player"].name
                player_points["points"].append(game_points.get(player_name, 0))
        return players_with_points

    def calculate_team_score_distribution(self):
        """Calcula distribución de puntajes promedio por equipo con análisis de dispersión"""
        team_a_scores = []
        team_b_scores = []
        
        for game in self.games:
            team_a_game_score = 0
            team_b_game_score = 0
            
            for round_game in game.rounds:
                for shot in round_game.shots:
                    if shot.player.team.name == "Team A" and shot.type in ["NS", "LS", "AS"]:
                        team_a_game_score += shot.score
                    elif shot.player.team.name == "Team B" and shot.type in ["NS", "LS", "AS"]:
                        team_b_game_score += shot.score
            
            team_a_scores.append(team_a_game_score)
            team_b_scores.append(team_b_game_score)
        
        # Cálculos estadísticos
        team_a_avg = sum(team_a_scores) / len(team_a_scores)
        team_b_avg = sum(team_b_scores) / len(team_b_scores)
        
        # Varianza y desviación estándar
        team_a_variance = sum((score - team_a_avg) ** 2 for score in team_a_scores) / len(team_a_scores)
        team_b_variance = sum((score - team_b_avg) ** 2 for score in team_b_scores) / len(team_b_scores)
        
        team_a_std = team_a_variance ** 0.5
        team_b_std = team_b_variance ** 0.5
        
        return {
            "team_a": {
                "name": "Team A",
                "average_score": round(team_a_avg, 2),
                "variance": round(team_a_variance, 2),
                "std_deviation": round(team_a_std, 2),
                "scores": team_a_scores
            },
            "team_b": {
                "name": "Team B", 
                "average_score": round(team_b_avg, 2),
                "variance": round(team_b_variance, 2),
                "std_deviation": round(team_b_std, 2),
                "scores": team_b_scores
            }
        }

    def calculate_special_shots_analysis(self):
        """Calcula promedio de lanzamientos especiales por equipo y correlación con experiencia"""
        team_a_special_shots = 0
        team_b_special_shots = 0
        
        # Contar lanzamientos especiales por equipo
        for game in self.games:
            for round_game in game.rounds:
                for shot in round_game.shots:
                    if shot.type in ["LS", "AS"]:  # Lanzamientos especiales
                        if shot.player.team.name == "Team A":
                            team_a_special_shots += 1
                        else:
                            team_b_special_shots += 1
        
        # Promedios por juego
        team_a_avg_special = team_a_special_shots / GAMES_AMOUNT
        team_b_avg_special = team_b_special_shots / GAMES_AMOUNT
        
        # Calcular experiencia ganada por equipo
        team_a_players = [p for p in self.players if p.team.name == "Team A"]
        team_b_players = [p for p in self.players if p.team.name == "Team B"]
        
        team_a_experience_gained = sum(p.experience - 10 for p in team_a_players)  # 10 es la experiencia inicial
        team_b_experience_gained = sum(p.experience - 10 for p in team_b_players)
        
        # Correlación simple (lanzamientos especiales vs experiencia ganada)
        correlation_a = team_a_special_shots * team_a_experience_gained if team_a_experience_gained > 0 else 0
        correlation_b = team_b_special_shots * team_b_experience_gained if team_b_experience_gained > 0 else 0
        
        return {
            "team_a": {
                "name": "Team A",
                "total_special_shots": team_a_special_shots,
                "avg_special_shots_per_game": round(team_a_avg_special, 2),
                "experience_gained": team_a_experience_gained,
                "correlation_factor": round(correlation_a / 1000, 2)  # Factor normalizado
            },
            "team_b": {
                "name": "Team B",
                "total_special_shots": team_b_special_shots,
                "avg_special_shots_per_game": round(team_b_avg_special, 2),
                "experience_gained": team_b_experience_gained,
                "correlation_factor": round(correlation_b / 1000, 2)  # Factor normalizado
            }
        }

    def calculate_tied_rounds_analysis(self):
        """Calcula número de rondas empatadas y frecuencia relativa"""
        tied_rounds_count = 0
        total_rounds = GAMES_AMOUNT * ROUNDS_PER_GAME
        
        for game in self.games:
            for round_game in game.rounds:
                if round_game.winner_team is None:  # Ronda empatada
                    tied_rounds_count += 1
        
        tied_frequency = (tied_rounds_count / total_rounds) * 100
        
        return {
            "tied_rounds_count": tied_rounds_count,
            "total_rounds": total_rounds,
            "tied_frequency_percent": round(tied_frequency, 2),
            "non_tied_rounds": total_rounds - tied_rounds_count,
            "non_tied_frequency_percent": round(100 - tied_frequency, 2)
        }
    
    def calculate_efficiency_metrics(self, total_time, setup_time, games_generation_time, analysis_time):
        """Calcula métricas de eficiencia del sistema"""
        # Calcular totales de elementos procesados
        total_shots = sum(len(round.shots) for game in self.games for round in game.rounds)
        total_rounds = len(self.games) * ROUNDS_PER_GAME
        total_luck_calculations = total_rounds * 2  # 2 por ronda (uno por equipo)
        
        # Velocidades de procesamiento
        games_per_second = GAMES_AMOUNT / games_generation_time if games_generation_time > 0 else 0
        rounds_per_second = total_rounds / games_generation_time if games_generation_time > 0 else 0
        shots_per_second = total_shots / games_generation_time if games_generation_time > 0 else 0
        
        # Distribución de tiempo
        setup_percentage = (setup_time / total_time) * 100
        games_percentage = (games_generation_time / total_time) * 100
        analysis_percentage = (analysis_time / total_time) * 100
        
        # Eficiencia de memoria (aproximada)
        memory_efficiency = {
            "total_games_stored": len(self.games),
            "total_rounds_stored": total_rounds,
            "total_shots_stored": total_shots,
            "average_shots_per_round": total_shots / total_rounds if total_rounds > 0 else 0
        }
        
        return {
            "timing": {
                "total_time_seconds": round(total_time, 3),
                "total_time_minutes": round(total_time / 60, 2),
                "setup_time_seconds": round(setup_time, 3),
                "games_generation_time_seconds": round(games_generation_time, 3),
                "analysis_time_seconds": round(analysis_time, 3)
            },
            "time_distribution": {
                "setup_percentage": round(setup_percentage, 2),
                "games_generation_percentage": round(games_percentage, 2),
                "analysis_percentage": round(analysis_percentage, 2)
            },
            "processing_rates": {
                "games_per_second": round(games_per_second, 2),
                "rounds_per_second": round(rounds_per_second, 2),
                "shots_per_second": round(shots_per_second, 2),
                "luck_calculations_per_second": round(total_luck_calculations / games_generation_time, 2) if games_generation_time > 0 else 0
            },
            "data_volume": {
                "total_games": GAMES_AMOUNT,
                "total_rounds": total_rounds,
                "total_shots": total_shots,
                "total_luck_calculations": total_luck_calculations,
                "average_shots_per_game": round(total_shots / GAMES_AMOUNT, 2),
                "average_shots_per_round": round(total_shots / total_rounds, 2)
            },
            "memory_efficiency": memory_efficiency,
            "system_performance": {
                "throughput_score": round((total_shots + total_luck_calculations) / total_time, 2),
                "efficiency_ratio": round(games_generation_time / total_time, 3),
                "processing_intensity": "High" if shots_per_second > 1000 else "Medium" if shots_per_second > 100 else "Low"
            }
        }
    
    def get_pseudorandom_number(self):
        number = self.numbers[self.current_number]
        self.current_number += 1
        return number

    def generate_sim_numbers(self):
        self.numbers = generate_numbers(self.nums_configurations[self.nums_index]['conf1'])
        self.numbers.extend(generate_numbers(self.nums_configurations[self.nums_index]['conf2']))
        self.change_index()
        while not test_numbers(self.numbers):
            self.numbers = generate_numbers(self.nums_configurations[self.nums_index]['conf1']).extend(
                generate_numbers(self.nums_configurations[self.nums_index]['conf2']))
            self.change_index()

    def load_configurations(self):
        with open('lcg_configurations.json', 'r') as f:
            self.nums_configurations = json.load(f)

    def load_index(self):
        with open('nums_info.json', 'r') as f:
            self.nums_index = json.load(f)["index"]

    def change_index(self):
        self.nums_index = self.nums_index + 1 if self.nums_index < len(self.nums_configurations) - 1 else 0
        with open('nums_info.json', 'w') as f:
            json.dump({"index": self.nums_index}, f)