import math
import time
import csv
from data_models import *

GAMES_AMOUNT = 10000
PLAYERS_PER_TEAM = 5
ROUNDS_PER_GAME = 10

class Model:
    def __init__(self, csv_file='numeros.csv'):
        """
        Modelo que consume números pseudoaleatorios exclusivamente desde CSV.
        No tiene capacidad de generar números - solo los consume.
        """
        self.csv_file = csv_file
        self.numbers = []
        self.current_number = 0
        self.total_numbers_loaded = 0
        self.load_numbers_from_csv()

    def set_presenter(self, presenter):
        self.presenter = presenter

    def load_numbers_from_csv(self):
        """Carga todos los números desde el archivo CSV"""
        print("📁 Cargando números desde CSV...")
        start_time = time.time()
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row_count, row in enumerate(csv_reader, 1):
                    number = float(row['number'])
                    self.numbers.append(number)
                    
                    # Mostrar progreso cada 250,000 números
                    if row_count % 250000 == 0:
                        print(f"   📊 Cargados: {row_count:,} números...")
                
                self.total_numbers_loaded = len(self.numbers)
                load_time = time.time() - start_time
                
                print(f"✅ Números cargados exitosamente:")
                print(f"   📈 Total: {self.total_numbers_loaded:,} números")
                print(f"   ⏱️  Tiempo: {load_time:.2f} segundos")
                print(f"   🚀 Velocidad: {self.total_numbers_loaded/load_time:,.0f} números/seg")
                
        except FileNotFoundError:
            print(f"❌ ERROR: No se encontró el archivo '{self.csv_file}'")
            print("\n💡 SOLUCIÓN:")
            print("   1. Genera el archivo CSV primero usando el generador separado")
            print("   2. Asegúrate de que el nombre del archivo sea correcto")
            print("   3. Verifica que esté en la carpeta correcta")
            raise
        except KeyError:
            print(f"❌ ERROR: El CSV no tiene la columna 'number' esperada")
            print("\n💡 SOLUCIÓN:")
            print("   Asegúrate de que el CSV tenga las columnas: index, number")
            raise
        except Exception as e:
            print(f"❌ ERROR al cargar CSV: {e}")
            raise

    def check_simulation_feasibility(self):
        """Verifica si la simulación es factible con los números disponibles"""
        # Estimación más precisa basada en análisis del código
        estimated_per_round = 55  # Número promedio estimado por ronda
        estimated_total = GAMES_AMOUNT * ROUNDS_PER_GAME * estimated_per_round
        
        available = self.total_numbers_loaded - self.current_number
        
        print(f"\n🔍 ANÁLISIS DE FACTIBILIDAD:")
        print(f"   📊 Números disponibles: {available:,}")
        print(f"   🎯 Estimación necesaria: {estimated_total:,}")
        print(f"   📈 Configuración actual:")
        print(f"      - Juegos: {GAMES_AMOUNT:,}")
        print(f"      - Rondas por juego: {ROUNDS_PER_GAME}")
        print(f"      - Jugadores: {PLAYERS_PER_TEAM * 2}")
        
        if available >= estimated_total:
            margin = available - estimated_total
            margin_percent = (margin / estimated_total) * 100
            print(f"   ✅ FACTIBLE - Margen: {margin:,} números ({margin_percent:.1f}%)")
            return True
        else:
            deficit = estimated_total - available
            print(f"   ❌ INSUFICIENTE - Faltan: {deficit:,} números")
            print(f"\n💡 OPCIONES:")
            print(f"      1. Generar más números en el CSV")
            print(f"      2. Reducir GAMES_AMOUNT a {(available // (ROUNDS_PER_GAME * estimated_per_round)):,}")
            return False

    def get_pseudorandom_number(self):
        """
        Obtiene el siguiente número pseudoaleatorio del CSV.
        Es la ÚNICA forma de obtener números en este modelo.
        """
        if self.current_number >= len(self.numbers):
            remaining = len(self.numbers) - self.current_number
            raise IndexError(
                f"❌ NÚMEROS AGOTADOS!\n"
                f"   Intentando acceder al número {self.current_number + 1}\n"
                f"   Disponibles: {len(self.numbers):,}\n"
                f"   Usados: {self.current_number:,}\n"
                f"   Restantes: {remaining:,}\n\n"
                f"💡 SOLUCIÓN: Genera más números en el CSV"
            )
        
        number = self.numbers[self.current_number]
        self.current_number += 1
        return number

    def get_consumption_stats(self):
        """Obtiene estadísticas actuales del consumo de números"""
        used = self.current_number
        total = self.total_numbers_loaded
        remaining = total - used
        percentage_used = (used / total) * 100 if total > 0 else 0
        
        return {
            "used": used,
            "total": total,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "estimated_games_remaining": remaining // 550 if remaining > 0 else 0  # ~550 números por juego
        }

    def start_simulation(self):
        """Inicia la simulación consumiendo números exclusivamente del CSV"""
        
        # Verificar factibilidad antes de comenzar
        if not self.check_simulation_feasibility():
            response = input("\n❓ ¿Continuar de todos modos? (s/n): ").lower().strip()
            if response not in ['s', 'si', 'sí', 'y', 'yes']:
                print("🚫 Simulación cancelada por el usuario")
                return
        
        print(f"\n🚀 INICIANDO SIMULACIÓN")
        print("="*50)
        
        # Iniciar medición de tiempo
        start_time = time.time()
        initial_numbers_used = self.current_number
        
        # Generar equipos y jugadores
        self.teams : list[Team] = self.generate_teams()
        self.players : list[Player] = []
        for team in self.teams:
            for i in range(PLAYERS_PER_TEAM):
                self.players.append(self.generate_player(team, f"Jugador {i+1} {team.name}"))
        
        setup_time = time.time() - start_time
        print(f"✅ Equipos y jugadores generados ({setup_time:.2f}s)")
        
        # Generar juegos
        self.games : list[Game] = []
        games_start_time = time.time()
        
        # Configurar progreso
        progress_interval = max(1, GAMES_AMOUNT // 10)  # 10 actualizaciones
        
        try:
            for i in range(GAMES_AMOUNT):
                rounds : list[Round] = []
                for j in range(ROUNDS_PER_GAME):
                    luck_values = self.generate_players_luck_values()
                    shots, endurance_values = self.generate_shots_and_endurance_values(luck_values, rounds)
                    winner_player, winner_team = self.calculate_winner(shots)
                    rounds.append(Round(j+1, shots, luck_values, endurance_values, winner_player, winner_team))
                
                winner_player, winner_team, luckiest_player = self.calculate_game_winner(rounds)
                self.games.append(Game(i+1, rounds, winner_team, winner_player, luckiest_player))
                
                # Mostrar progreso
                if (i + 1) % progress_interval == 0 or i == GAMES_AMOUNT - 1:
                    progress = ((i + 1) / GAMES_AMOUNT) * 100
                    stats = self.get_consumption_stats()
                    elapsed = time.time() - games_start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    
                    print(f"⏳ Progreso: {progress:5.1f}% ({i+1:,}/{GAMES_AMOUNT:,}) | "
                          f"📊 Números: {stats['used']:,} ({stats['percentage_used']:4.1f}%) | "
                          f"🚀 Velocidad: {rate:.1f} juegos/s")
                        
        except IndexError as e:
            print(f"\n❌ ERROR DURANTE LA SIMULACIÓN:")
            print(f"   {e}")
            print(f"\n📊 Estadísticas al momento del error:")
            stats = self.get_consumption_stats()
            print(f"   Juegos completados: {len(self.games):,}/{GAMES_AMOUNT:,}")
            print(f"   Números consumidos: {stats['used']:,}")
            print(f"   Progreso: {(len(self.games)/GAMES_AMOUNT)*100:.1f}%")
            return
        
        games_generation_time = time.time() - games_start_time
        numbers_consumed = self.get_consumption_stats()['used'] - initial_numbers_used
        
        print(f"\n✅ JUEGOS COMPLETADOS:")
        print(f"   🎮 Total: {GAMES_AMOUNT:,} juegos")
        print(f"   ⏱️  Tiempo: {games_generation_time:.2f} segundos")
        print(f"   📊 Números consumidos: {numbers_consumed:,}")
        
        # Análisis de resultados
        print(f"\n🔬 ANALIZANDO RESULTADOS...")
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
        
        analysis_time = time.time() - analysis_start_time
        total_time = time.time() - start_time
        
        # Métricas finales
        final_stats = self.get_consumption_stats()
        efficiency_metrics = self.calculate_efficiency_metrics(
            total_time, setup_time, games_generation_time, analysis_time, 
            numbers_consumed, final_stats
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
        
        # Mostrar resumen final
        print(f"\n📈 RESUMEN FINAL:")
        print("="*50)
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos ({total_time/60:.1f} minutos)")
        print(f"📊 Números consumidos: {numbers_consumed:,}")
        print(f"📉 Números restantes: {final_stats['remaining']:,}")
        print(f"🎯 Promedio por juego: {numbers_consumed/GAMES_AMOUNT:.1f} números")
        print(f"🎲 Utilización total: {final_stats['percentage_used']:.2f}%")
        print(f"♻️  Juegos adicionales posibles: ~{final_stats['estimated_games_remaining']:,}")
        
        # Entregar resultados
        self.presenter.show_results(results)
        print(f"\n🎉 ¡SIMULACIÓN COMPLETADA EXITOSAMENTE!")

    # ===================================================================
    # MÉTODOS DE SIMULACIÓN - Sin cambios, solo usan get_pseudorandom_number()
    # ===================================================================

    def generate_teams(self): 
        team1 = Team(name="Team A")
        team2 = Team(name="Team B")
        return [team1, team2]

    def generate_player(self, team, name):
        if self.get_pseudorandom_number() < 0.5:
            is_male = True
        else:
            is_male = False
        original_endurance = int(25 + (45 - 25) * self.get_pseudorandom_number())
        experience = 10
        player = Player(name, team, is_male, original_endurance, experience)
        return player
    
    def generate_players_luck_values(self): 
        players_luck = []
        for player in self.players:
            luck_value = self.generate_normal_random(1.5, 1.0)
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
        
        u1 = max(1e-10, min(1 - 1e-10, u1))
        u2 = max(1e-10, min(1 - 1e-10, u2))
        
        z0 = (-2 * math.log(u1))**0.5 * math.cos(2 * math.pi * u2)
        return mu + sigma * z0
   
    def generate_shots_and_endurance_values(self, luck_values: list[LuckValue], rounds: list[Round]):
        shots: list[Shot] = []
        endurance_values: list[EnduranceValue] = []
        points_total_rd = []
        for player in self.players:
            endurance = self.generatePlayer_endurance(player, rounds)
            current_endurance = endurance.value
            pts = { "player": player, "points": 0 }
            while current_endurance >= 5:
                shot = self.do_shot(player, len(shots) + 1)
                shots.append(shot)
                current_endurance -= 5
                player.total_points += shot.score
                pts["points"] += shot.score
            endurance_values.append(endurance)
            points_total_rd.append(pts)
        
        luckiest_players = [player for player in self.players if player.name == luck_values[0].player.name 
                            or player.name == luck_values[1].player.name]
        
        if len(rounds) >= 3:
            names_list = []
            for round in list(filter(lambda value: (len(rounds) + 1) - value.round_number <= 3, rounds)):
                lvs = round.luck_values
                names_list.extend([lv.player.name for lv in lvs])
            for name in set(names_list):
                if len(list(filter(lambda name_l: name_l == name, names_list))) == 3:
                    luckiest_players.append(list(filter(lambda player: player.name == name, self.players))[0])
        
        for player in luckiest_players:
            shot = self.do_shot(player, len(shots) + 1, "LS")
            shots.append(shot)
            player.total_points += shot.score
        
        if len(rounds) >= 2:
            last_two_rounds = rounds[-2:]
            for player in self.players:
                has_special_shots_consecutive = True
                for round_check in last_two_rounds:
                    player_in_luck = any(lv.player.name == player.name for lv in round_check.luck_values)
                    if not player_in_luck:
                        has_special_shots_consecutive = False
                        break
                
                if has_special_shots_consecutive:
                    shot = self.do_shot(player, len(shots) + 1, "AS")
                    shots.append(shot)
                    player.total_points += shot.score
        
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
            
            endurance_spent = player.original_endurance - last_endurance.value if len(rounds) == 1 else \
                             list(filter(lambda value:value.player.name == player.name, 
                                        rounds[len(rounds) - 2].endurance_values))[0].value - last_endurance.value
            
            if player.experience >= 19:
                endurance = player.original_endurance - 1
            else:
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
        if score <= 0.15:
            return 10
        elif score <= 0.45:
            return 9
        elif score <= 0.92:
            return 8
        else:
            return 0
        
    def calculate_score_female(self, score):
        if score <= 0.25:
            return 10
        elif score <= 0.65:
            return 9
        elif score <= 0.95:
            return 8
        else:
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

    # ===================================================================
    # MÉTODOS DE ANÁLISIS - Sin cambios
    # ===================================================================

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
        
        team_a_avg = sum(team_a_scores) / len(team_a_scores)
        team_b_avg = sum(team_b_scores) / len(team_b_scores)
        
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
        team_a_special_shots = 0
        team_b_special_shots = 0
        
        for game in self.games:
            for round_game in game.rounds:
                for shot in round_game.shots:
                    if shot.type in ["LS", "AS"]:
                        if shot.player.team.name == "Team A":
                            team_a_special_shots += 1
                        else:
                            team_b_special_shots += 1
        
        team_a_avg_special = team_a_special_shots / GAMES_AMOUNT
        team_b_avg_special = team_b_special_shots / GAMES_AMOUNT
        
        team_a_players = [p for p in self.players if p.team.name == "Team A"]
        team_b_players = [p for p in self.players if p.team.name == "Team B"]
        
        team_a_experience_gained = sum(p.experience - 10 for p in team_a_players)
        team_b_experience_gained = sum(p.experience - 10 for p in team_b_players)
        
        correlation_a = team_a_special_shots * team_a_experience_gained if team_a_experience_gained > 0 else 0
        correlation_b = team_b_special_shots * team_b_experience_gained if team_b_experience_gained > 0 else 0
        
        return {
            "team_a": {
                "name": "Team A",
                "total_special_shots": team_a_special_shots,
                "avg_special_shots_per_game": round(team_a_avg_special, 2),
                "experience_gained": team_a_experience_gained,
                "correlation_factor": round(correlation_a / 1000, 2)
            },
            "team_b": {
                "name": "Team B",
                "total_special_shots": team_b_special_shots,
                "avg_special_shots_per_game": round(team_b_avg_special, 2),
                "experience_gained": team_b_experience_gained,
                "correlation_factor": round(correlation_b / 1000, 2)
            }
        }

    def calculate_tied_rounds_analysis(self):
        tied_rounds_count = 0
        total_rounds = GAMES_AMOUNT * ROUNDS_PER_GAME
        
        for game in self.games:
            for round_game in game.rounds:
                if round_game.winner_team is None:
                    tied_rounds_count += 1
        
        tied_frequency = (tied_rounds_count / total_rounds) * 100
        
        return {
            "tied_rounds_count": tied_rounds_count,
            "total_rounds": total_rounds,
            "tied_frequency_percent": round(tied_frequency, 2),
            "non_tied_rounds": total_rounds - tied_rounds_count,
            "non_tied_frequency_percent": round(100 - tied_frequency, 2)
        }
    
    def calculate_efficiency_metrics(self, total_time, setup_time, games_generation_time, analysis_time, 
                                   numbers_consumed, consumption_stats):
        """Calcula métricas de eficiencia incluyendo el consumo de números del CSV"""
        total_shots = sum(len(round.shots) for game in self.games for round in game.rounds)
        total_rounds = len(self.games) * ROUNDS_PER_GAME
        total_luck_calculations = total_rounds * 2
        
        games_per_second = GAMES_AMOUNT / games_generation_time if games_generation_time > 0 else 0
        rounds_per_second = total_rounds / games_generation_time if games_generation_time > 0 else 0
        shots_per_second = total_shots / games_generation_time if games_generation_time > 0 else 0
        numbers_per_second = numbers_consumed / games_generation_time if games_generation_time > 0 else 0
        
        setup_percentage = (setup_time / total_time) * 100
        games_percentage = (games_generation_time / total_time) * 100
        analysis_percentage = (analysis_time / total_time) * 100
        
        numbers_efficiency = {
            "numbers_consumed": numbers_consumed,
            "numbers_remaining": consumption_stats['remaining'],
            "consumption_percentage": consumption_stats['percentage_used'],
            "numbers_per_game": numbers_consumed / GAMES_AMOUNT if GAMES_AMOUNT > 0 else 0,
            "numbers_per_round": numbers_consumed / total_rounds if total_rounds > 0 else 0,
            "numbers_per_shot": numbers_consumed / total_shots if total_shots > 0 else 0,
            "csv_utilization_efficiency": "Excellent" if consumption_stats['percentage_used'] < 25 else "Good" if consumption_stats['percentage_used'] < 50 else "Fair"
        }
        
        memory_efficiency = {
            "total_games_stored": len(self.games),
            "total_rounds_stored": total_rounds,
            "total_shots_stored": total_shots,
            "average_shots_per_round": total_shots / total_rounds if total_rounds > 0 else 0,
            "csv_memory_footprint": f"{len(self.numbers) * 8 // 1024 // 1024} MB"  # Aproximado
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
                "numbers_per_second": round(numbers_per_second, 2),
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
            "numbers_efficiency": numbers_efficiency,
            "memory_efficiency": memory_efficiency,
            "csv_performance": {
                "csv_source": self.csv_file,
                "total_numbers_loaded": self.total_numbers_loaded,
                "peak_memory_usage": f"~{len(self.numbers) * 8 // 1024 // 1024} MB",
                "numbers_consumption_rate": round(numbers_consumed / total_time, 2),
                "csv_read_efficiency": "Single load at startup - optimal for multiple simulations"
            },
            "system_performance": {
                "throughput_score": round((total_shots + total_luck_calculations) / total_time, 2),
                "efficiency_ratio": round(games_generation_time / total_time, 3),
                "processing_intensity": "High" if shots_per_second > 1000 else "Medium" if shots_per_second > 100 else "Low",
                "numbers_utilization": numbers_efficiency["csv_utilization_efficiency"],
                "overall_performance": "Excellent" if games_per_second > 50 else "Good" if games_per_second > 20 else "Fair"
            }
        }