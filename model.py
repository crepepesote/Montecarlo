import math
import time
import csv
from data_models import *

# Configuración global de la simulación
GAMES_AMOUNT = 10000        # Cantidad total de juegos a simular
PLAYERS_PER_TEAM = 5        # Número de jugadores por equipo
ROUNDS_PER_GAME = 10        # Número de rondas por cada juego

class Model:
    """
    Clase principal del modelo de simulación de juegos.
    
    Este modelo simula juegos entre dos equipos, donde cada juego consiste en múltiples
    rondas y los jugadores realizan disparos basados en su resistencia y suerte.
    
    Características principales:
    - Consume números pseudoaleatorios exclusivamente desde un archivo CSV
    - No genera números aleatorios propios
    - Simula equipos, jugadores, juegos, rondas y disparos
    - Calcula estadísticas y métricas de rendimiento
    """
    
    def __init__(self, csv_file='numeros.csv'):
        """
        Inicializa el modelo con configuración básica.
        
        Args:
            csv_file (str): Ruta al archivo CSV que contiene los números pseudoaleatorios
        
        Atributos:
            csv_file: Nombre del archivo CSV con números
            numbers: Lista que almacena todos los números cargados del CSV
            current_number: Índice del próximo número a consumir
            total_numbers_loaded: Total de números cargados exitosamente
        """
        self.csv_file = csv_file
        self.numbers = []                # Lista de números pseudoaleatorios del CSV
        self.current_number = 0          # Índice del próximo número a usar
        self.total_numbers_loaded = 0    # Contador total de números disponibles
        self.load_numbers_from_csv()     # Carga automática al inicializar

    def set_presenter(self, presenter):
        """
        Establece el objeto presentador para mostrar resultados.
        
        Args:
            presenter: Objeto encargado de presentar los resultados de la simulación
        """
        self.presenter = presenter

    def load_numbers_from_csv(self):
        """
        Carga todos los números pseudoaleatorios desde el archivo CSV.
        
        Este es el único método que lee datos externos. Carga todos los números
        de una vez en memoria para acceso rápido durante la simulación.
        
        Funcionalidades:
        - Lee archivo CSV con columna 'number'
        - Muestra progreso cada 250,000 números
        - Calcula estadísticas de carga (tiempo, velocidad)
        - Maneja errores de archivo no encontrado o formato incorrecto
        
        Raises:
            FileNotFoundError: Si el archivo CSV no existe
            KeyError: Si el CSV no tiene la columna 'number'
            Exception: Para otros errores de lectura
        """
        print("📁 Cargando números desde CSV...")
        start_time = time.time()
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                # Leer todos los números del CSV
                for row_count, row in enumerate(csv_reader, 1):
                    number = float(row['number'])    # Convierte a float
                    self.numbers.append(number)      # Almacena en memoria
                    
                    # Mostrar progreso cada 250,000 números para archivos grandes
                    if row_count % 250000 == 0:
                        print(f"   📊 Cargados: {row_count:,} números...")
                
                # Calcular estadísticas de carga
                self.total_numbers_loaded = len(self.numbers)
                load_time = time.time() - start_time
                
                # Mostrar resumen de carga exitosa
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
        """
        Verifica si la simulación es factible con los números disponibles.
        
        Calcula una estimación de cuántos números se necesitan para completar
        la simulación y los compara con los disponibles.
        
        Estimación basada en:
        - ~55 números promedio por ronda (valor empírico)
        - GAMES_AMOUNT * ROUNDS_PER_GAME * números_por_ronda
        
        Returns:
            bool: True si hay suficientes números, False si no
        
        Muestra:
            - Números disponibles vs estimación necesaria
            - Margen de seguridad o déficit
            - Configuración actual de la simulación
            - Sugerencias si hay déficit
        """
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
        
        Este es el ÚNICO método para obtener números aleatorios en todo el sistema.
        Implementa un consumo secuencial de los números cargados.
        
        Returns:
            float: El siguiente número pseudoaleatorio (entre 0 y 1)
        
        Raises:
            IndexError: Si se agotan los números disponibles
        
        Funcionamiento:
        1. Verifica que hay números disponibles
        2. Obtiene el número en la posición current_number
        3. Incrementa el índice para el próximo acceso
        4. Retorna el número
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
        
        number = self.numbers[self.current_number]  # Obtiene el número actual
        self.current_number += 1                    # Avanza al siguiente
        return number

    def get_consumption_stats(self):
        """
        Obtiene estadísticas actuales del consumo de números.
        
        Returns:
            dict: Diccionario con estadísticas de consumo:
                - used: Números ya consumidos
                - total: Total de números cargados
                - remaining: Números restantes
                - percentage_used: Porcentaje de utilización
                - estimated_games_remaining: Juegos adicionales posibles
        """
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
        """
        Método principal que ejecuta toda la simulación.
        
        Proceso completo:
        1. Verificación de factibilidad
        2. Generación de equipos y jugadores
        3. Simulación de todos los juegos
        4. Análisis de resultados
        5. Cálculo de métricas de eficiencia
        6. Presentación de resultados
        
        Características:
        - Muestra progreso en tiempo real
        - Maneja errores de números agotados
        - Calcula estadísticas de rendimiento
        - Control de tiempo detallado para cada fase
        """
        
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
        
        # ===== FASE 1: GENERACIÓN DE EQUIPOS Y JUGADORES =====
        self.teams : list[Team] = self.generate_teams()
        self.players : list[Player] = []
        for team in self.teams:
            for i in range(PLAYERS_PER_TEAM):
                self.players.append(self.generate_player(team, f"Jugador {i+1} {team.name}"))
        
        setup_time = time.time() - start_time
        print(f"✅ Equipos y jugadores generados ({setup_time:.2f}s)")
        
        # ===== FASE 2: SIMULACIÓN DE JUEGOS =====
        self.games : list[Game] = []
        games_start_time = time.time()
        
        # Configurar progreso (mostrar 10 actualizaciones)
        progress_interval = max(1, GAMES_AMOUNT // 10)
        
        try:
            # Simular cada juego
            for i in range(GAMES_AMOUNT):
                rounds : list[Round] = []
                
                # Simular cada ronda del juego
                for j in range(ROUNDS_PER_GAME):
                    # Generar valores de suerte para esta ronda
                    luck_values = self.generate_players_luck_values()
                    
                    # Generar disparos y valores de resistencia
                    shots, endurance_values = self.generate_shots_and_endurance_values(luck_values, rounds)
                    
                    # Calcular ganador de la ronda
                    winner_player, winner_team = self.calculate_winner(shots)
                    
                    # Crear objeto ronda con todos los datos
                    rounds.append(Round(j+1, shots, luck_values, endurance_values, winner_player, winner_team))
                
                # Calcular ganador del juego completo
                winner_player, winner_team, luckiest_player = self.calculate_game_winner(rounds)
                
                # Crear objeto juego con todos los datos
                self.games.append(Game(i+1, rounds, winner_team, winner_player, luckiest_player))
                
                # Mostrar progreso periódicamente
                if (i + 1) % progress_interval == 0 or i == GAMES_AMOUNT - 1:
                    progress = ((i + 1) / GAMES_AMOUNT) * 100
                    stats = self.get_consumption_stats()
                    elapsed = time.time() - games_start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    
                    print(f"⏳ Progreso: {progress:5.1f}% ({i+1:,}/{GAMES_AMOUNT:,}) | "
                          f"📊 Números: {stats['used']:,} ({stats['percentage_used']:4.1f}%) | "
                          f"🚀 Velocidad: {rate:.1f} juegos/s")
                        
        except IndexError as e:
            # Manejo de error por números agotados
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
        
        # ===== FASE 3: ANÁLISIS DE RESULTADOS =====
        print(f"\n🔬 ANALIZANDO RESULTADOS...")
        analysis_start_time = time.time()
        
        # Ejecutar todos los análisis estadísticos
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
        
        # ===== FASE 4: CÁLCULO DE MÉTRICAS DE EFICIENCIA =====
        final_stats = self.get_consumption_stats()
        efficiency_metrics = self.calculate_efficiency_metrics(
            total_time, setup_time, games_generation_time, analysis_time, 
            numbers_consumed, final_stats
        )
        
        # Compilar todos los resultados
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
        
        # ===== FASE 5: PRESENTACIÓN DE RESULTADOS FINALES =====
        print(f"\n📈 RESUMEN FINAL:")
        print("="*50)
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos ({total_time/60:.1f} minutos)")
        print(f"📊 Números consumidos: {numbers_consumed:,}")
        print(f"📉 Números restantes: {final_stats['remaining']:,}")
        print(f"🎯 Promedio por juego: {numbers_consumed/GAMES_AMOUNT:.1f} números")
        print(f"🎲 Utilización total: {final_stats['percentage_used']:.2f}%")
        print(f"♻️  Juegos adicionales posibles: ~{final_stats['estimated_games_remaining']:,}")
        
        # Entregar resultados al presentador
        self.presenter.show_results(results)
        print(f"\n🎉 ¡SIMULACIÓN COMPLETADA EXITOSAMENTE!")

    # ===================================================================
    # MÉTODOS DE SIMULACIÓN - Generación de elementos del juego
    # ===================================================================

    def generate_teams(self): 
        """
        Genera los dos equipos que competirán en la simulación.
        
        Returns:
            list[Team]: Lista con exactamente 2 equipos (Team A y Team B)
        """
        team1 = Team(name="Team A")
        team2 = Team(name="Team B")
        return [team1, team2]

    def generate_player(self, team, name):
        """
        Genera un jugador con características aleatorias.
        
        Args:
            team (Team): Equipo al que pertenece el jugador
            name (str): Nombre del jugador
            
        Returns:
            Player: Jugador generado con características aleatorias
            
        Características generadas:
        - Género: 50% probabilidad de ser masculino o femenino
        - Resistencia original: Entre 25 y 45 puntos
        - Experiencia inicial: 10 puntos (valor base)
        """
        # Determinar género aleatoriamente (50/50)
        if self.get_pseudorandom_number() < 0.5:
            is_male = True
        else:
            is_male = False
            
        # Generar resistencia original entre 25 y 45
        original_endurance = int(25 + (45 - 25) * self.get_pseudorandom_number())
        
        # Experiencia inicial estándar
        experience = 10
        
        player = Player(name, team, is_male, original_endurance, experience)
        return player
    
    def generate_players_luck_values(self): 
        """
        Genera valores de suerte para todos los jugadores en una ronda.
        
        Proceso:
        1. Calcula valor de suerte para cada jugador usando distribución normal
        2. Asegura valores mínimos (no menores a 0.1)
        3. Selecciona el jugador más afortunado de cada equipo
        4. Retorna solo los 2 jugadores más afortunados (1 por equipo)
        
        Returns:
            list[LuckValue]: Lista con 2 elementos (jugador más afortunado de cada equipo)
        """
        players_luck = []
        
        # Generar valor de suerte para cada jugador
        for player in self.players:
            # Usar distribución normal (μ=1.5, σ=1.0)
            luck_value = self.generate_normal_random(1.5, 1.0)
            luck_value = max(0.1, luck_value)  # Mínimo 0.1
            players_luck.append({"value": luck_value, "player": player}) 
            
        # Separar jugadores por equipo
        team_a_players = [player for player in players_luck if player["player"].team.name == "Team A"]
        team_b_players = [player for player in players_luck if player["player"].team.name == "Team B"]
        
        # Ordenar por valor de suerte (descendente)
        team_a_players.sort(key=lambda p: p["value"], reverse=True)
        team_b_players.sort(key=lambda p: p["value"], reverse=True)
        
        # Seleccionar el más afortunado de cada equipo
        top_lucky_player_team_a = team_a_players[0] 
        top_lucky_player_team_b = team_b_players[0] 
        
        # Crear objetos LuckValue
        top_lucky_players = [
            LuckValue(top_lucky_player_team_a["player"], top_lucky_player_team_a["value"]), 
            LuckValue(top_lucky_player_team_b["player"], top_lucky_player_team_b["value"])
        ]
        return top_lucky_players
    
    def generate_normal_random(self, mu, sigma):
        """
        Genera número aleatorio con distribución normal usando algoritmo Box-Muller.
        
        Args:
            mu (float): Media de la distribución
            sigma (float): Desviación estándar
            
        Returns:
            float: Número con distribución normal
            
        Implementa Box-Muller para convertir números uniformes en normales:
        - Consume 2 números pseudoaleatorios del CSV
        - Aplica transformación matemática
        - Previene valores extremos (log(0))
        """
        # Obtener dos números uniformes del CSV
        u1 = self.get_pseudorandom_number()
        u2 = self.get_pseudorandom_number()
        
        # Prevenir log(0) y valores extremos
        u1 = max(1e-10, min(1 - 1e-10, u1))
        u2 = max(1e-10, min(1 - 1e-10, u2))
        
        # Aplicar transformación Box-Muller
        z0 = (-2 * math.log(u1))**0.5 * math.cos(2 * math.pi * u2)
        return mu + sigma * z0
   
    def generate_shots_and_endurance_values(self, luck_values: list[LuckValue], rounds: list[Round]):
        """
        Genera todos los disparos y valores de resistencia para una ronda.
        
        Args:
            luck_values (list[LuckValue]): Jugadores más afortunados de la ronda
            rounds (list[Round]): Rondas anteriores del juego
            
        Returns:
            tuple: (shots, endurance_values)
                - shots: Lista de todos los disparos realizados
                - endurance_values: Lista de resistencia de cada jugador
                
        Tipos de disparos generados:
        1. NS (Normal Shot): Disparos regulares basados en resistencia
        2. LS (Lucky Shot): Disparos extra para jugadores afortunados
        3. AS (Advantage Shot): Disparos por racha de suerte (3 rondas consecutivas)
        4. ES (Extra Shot): Disparos de desempate cuando hay empates
        
        Proceso complejo:
        1. Calcula resistencia actual de cada jugador
        2. Genera disparos normales basados en resistencia
        3. Añade disparos especiales por suerte
        4. Añade disparos por racha de suerte
        5. Resuelve empates con disparos adicionales
        """
        shots: list[Shot] = []
        endurance_values: list[EnduranceValue] = []
        points_total_rd = []
        
        # ===== FASE 1: DISPAROS NORMALES BASADOS EN RESISTENCIA =====
        for player in self.players:
            # Calcular resistencia actual del jugador
            endurance = self.generatePlayer_endurance(player, rounds)
            current_endurance = endurance.value
            pts = { "player": player, "points": 0 }
            
            # Realizar disparos mientras tenga resistencia (cada disparo cuesta 5)
            while current_endurance >= 5:
                shot = self.do_shot(player, len(shots) + 1)  # Disparo normal (NS)
                shots.append(shot)
                current_endurance -= 5
                player.total_points += shot.score
                pts["points"] += shot.score
                
            endurance_values.append(endurance)
            points_total_rd.append(pts)
        
        # ===== FASE 2: DISPAROS ESPECIALES POR SUERTE (LS) =====
        # Identificar jugadores que reciben disparos de suerte
        luckiest_players = [player for player in self.players if player.name == luck_values[0].player.name 
                            or player.name == luck_values[1].player.name]
        
        # ===== FASE 3: DISPAROS POR RACHA DE SUERTE (AS) =====
        # Verificar rachas de suerte en las últimas 3 rondas
        if len(rounds) >= 3:
            names_list = []
            # Revisar últimas 3 rondas
            for round in list(filter(lambda value: (len(rounds) + 1) - value.round_number <= 3, rounds)):
                lvs = round.luck_values
                names_list.extend([lv.player.name for lv in lvs])
                
            # Encontrar jugadores con suerte en las 3 rondas
            for name in set(names_list):
                if len(list(filter(lambda name_l: name_l == name, names_list))) == 3:
                    luckiest_players.append(list(filter(lambda player: player.name == name, self.players))[0])
        
        # Realizar disparos especiales para jugadores afortunados
        for player in luckiest_players:
            shot = self.do_shot(player, len(shots) + 1, "LS")  # Lucky Shot
            shots.append(shot)
            player.total_points += shot.score
        
        # ===== FASE 4: DISPAROS POR VENTAJA CONSECUTIVA (AS) =====
        # Verificar jugadores con suerte en las últimas 2 rondas
        if len(rounds) >= 2:
            last_two_rounds = rounds[-2:]
            for player in self.players:
                has_special_shots_consecutive = True
                
                # Verificar si tuvo suerte en ambas rondas
                for round_check in last_two_rounds:
                    player_in_luck = any(lv.player.name == player.name for lv in round_check.luck_values)
                    if not player_in_luck:
                        has_special_shots_consecutive = False
                        break
                
                # Si tuvo suerte consecutiva, recibe disparo de ventaja
                if has_special_shots_consecutive:
                    shot = self.do_shot(player, len(shots) + 1, "AS")  # Advantage Shot
                    shots.append(shot)
                    player.total_points += shot.score
        
        # ===== FASE 5: DISPAROS DE DESEMPATE (ES) =====
        # Encontrar puntuación máxima de la ronda
        max_pts = max([pts["points"] for pts in points_total_rd])
        max_pst_list = list(filter(lambda pts: pts["points"] == max_pts, points_total_rd))
        
        # Si hay empate, realizar disparos de desempate hasta resolverlo
        if len(max_pst_list) > 1:
            while len(set([pts["points"] for pts in max_pst_list])) != len(max_pst_list):
                for stl in max_pst_list:
                    player = stl["player"]
                    shot = self.do_shot(player, len(shots) + 1, "ES")  # Extra Shot (desempate)
                    shots.append(shot)
                    player.total_points += shot.score
                    stl["points"] += shot.score
                    
        return shots, endurance_values

    def do_shot(self, player: Player, n_shot: int, type = "NS"):
        """
        Realiza un disparo individual para un jugador.
        
        Args:
            player (Player): Jugador que realiza el disparo
            n_shot (int): Número secuencial del disparo
            type (str): Tipo de disparo ("NS", "LS", "AS", "ES")
            
        Returns:
            Shot: Objeto disparo con puntuación calculada
            
        Tipos de disparo:
        - NS (Normal Shot): Disparo regular
        - LS (Lucky Shot): Disparo por suerte
        - AS (Advantage Shot): Disparo por racha
        - ES (Extra Shot): Disparo de desempate
        """
        # Obtener número pseudoaleatorio para el disparo
        num = self.get_pseudorandom_number()
        
        # Calcular puntuación según el género del jugador
        if player.is_male:
            score = self.calculate_score_male(num)
        else:
            score = self.calculate_score_female(num)
            
        return Shot(player, score, n_shot, type)
    
    def generatePlayer_endurance(self, player: Player, rounds: list[Round]):
        """
        Calcula la resistencia actual de un jugador basada en rondas anteriores.
        
        Args:
            player (Player): Jugador para calcular resistencia
            rounds (list[Round]): Lista de rondas anteriores del juego actual
            
        Returns:
            EnduranceValue: Objeto con la resistencia calculada para el jugador
            
        Lógica de resistencia:
        - Primera ronda: Usa resistencia original
        - Jugadores expertos (exp >= 19): Solo pierden 1 punto por ronda
        - Jugadores normales: Recuperan resistencia con reducción aleatoria
        
        Fórmula de recuperación:
        resistencia_nueva = resistencia_anterior + (resistencia_gastada - reducción_aleatoria)
        """
        if not rounds:
            # Primera ronda: usar resistencia original
            endurance = player.original_endurance
        else:
            # Obtener resistencia de la última ronda
            last_endurance = list(filter(lambda value:value.player.name == player.name, 
                                            rounds[len(rounds) - 1].endurance_values))[0]
            
            # Calcular resistencia gastada en la ronda anterior
            if len(rounds) == 1:
                # Segunda ronda: comparar con resistencia original
                endurance_spent = player.original_endurance - last_endurance.value
            else:
                # Rondas posteriores: comparar con ronda anterior
                previous_endurance = list(filter(lambda value:value.player.name == player.name, 
                                            rounds[len(rounds) - 2].endurance_values))[0]
                endurance_spent = previous_endurance.value - last_endurance.value
            
            # Aplicar reglas de experiencia
            if player.experience >= 19:
                # Jugadores muy experimentados: pérdida mínima
                endurance = player.original_endurance - 1
            else:
                # Jugadores normales: recuperación con reducción aleatoria
                random_reduction = self.get_random_reduction()
                recovery = max(0, endurance_spent - random_reduction)
                endurance = last_endurance.value + recovery
                
        return EnduranceValue(player, max(0, endurance))
    
    def get_random_reduction(self):
        """
        Genera una reducción aleatoria para la recuperación de resistencia.
        
        Returns:
            int: Valor de reducción (1, 2 o 3) con probabilidades iguales
            
        Distribución:
        - 33.33% probabilidad de reducción 1
        - 33.33% probabilidad de reducción 2  
        - 33.33% probabilidad de reducción 3
        """
        rand = self.get_pseudorandom_number()
        if rand < 0.33:
            return 1
        elif rand < 0.66:
            return 2
        else:
            return 3

    def calculate_score_male(self, score):
        """
        Calcula la puntuación de un disparo para jugadores masculinos.
        
        Args:
            score (float): Número aleatorio entre 0 y 1
            
        Returns:
            int: Puntuación del disparo (0, 8, 9 o 10)
            
        Distribución de probabilidades para hombres:
        - 15% probabilidad de 10 puntos (excelente)
        - 30% probabilidad de 9 puntos (bueno) 
        - 47% probabilidad de 8 puntos (regular)
        - 8% probabilidad de 0 puntos (fallo)
        """
        if score <= 0.15:
            return 10
        elif score <= 0.45:
            return 9
        elif score <= 0.92:
            return 8
        else:
            return 0
        
    def calculate_score_female(self, score):
        """
        Calcula la puntuación de un disparo para jugadoras femeninas.
        
        Args:
            score (float): Número aleatorio entre 0 y 1
            
        Returns:
            int: Puntuación del disparo (0, 8, 9 o 10)
            
        Distribución de probabilidades para mujeres (más favorable):
        - 25% probabilidad de 10 puntos (excelente)
        - 40% probabilidad de 9 puntos (bueno)
        - 30% probabilidad de 8 puntos (regular) 
        - 5% probabilidad de 0 puntos (fallo)
        """
        if score <= 0.25:
            return 10
        elif score <= 0.65:
            return 9
        elif score <= 0.95:
            return 8
        else:
            return 0

    def calculate_winner(self, shots:list[Shot]):
        """
        Calcula los ganadores de una ronda específica.
        
        Args:
            shots (list[Shot]): Todos los disparos realizados en la ronda
            
        Returns:
            tuple: (winner_player, winner_team)
                - winner_player: Jugador con más puntos individuales
                - winner_team: Equipo con más puntos totales (None si empate)
                
        Proceso:
        1. Suma puntos por equipo (solo disparos NS, LS, AS cuentan para equipos)
        2. Suma puntos por jugador (todos los disparos cuentan excepto LS para individual)
        3. Determina ganador individual y de equipo
        4. Otorga 3 puntos de experiencia al ganador individual
        """
        # Inicializar contadores
        points_total_rd = [{"player":player, "points": 0} for player in self.players]
        team_a_points = 0
        team_b_points = 0
        
        # Procesar cada disparo
        for shot in shots:
            # Puntos para equipos (solo ciertos tipos de disparo)
            if shot.player.team.name == "Team A" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                team_a_points += shot.score
            if shot.player.team.name == "Team B" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                team_b_points += shot.score
                
            # Puntos individuales (excluye LS para conteo individual)
            if shot.type == "NS" or shot.type == "ES" or shot.type == "AS":
                points_total_rd[self.players.index(shot.player)]["points"] += shot.score
        
        # Determinar ganador individual (mayor puntuación individual)
        max_individual_points = max([pts["points"] for pts in points_total_rd])
        winner_player = list(filter(lambda value: value["points"] == max_individual_points, points_total_rd))[0]["player"]
        
        # Determinar ganador por equipos
        winner_team = None
        if team_a_points != team_b_points:
            max_tm_name = "Team A" if team_a_points > team_b_points else "Team B"
            winner_team = list(filter(lambda tm: tm.name == max_tm_name, self.teams))[0]
        
        # Otorgar experiencia al ganador individual
        list(filter(lambda player: player.name == winner_player.name, self.players))[0].experience += 3
        
        return winner_player, winner_team

    def calculate_game_winner(self, rounds:list[Round]):
        """
        Calcula los ganadores de un juego completo basado en todas las rondas.
        
        Args:
            rounds (list[Round]): Todas las rondas del juego
            
        Returns:
            tuple: (winner_player, winner_team, luckiest_player)
                - winner_player: Jugador que ganó más rondas individuales
                - winner_team: Equipo con más puntos totales del juego
                - luckiest_player: Jugador que fue más veces afortunado
                
        Proceso:
        1. Suma puntos totales por equipo en todo el juego
        2. Cuenta victorias por ronda para cada jugador
        3. Cuenta apariciones como jugador afortunado
        4. Determina ganadores por cada categoría
        """
        # Calcular puntos totales por equipo
        team_a_points = 0
        team_b_points = 0
        
        for round in rounds:
            for shot in round.shots:
                if shot.player.team.name == "Team A" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                    team_a_points += shot.score
                if shot.player.team.name == "Team B" and (shot.type == "NS" or shot.type == "LS" or shot.type == "AS"):
                    team_b_points += shot.score
        
        # Determinar equipo ganador
        max_tm_name = "Team A" if team_a_points > team_b_points else "Team B"
        winner_team = list(filter(lambda tm: tm.name == max_tm_name, self.teams))[0]
        
        # Contar victorias por ronda y apariciones como afortunado
        rds_winners = []  # Ganadores por ronda
        lks_winners = []  # Apariciones como afortunado
        
        for round in rounds:
            # Procesar valores de suerte
            for luck_value in round.luck_values:
                if luck_value.player.name in [lk_w['player'].name for lk_w in lks_winners]:
                    list(filter(lambda lk_w: lk_w['player'].name == luck_value.player.name, lks_winners))[0]['amount'] += 1
                else:
                    lks_winners.append({"player": luck_value.player, "amount": 1})
            
            # Procesar ganadores de ronda
            if round.winner_player.name in [rd_w['player'].name for rd_w in rds_winners]:
                list(filter(lambda rd_w: rd_w['player'].name == round.winner_player.name, rds_winners))[0]['amount'] += 1
            else:
                rds_winners.append({"player": round.winner_player, "amount": 1})
        
        # Determinar jugador que ganó más rondas
        max_round_wins = max([rd_w['amount'] for rd_w in rds_winners])
        winner_player = list(filter(lambda rd_w: rd_w['amount'] == max_round_wins, rds_winners))[0]['player']
        
        # Determinar jugador más afortunado
        max_luck_appearances = max([lk_w['amount'] for lk_w in lks_winners])
        luckiest_player = list(filter(lambda lk_w: lk_w['amount'] == max_luck_appearances, lks_winners))[0]['player']
        
        return winner_player, winner_team, luckiest_player

    # ===================================================================
    # MÉTODOS DE ANÁLISIS ESTADÍSTICO - Procesan resultados finales
    # ===================================================================

    def calculate_luckiest_player_per_games(self):
        """
        Identifica al jugador más afortunado a lo largo de todos los juegos.
        
        Returns:
            dict: Diccionario con jugador más afortunado y cantidad de veces
                - player: Objeto Player más afortunado
                - amount_luck: Número de juegos donde fue el más afortunado
        """
        luck_counts = {}
        
        # Contar apariciones como jugador más afortunado por juego
        for game in self.games:
            luckiest_player = game.luckiest_player
            if luck_counts.get(luckiest_player) == None:
                luck_counts[luckiest_player] = 0
            luck_counts[luckiest_player] += 1
            
        # Encontrar el máximo
        luckiest_player_overall = max(luck_counts, key=luck_counts.get)
        
        return {
            "player": luckiest_player_overall,
            "amount_luck": luck_counts[luckiest_player_overall]
        }

    def calculate_more_experienced_player(self):
        """
        Identifica al jugador con mayor experiencia acumulada.
        
        Returns:
            dict: Diccionario con jugador más experimentado
                - player: Objeto Player con mayor experiencia
                - amount_experienced: Puntos de experiencia totales
                
        La experiencia se gana:
        - Base: 10 puntos iniciales
        - +3 puntos por cada ronda ganada individualmente
        """
        most_experienced_player = max(self.players, key=lambda player: player.experience)
        
        return {
            "player": most_experienced_player,
            "amount_experienced": most_experienced_player.experience
        }

    def calculate_team_winner(self):
        """
        Determina el equipo ganador general y estadísticas de sus jugadores.
        
        Returns:
            dict: Información del equipo ganador
                - team: Objeto Team ganador
                - player_points: Lista con puntos totales de cada jugador del equipo
                
        Lógica:
        - Cuenta victorias por juego de cada equipo
        - El equipo con más juegos ganados es el ganador general
        - Incluye puntos totales acumulados por jugadores del equipo ganador
        """
        count_wins_team_a = 0
        count_wins_team_b = 0
        
        # Contar victorias por juego
        for game in self.games:
            count_wins_team_a += game.winner_team.name == 'Team A'
            count_wins_team_b += game.winner_team.name  == 'Team B'
        
        # Determinar equipo ganador
        if count_wins_team_a > count_wins_team_b:
            final_winner_team = self.teams[0]  # Team A
        else: 
            final_winner_team = self.teams[1]  # Team B
        
        # Recopilar puntos de jugadores del equipo ganador
        final_players_win_points = []
        for player in self.players:
            if player.team.name == final_winner_team.name:
                final_players_win_points.append({"player":player.name, "points":player.total_points})
        
        return {
            "team": final_winner_team, 
            "player_points": final_players_win_points
        }

    def calculate_winner_gender_per_game(self):
        """
        Analiza qué género gana más juegos individuales.
        
        Returns:
            dict: Estadísticas de género ganador por juegos
                - gender: Género que más juegos ganó ("Hombres" o "Mujeres")
                - amount_wins: Cantidad de juegos ganados por ese género
                
        Cuenta el género del jugador que ganó cada juego individual
        (no por equipos, sino por mejor jugador individual del juego).
        """
        count_wins_male = 0
        count_wins_female = 0
        
        # Contar por género del ganador de cada juego
        for game in self.games:
            if game.winner_player.is_male:
                count_wins_male += 1
            else:
                count_wins_female +=1
        
        # Determinar género ganador
        if count_wins_male > count_wins_female:
            gender_win = 'Hombres'
            count_win = count_wins_male
        else:
            gender_win = 'Mujeres'
            count_win = count_wins_female
            
        return {
            "gender": gender_win, 
            "amount_wins": count_win
        }

    def calculate_winner_gender_total(self):
        """
        Analiza qué género gana más rondas individuales en total.
        
        Returns:
            dict: Estadísticas de género ganador por rondas totales
                - gender: Género que más rondas ganó ("Hombres" o "Mujeres")
                - total_rounds_won: Total de rondas ganadas por ese género
                
        Diferencia con método anterior:
        - Este cuenta TODAS las rondas individuales
        - El anterior solo contaba juegos completos
        """
        male_wins = 0
        female_wins = 0
        
        # Contar todas las victorias de ronda por género
        for game in self.games:
            for round_game in game.rounds:
                winner_player = round_game.winner_player
                if winner_player.is_male:
                    male_wins += 1
                else:
                    female_wins += 1
        
        # Determinar género ganador
        winner_gender = "Hombres" if male_wins > female_wins else "Mujeres"
        
        return {
            "gender": winner_gender,
            "total_rounds_won": max(male_wins, female_wins)
        }

    def calculate_points_vs_games_per_player(self):
        """
        Calcula la progresión de puntos por juego para cada jugador.
        
        Returns:
            list: Lista de jugadores con su historial de puntos por juego
                Cada elemento contiene:
                - player: Objeto Player
                - points: Lista con puntos obtenidos en cada juego
                
        Útil para:
        - Análizar evolución del rendimiento
        - Identificar patrones de mejora o declive
        - Crear gráficas de rendimiento temporal
        """
        players_with_points = [{"player": player, "points": []} for player in self.players]
        
        # Procesar cada juego
        for game in self.games:
            # Inicializar puntos por jugador para este juego
            game_points = {player.name: 0 for player in self.players}
            
            # Sumar puntos de todas las rondas del juego
            for round_game in game.rounds:
                for shot in round_game.shots:
                    game_points[shot.player.name] += shot.score
            
            # Agregar puntos del juego al historial de cada jugador
            for player_points in players_with_points:
                player_name = player_points["player"].name
                player_points["points"].append(game_points.get(player_name, 0))
        
        return players_with_points

    def calculate_team_score_distribution(self):
        """
        Calcula estadísticas de distribución de puntuaciones por equipo.
        
        Returns:
            dict: Estadísticas completas de ambos equipos
                Para cada equipo incluye:
                - name: Nombre del equipo
                - average_score: Puntuación promedio por juego
                - variance: Varianza de las puntuaciones
                - std_deviation: Desviación estándar
                - scores: Lista completa de puntuaciones por juego
                
        Métricas estadísticas importantes:
        - Promedio: Rendimiento típico del equipo
        - Varianza: Qué tan dispersas están las puntuaciones
        - Desv. estándar: Consistencia del rendimiento
        """
        team_a_scores = []
        team_b_scores = []
        
        # Calcular puntuación por equipo en cada juego
        for game in self.games:
            team_a_game_score = 0
            team_b_game_score = 0
            
            # Sumar puntos de todos los disparos válidos para equipos
            for round_game in game.rounds:
                for shot in round_game.shots:
                    if shot.player.team.name == "Team A" and shot.type in ["NS", "LS", "AS"]:
                        team_a_game_score += shot.score
                    elif shot.player.team.name == "Team B" and shot.type in ["NS", "LS", "AS"]:
                        team_b_game_score += shot.score
            
            team_a_scores.append(team_a_game_score)
            team_b_scores.append(team_b_game_score)
        
        # Calcular estadísticas para Team A
        team_a_avg = sum(team_a_scores) / len(team_a_scores)
        team_a_variance = sum((score - team_a_avg) ** 2 for score in team_a_scores) / len(team_a_scores)
        team_a_std = team_a_variance ** 0.5
        
        # Calcular estadísticas para Team B
        team_b_avg = sum(team_b_scores) / len(team_b_scores)
        team_b_variance = sum((score - team_b_avg) ** 2 for score in team_b_scores) / len(team_b_scores)
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
        """
        Analiza el uso y efectividad de disparos especiales por equipo.
        
        Returns:
            dict: Análisis de disparos especiales para ambos equipos
                Para cada equipo incluye:
                - name: Nombre del equipo
                - total_special_shots: Total de disparos LS y AS realizados
                - avg_special_shots_per_game: Promedio de disparos especiales por juego
                - experience_gained: Experiencia total ganada por el equipo
                - correlation_factor: Factor de correlación entre disparos y experiencia
                
        Disparos especiales analizados:
        - LS (Lucky Shot): Por ser jugador afortunado
        - AS (Advantage Shot): Por racha de suerte consecutiva
        
        Útil para evaluar:
        - Ventajas estratégicas por suerte
        - Relación entre suerte y experiencia ganada
        """
        team_a_special_shots = 0
        team_b_special_shots = 0
        
        # Contar disparos especiales por equipo
        for game in self.games:
            for round_game in game.rounds:
                for shot in round_game.shots:
                    if shot.type in ["LS", "AS"]:
                        if shot.player.team.name == "Team A":
                            team_a_special_shots += 1
                        else:
                            team_b_special_shots += 1
        
        # Calcular promedios
        team_a_avg_special = team_a_special_shots / GAMES_AMOUNT
        team_b_avg_special = team_b_special_shots / GAMES_AMOUNT
        
        # Calcular experiencia ganada (inicial era 10, resto es ganancia)
        team_a_players = [p for p in self.players if p.team.name == "Team A"]
        team_b_players = [p for p in self.players if p.team.name == "Team B"]
        
        team_a_experience_gained = sum(p.experience - 10 for p in team_a_players)
        team_b_experience_gained = sum(p.experience - 10 for p in team_b_players)
        
        # Calcular factor de correlación (métrica personalizada)
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
        """
        Analiza la frecuencia de rondas empatadas en la simulación.
        
        Returns:
            dict: Estadísticas de empates
                - tied_rounds_count: Número total de rondas empatadas
                - total_rounds: Total de rondas simuladas
                - tied_frequency_percent: Porcentaje de rondas empatadas
                - non_tied_rounds: Número de rondas no empatadas
                - non_tied_frequency_percent: Porcentaje de rondas decididas
                
        Una ronda está empatada cuando winner_team es None
        (ambos equipos obtuvieron la misma puntuación).
        
        Útil para:
        - Evaluar balance del sistema de puntuación
        - Analizar efectividad del sistema de desempate
        """
        tied_rounds_count = 0
        total_rounds = GAMES_AMOUNT * ROUNDS_PER_GAME
        
        # Contar rondas empatadas
        for game in self.games:
            for round_game in game.rounds:
                if round_game.winner_team is None:  # Empate
                    tied_rounds_count += 1
        
        # Calcular frecuencias
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
        """
        Calcula métricas completas de eficiencia y rendimiento de la simulación.
        
        Args:
            total_time (float): Tiempo total de ejecución
            setup_time (float): Tiempo de configuración inicial
            games_generation_time (float): Tiempo de generación de juegos
            analysis_time (float): Tiempo de análisis de resultados
            numbers_consumed (int): Números del CSV consumidos
            consumption_stats (dict): Estadísticas de consumo del CSV
            
        Returns:
            dict: Métricas completas organizadas en categorías:
                - timing: Tiempos de cada fase
                - time_distribution: Distribución porcentual del tiempo
                - processing_rates: Velocidades de procesamiento
                - data_volume: Volúmenes de datos procesados
                - numbers_efficiency: Eficiencia en el uso de números del CSV
                - memory_efficiency: Uso de memoria
                - csv_performance: Rendimiento específico del CSV
                - system_performance: Evaluación general del sistema
                
        Métricas clave calculadas:
        - Juegos/segundo, rondas/segundo, disparos/segundo
        - Números consumidos por juego/ronda/disparo
        - Eficiencia de utilización del CSV
        - Evaluación cualitativa del rendimiento
        """
        # Calcular volúmenes de datos procesados
        total_shots = sum(len(round.shots) for game in self.games for round in game.rounds)
        total_rounds = len(self.games) * ROUNDS_PER_GAME
        total_luck_calculations = total_rounds * 2  # 2 jugadores afortunados por ronda
        
        # Calcular velocidades de procesamiento
        games_per_second = GAMES_AMOUNT / games_generation_time if games_generation_time > 0 else 0
        rounds_per_second = total_rounds / games_generation_time if games_generation_time > 0 else 0
        shots_per_second = total_shots / games_generation_time if games_generation_time > 0 else 0
        numbers_per_second = numbers_consumed / games_generation_time if games_generation_time > 0 else 0
        
        # Calcular distribución de tiempo
        setup_percentage = (setup_time / total_time) * 100
        games_percentage = (games_generation_time / total_time) * 100
        analysis_percentage = (analysis_time / total_time) * 100
        
        # Métricas de eficiencia de números
        numbers_efficiency = {
            "numbers_consumed": numbers_consumed,
            "numbers_remaining": consumption_stats['remaining'],
            "consumption_percentage": consumption_stats['percentage_used'],
            "numbers_per_game": numbers_consumed / GAMES_AMOUNT if GAMES_AMOUNT > 0 else 0,
            "numbers_per_round": numbers_consumed / total_rounds if total_rounds > 0 else 0,
            "numbers_per_shot": numbers_consumed / total_shots if total_shots > 0 else 0,
            "csv_utilization_efficiency": "Excellent" if consumption_stats['percentage_used'] < 25 else "Good" if consumption_stats['percentage_used'] < 50 else "Fair"
        }
        
        # Métricas de eficiencia de memoria
        memory_efficiency = {
            "total_games_stored": len(self.games),
            "total_rounds_stored": total_rounds,
            "total_shots_stored": total_shots,
            "average_shots_per_round": total_shots / total_rounds if total_rounds > 0 else 0,
            "csv_memory_footprint": f"{len(self.numbers) * 8 // 1024 // 1024} MB"  # Aproximado para floats
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