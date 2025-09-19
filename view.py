from intefaces import IView, IPresenter, IModel
from model import Model
from presenter import Presenter
import tkinter as tk
import threading
import matplotlib.pyplot as plt

class LoadingCircle:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.canvas = tk.Canvas(root, width=100, height=100)
        self.canvas.pack(expand=True, fill=tk.BOTH, pady=20)
        self.arc = None
        self.angle = 0
        self.canvas.bind("<Configure>", self.update_arc_position)
        self.animate()

    def update_arc_position(self, event=None):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        size = 0.8 * min(canvas_width, canvas_height)
        x0 = (canvas_width - size) / 2
        y0 = (canvas_height - size) / 2
        x1 = x0 + size
        y1 = y0 + size
        if self.arc:
            self.canvas.delete(self.arc)
        self.arc = self.canvas.create_arc(
            x0, y0, x1, y1,
            start=self.angle,
            extent=210,
            style=tk.ARC,
            outline="#3498db",
            width=min(canvas_width, canvas_height)*0.1
        )

    def animate(self):
        self.angle = (self.angle + 10) % 360
        self.canvas.itemconfig(self.arc, start=self.angle)
        def update():
            if self.root.winfo_exists():
                try:
                    self.animate()
                except tk.TclError:
                    pass
        self.root.after(50, update)

class View(tk.Tk, IView):
    def __init__(self):
        super().__init__()
        self.presenter : IPresenter = None
        self.load_frame = None
        self.title("Simulador de Juegos de Arquería")
        self.geometry("1000x700")
        self.configure(bg="#f0f0f0")
        self.update_idletasks()
        self.geometry("+{}+{}".format(int(self.winfo_screenwidth()/2 - self.winfo_width()/2), int(self.winfo_screenheight()/2 - self.winfo_height()/2)))
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.label = tk.Label(self.main_frame, text="Simulador de juegos de arqueria")
        self.label.config(font=("Arial", 20))
        self.label.pack(pady=10)
        def on_start():
            self.show_load_frame()
            threading.Thread(target=self.presenter.start_simulation, daemon=True).start()
        tk.Button(self.main_frame, text="Iniciar Simulación", command=on_start).pack(pady=10)

    def show_load_frame(self):
        self.main_frame.pack_forget()
        self.create_load_frame()
        self.load_frame.pack(fill=tk.BOTH, expand=True)

    def create_load_frame(self):
        self.load_frame = tk.Frame(self)
        self.load_frame.pack(fill=tk.BOTH, expand=True)
        LoadingCircle(self.load_frame)
        self.load_label = tk.Label(self.load_frame, text="Cargando simulacion...")
        self.load_label.config(font=("Arial", 20))
        self.load_label.pack(fill=tk.X, expand=True)

    def set_presenter(self, presenter):
        self.presenter = presenter

    def show_results(self, results):
        results_frame = tk.Frame(self)
        canvas = tk.Canvas(results_frame)
        scrollbar = tk.Scrollbar(results_frame, orient=tk.VERTICAL, command=canvas.yview, width=10)
        scrollable_frame = tk.Frame(canvas, border=2, relief="sunken")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.winfo_width() - 10)
        
        # Título principal
        tk.Label(scrollable_frame, text="Resultados de la Simulación", font=("Arial", 20, "bold")).pack(pady=15)
        
        # Métricas básicas
        basic_frame = tk.LabelFrame(scrollable_frame, text="Métricas Básicas", font=("Arial", 14, "bold"))
        basic_frame.pack(fill=tk.X, padx=10, pady=10)
        
        grid_frame = tk.Frame(basic_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(grid_frame, text="Jugador con más suerte por juego:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=(0,10))
        tk.Label(grid_frame, text=f"{results['luckiest_player_per_game']['player'].name} - {results['luckiest_player_per_game']['amount_luck']} veces", 
                 font=("Arial", 12)).grid(row=0, column=1, sticky="w")
        
        tk.Label(grid_frame, text="Jugador con más experiencia:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=(0,10))
        tk.Label(grid_frame, text=f"{results['more_experienced_player']['player'].name} - {results['more_experienced_player']['amount_experienced']} puntos", 
                 font=("Arial", 12)).grid(row=1, column=1, sticky="w")
        
        tk.Label(grid_frame, text="Género más ganador por juego:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=(0,10))
        tk.Label(grid_frame, text=f"{results['winner_gender_per_game']['gender']} - {results['winner_gender_per_game']['amount_wins']} veces", 
                 font=("Arial", 12)).grid(row=2, column=1, sticky="w")
        
        tk.Label(grid_frame, text="Género más ganador en total:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=(0,10))
        tk.Label(grid_frame, text=f"{results['winner_gender_total']['gender']} - {results['winner_gender_total']['total_rounds_won']} rondas", 
                 font=("Arial", 12)).grid(row=3, column=1, sticky="w")

        # Equipo ganador
        team_frame = tk.LabelFrame(scrollable_frame, text="Equipo Ganador", font=("Arial", 14, "bold"))
        team_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(team_frame, text=f"Equipo ganador: {results['winner_team_total']['team'].name}", 
                 font=("Arial", 13, "bold")).pack(pady=5)
        
        for player_points in results['winner_team_total']['player_points']:
            tk.Label(team_frame, text=f"• {player_points['player']} - {player_points['points']} puntos", 
                     font=("Arial", 11)).pack(pady=2)

        # Distribución de puntajes por equipo
        distribution_frame = tk.LabelFrame(scrollable_frame, text="Distribución de Puntajes por Equipo", font=("Arial", 14, "bold"))
        distribution_frame.pack(fill=tk.X, padx=10, pady=10)
        
        dist_grid = tk.Frame(distribution_frame)
        dist_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Encabezados
        tk.Label(dist_grid, text="Equipo", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        tk.Label(dist_grid, text="Promedio", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=2)
        tk.Label(dist_grid, text="Varianza", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=2)
        tk.Label(dist_grid, text="Desv. Estándar", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=2)
        tk.Label(dist_grid, text="Ver Dispersión", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5, pady=2)
        
        # Team A
        team_a_data = results['team_score_distribution']['team_a']
        tk.Label(dist_grid, text=team_a_data['name'], font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        tk.Label(dist_grid, text=f"{team_a_data['average_score']}", font=("Arial", 11)).grid(row=1, column=1, padx=5, pady=2)
        tk.Label(dist_grid, text=f"{team_a_data['variance']}", font=("Arial", 11)).grid(row=1, column=2, padx=5, pady=2)
        tk.Label(dist_grid, text=f"{team_a_data['std_deviation']}", font=("Arial", 11)).grid(row=1, column=3, padx=5, pady=2)
        tk.Button(dist_grid, text="Gráfica", font=("Arial", 10), 
                 command=lambda: self.show_dispersion_analysis(team_a_data)).grid(row=1, column=4, padx=5, pady=2)
        
        # Team B
        team_b_data = results['team_score_distribution']['team_b']
        tk.Label(dist_grid, text=team_b_data['name'], font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        tk.Label(dist_grid, text=f"{team_b_data['average_score']}", font=("Arial", 11)).grid(row=2, column=1, padx=5, pady=2)
        tk.Label(dist_grid, text=f"{team_b_data['variance']}", font=("Arial", 11)).grid(row=2, column=2, padx=5, pady=2)
        tk.Label(dist_grid, text=f"{team_b_data['std_deviation']}", font=("Arial", 11)).grid(row=2, column=3, padx=5, pady=2)
        tk.Button(dist_grid, text="Gráfica", font=("Arial", 10), 
                 command=lambda: self.show_dispersion_analysis(team_b_data)).grid(row=2, column=4, padx=5, pady=2)
        
        # Botón para comparación de ambos equipos
        tk.Button(distribution_frame, text="Ver Comparación de Dispersión de Ambos Equipos", font=("Arial", 12), 
                 command=lambda: self.show_combined_dispersion_analysis(results['team_score_distribution'])).pack(pady=10)

        # Análisis de lanzamientos especiales
        special_frame = tk.LabelFrame(scrollable_frame, text="Análisis de Lanzamientos Especiales", font=("Arial", 14, "bold"))
        special_frame.pack(fill=tk.X, padx=10, pady=10)
        
        special_grid = tk.Frame(special_frame)
        special_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Encabezados
        tk.Label(special_grid, text="Equipo", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        tk.Label(special_grid, text="Total Especiales", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=2)
        tk.Label(special_grid, text="Promedio/Juego", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=5, pady=2)
        tk.Label(special_grid, text="Experiencia Ganada", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5, pady=2)
        tk.Label(special_grid, text="Factor Correlación", font=("Arial", 12, "bold")).grid(row=0, column=4, padx=5, pady=2)
        
        # Team A
        special_a = results['special_shots_analysis']['team_a']
        tk.Label(special_grid, text=special_a['name'], font=("Arial", 11)).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        tk.Label(special_grid, text=f"{special_a['total_special_shots']}", font=("Arial", 11)).grid(row=1, column=1, padx=5, pady=2)
        tk.Label(special_grid, text=f"{special_a['avg_special_shots_per_game']}", font=("Arial", 11)).grid(row=1, column=2, padx=5, pady=2)
        tk.Label(special_grid, text=f"{special_a['experience_gained']}", font=("Arial", 11)).grid(row=1, column=3, padx=5, pady=2)
        tk.Label(special_grid, text=f"{special_a['correlation_factor']}", font=("Arial", 11)).grid(row=1, column=4, padx=5, pady=2)
        
        # Team B
        special_b = results['special_shots_analysis']['team_b']
        tk.Label(special_grid, text=special_b['name'], font=("Arial", 11)).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        tk.Label(special_grid, text=f"{special_b['total_special_shots']}", font=("Arial", 11)).grid(row=2, column=1, padx=5, pady=2)
        tk.Label(special_grid, text=f"{special_b['avg_special_shots_per_game']}", font=("Arial", 11)).grid(row=2, column=2, padx=5, pady=2)
        tk.Label(special_grid, text=f"{special_b['experience_gained']}", font=("Arial", 11)).grid(row=2, column=3, padx=5, pady=2)
        tk.Label(special_grid, text=f"{special_b['correlation_factor']}", font=("Arial", 11)).grid(row=2, column=4, padx=5, pady=2)

        # Análisis de rondas empatadas
        tied_frame = tk.LabelFrame(scrollable_frame, text="Análisis de Rondas Empatadas", font=("Arial", 14, "bold"))
        tied_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tied_data = results['tied_rounds_analysis']
        tied_info_frame = tk.Frame(tied_frame)
        tied_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(tied_info_frame, text=f"Total de rondas jugadas: {tied_data['total_rounds']}", 
                 font=("Arial", 12)).pack(anchor="w", pady=2)
        tk.Label(tied_info_frame, text=f"Rondas empatadas: {tied_data['tied_rounds_count']} ({tied_data['tied_frequency_percent']}%)", 
                 font=("Arial", 12)).pack(anchor="w", pady=2)
        tk.Label(tied_info_frame, text=f"Rondas con ganador: {tied_data['non_tied_rounds']} ({tied_data['non_tied_frequency_percent']}%)", 
                 font=("Arial", 12)).pack(anchor="w", pady=2)

        # Métricas de eficiencia y tiempo
        efficiency_frame = tk.LabelFrame(scrollable_frame, text="Tiempo Total de Simulación y Eficiencia del Sistema", font=("Arial", 14, "bold"))
        efficiency_frame.pack(fill=tk.X, padx=10, pady=10)
        
        efficiency_data = results['efficiency_metrics']
        
        # Información de tiempo
        timing_frame = tk.LabelFrame(efficiency_frame, text="Tiempos de Ejecución", font=("Arial", 12, "bold"))
        timing_frame.pack(fill=tk.X, padx=5, pady=5)
        
        timing_grid = tk.Frame(timing_frame)
        timing_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(timing_grid, text=f"Tiempo Total: {efficiency_data['timing']['total_time_seconds']}s ({efficiency_data['timing']['total_time_minutes']} min)", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=2)
        tk.Label(timing_grid, text=f"• Configuración inicial: {efficiency_data['timing']['setup_time_seconds']}s ({efficiency_data['time_distribution']['setup_percentage']}%)", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(timing_grid, text=f"• Generación de juegos: {efficiency_data['timing']['games_generation_time_seconds']}s ({efficiency_data['time_distribution']['games_generation_percentage']}%)", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(timing_grid, text=f"• Análisis de resultados: {efficiency_data['timing']['analysis_time_seconds']}s ({efficiency_data['time_distribution']['analysis_percentage']}%)", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        
        # Velocidades de procesamiento
        performance_frame = tk.LabelFrame(efficiency_frame, text="Velocidades de Procesamiento", font=("Arial", 12, "bold"))
        performance_frame.pack(fill=tk.X, padx=5, pady=5)
        
        perf_grid = tk.Frame(performance_frame)
        perf_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Primera columna
        perf_left = tk.Frame(perf_grid)
        perf_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(perf_left, text=f"Juegos por segundo: {efficiency_data['processing_rates']['games_per_second']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(perf_left, text=f"Rondas por segundo: {efficiency_data['processing_rates']['rounds_per_second']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        
        # Segunda columna
        perf_right = tk.Frame(perf_grid)
        perf_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(perf_right, text=f"Disparos por segundo: {efficiency_data['processing_rates']['shots_per_second']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(perf_right, text=f"Cálculos de suerte/seg: {efficiency_data['processing_rates']['luck_calculations_per_second']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        
        # Volumen de datos procesados
        data_frame = tk.LabelFrame(efficiency_frame, text="Volumen de Datos Procesados", font=("Arial", 12, "bold"))
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        data_grid = tk.Frame(data_frame)
        data_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Primera columna
        data_left = tk.Frame(data_grid)
        data_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(data_left, text=f"Total de juegos: {efficiency_data['data_volume']['total_games']:,}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(data_left, text=f"Total de rondas: {efficiency_data['data_volume']['total_rounds']:,}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(data_left, text=f"Total de disparos: {efficiency_data['data_volume']['total_shots']:,}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        
        # Segunda columna
        data_right = tk.Frame(data_grid)
        data_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(data_right, text=f"Disparos promedio/juego: {efficiency_data['data_volume']['average_shots_per_game']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(data_right, text=f"Disparos promedio/ronda: {efficiency_data['data_volume']['average_shots_per_round']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(data_right, text=f"Cálculos de suerte: {efficiency_data['data_volume']['total_luck_calculations']:,}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        
        # Indicadores de rendimiento
        system_frame = tk.LabelFrame(efficiency_frame, text="Indicadores de Rendimiento del Sistema", font=("Arial", 12, "bold"))
        system_frame.pack(fill=tk.X, padx=5, pady=5)
        
        system_grid = tk.Frame(system_frame)
        system_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(system_grid, text=f"Puntuación de rendimiento: {efficiency_data['system_performance']['throughput_score']} operaciones/segundo", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(system_grid, text=f"Ratio de eficiencia: {efficiency_data['system_performance']['efficiency_ratio']} (0-1)", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)
        tk.Label(system_grid, text=f"Intensidad de procesamiento: {efficiency_data['system_performance']['processing_intensity']}", 
                 font=("Arial", 11)).pack(anchor="w", pady=1)

        # Gráficas de jugadores
        graphics_frame = tk.LabelFrame(scrollable_frame, text="Gráficas de Puntos vs Juegos por Jugador", font=("Arial", 14, "bold"))
        graphics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(graphics_frame, text="Haz clic en un jugador para ver su gráfica:", font=("Arial", 12)).pack(pady=5)
        
        grid2_frame = tk.Frame(graphics_frame)
        grid2_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        row, column = 0, 0
        for player_vs_game in results['points_vs_games_per_player']:
            data = {"points": player_vs_game['points']}
            tk.Button(grid2_frame, text=f"{player_vs_game['player'].name}", 
                command=lambda data=data, name=player_vs_game['player'].name: self.show_graphics(data, name)).grid(row=row, column=column, padx=2, pady=2)
            column += 1
            if column == 5:
                row += 1
                column = 0

        def on_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(scrollable_frame_id, width=self.winfo_width() - 10)
        
        scrollable_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_configure)
        
        def on_back():
            self.reset_view(results_frame)
            results_frame.destroy()
        
        tk.Button(results_frame, text="Volver", command=on_back).pack(pady=10)
        self.load_frame.pack_forget()
        results_frame.pack(fill=tk.BOTH, expand=True)
        self.load_frame.destroy()
    
    def reset_view(self, frame: tk.Frame):
        frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_graphics(self, data, player_name):
        plt.figure(figsize=(12, 8))
        games = list(range(1, len(data['points']) + 1))
        plt.plot(games, data['points'], color='blue', linewidth=2, alpha=0.7)
        plt.scatter(games, data['points'], color='red', s=20, alpha=0.6)
        plt.xlabel('Juegos', fontsize=12)
        plt.ylabel('Puntos', fontsize=12)
        plt.title(f'Gráfica de Puntos vs Juegos - {player_name}', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def show_dispersion_analysis(self, team_data):
        """Muestra análisis de dispersión para un equipo específico"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        scores = team_data['scores']
        team_name = team_data['name']
        avg = team_data['average_score']
        std = team_data['std_deviation']
        
        # 1. Histograma de distribución
        ax1.hist(scores, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(avg, color='red', linestyle='--', linewidth=2, label=f'Promedio: {avg}')
        ax1.axvline(avg + std, color='orange', linestyle='--', alpha=0.7, label=f'+1 Desv: {avg + std:.2f}')
        ax1.axvline(avg - std, color='orange', linestyle='--', alpha=0.7, label=f'-1 Desv: {avg - std:.2f}')
        ax1.set_xlabel('Puntaje por Juego')
        ax1.set_ylabel('Frecuencia')
        ax1.set_title(f'Distribución de Puntajes - {team_name}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Box plot
        ax2.boxplot(scores, patch_artist=True, 
                   boxprops=dict(facecolor='lightblue', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2))
        ax2.set_ylabel('Puntaje')
        ax2.set_title(f'Box Plot - {team_name}')
        ax2.grid(True, alpha=0.3)
        
        # 3. Serie temporal de puntajes
        games = list(range(1, len(scores) + 1))
        ax3.plot(games, scores, color='blue', alpha=0.6, linewidth=1)
        ax3.axhline(avg, color='red', linestyle='--', label=f'Promedio: {avg}')
        ax3.fill_between(games, avg - std, avg + std, alpha=0.2, color='orange', 
                        label=f'±1 Desviación Estándar')
        ax3.set_xlabel('Número de Juego')
        ax3.set_ylabel('Puntaje')
        ax3.set_title(f'Serie Temporal de Puntajes - {team_name}')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Q-Q Plot (aproximación simple)
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        theoretical_quantiles = [(i - 0.5) / n for i in range(1, n + 1)]
        
        # Aproximación a cuantiles normales
        import math
        normal_quantiles = [avg + std * math.sqrt(2) * self.inverse_erf(2 * q - 1) for q in theoretical_quantiles]
        
        ax4.scatter(normal_quantiles, sorted_scores, alpha=0.6, color='green')
        
        # Línea de referencia
        min_val = min(min(normal_quantiles), min(sorted_scores))
        max_val = max(max(normal_quantiles), max(sorted_scores))
        ax4.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.7)
        
        ax4.set_xlabel('Cuantiles Teóricos (Distribución Normal)')
        ax4.set_ylabel('Cuantiles Observados')
        ax4.set_title(f'Q-Q Plot vs Normal - {team_name}')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.suptitle(f'Análisis de Dispersión - {team_name}', fontsize=16, fontweight='bold', y=1.02)
        plt.show()

    def show_combined_dispersion_analysis(self, distribution_data):
        """Muestra análisis comparativo de dispersión entre ambos equipos"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        team_a_data = distribution_data['team_a']
        team_b_data = distribution_data['team_b']
        
        scores_a = team_a_data['scores']
        scores_b = team_b_data['scores']
        
        # 1. Histogramas superpuestos
        ax1.hist(scores_a, bins=30, alpha=0.6, color='blue', label='Team A', density=True)
        ax1.hist(scores_b, bins=30, alpha=0.6, color='red', label='Team B', density=True)
        ax1.axvline(team_a_data['average_score'], color='blue', linestyle='--', linewidth=2)
        ax1.axvline(team_b_data['average_score'], color='red', linestyle='--', linewidth=2)
        ax1.set_xlabel('Puntaje por Juego')
        ax1.set_ylabel('Densidad')
        ax1.set_title('Distribución Comparativa de Puntajes')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Box plots comparativos
        box_data = [scores_a, scores_b]
        box_labels = ['Team A', 'Team B']
        bp = ax2.boxplot(box_data, labels=box_labels, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightblue')
        bp['boxes'][1].set_facecolor('lightcoral')
        ax2.set_ylabel('Puntaje')
        ax2.set_title('Box Plot Comparativo')
        ax2.grid(True, alpha=0.3)
        
        # 3. Serie temporal comparativa (muestra)
        sample_size = min(100, len(scores_a))  # Muestra para mejor visualización
        games_sample = list(range(1, sample_size + 1))
        ax3.plot(games_sample, scores_a[:sample_size], color='blue', alpha=0.7, label='Team A', linewidth=1)
        ax3.plot(games_sample, scores_b[:sample_size], color='red', alpha=0.7, label='Team B', linewidth=1)
        ax3.axhline(team_a_data['average_score'], color='blue', linestyle='--', alpha=0.7)
        ax3.axhline(team_b_data['average_score'], color='red', linestyle='--', alpha=0.7)
        ax3.set_xlabel(f'Número de Juego (primeros {sample_size})')
        ax3.set_ylabel('Puntaje')
        ax3.set_title('Serie Temporal Comparativa (Muestra)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Comparación de estadísticas
        categories = ['Promedio', 'Desv. Estándar', 'Varianza']
        team_a_stats = [team_a_data['average_score'], team_a_data['std_deviation'], team_a_data['variance']]
        team_b_stats = [team_b_data['average_score'], team_b_data['std_deviation'], team_b_data['variance']]
        
        x = range(len(categories))
        width = 0.35
        
        ax4.bar([i - width/2 for i in x], team_a_stats, width, label='Team A', color='lightblue', alpha=0.8)
        ax4.bar([i + width/2 for i in x], team_b_stats, width, label='Team B', color='lightcoral', alpha=0.8)
        
        ax4.set_xlabel('Estadísticas')
        ax4.set_ylabel('Valor')
        ax4.set_title('Comparación de Estadísticas Descriptivas')
        ax4.set_xticks(x)
        ax4.set_xticklabels(categories)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Añadir valores sobre las barras
        for i, (a_stat, b_stat) in enumerate(zip(team_a_stats, team_b_stats)):
            ax4.text(i - width/2, a_stat + max(team_a_stats + team_b_stats) * 0.01, 
                    f'{a_stat:.2f}', ha='center', va='bottom', fontsize=9)
            ax4.text(i + width/2, b_stat + max(team_a_stats + team_b_stats) * 0.01, 
                    f'{b_stat:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.suptitle('Análisis Comparativo de Dispersión - Team A vs Team B', 
                     fontsize=16, fontweight='bold', y=1.02)
        plt.show()

    def inverse_erf(self, x):
        """Aproximación simple de la función inversa del error para Q-Q plot"""
        import math
        # Aproximación de Beasley-Springer-Moro
        if abs(x) >= 1:
            return 0
        
        # Aproximación simple para demostración
        if x == 0:
            return 0
        
        # Usamos una aproximación básica
        a = 0.147
        b = 2 / (math.pi * a) + math.log(1 - x*x) / 2
        result = math.copysign(math.sqrt(math.sqrt(b*b - math.log(1 - x*x) / a) - b), x)
        return result

if __name__ == "__main__":
    model: IModel = Model()
    view: IView = View()
    presenter = Presenter(model, view)
    view.mainloop()