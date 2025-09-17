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
        self.title("Aplicación")
        self.geometry("800x600")
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
        tk.Label(scrollable_frame, text="Resultados", font=("Arial", 20)).pack(pady=15)
        grid_frame = tk.Frame(scrollable_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(grid_frame, text="Jugador con mas suerte por juego:", font=("Arial", 15)).grid(row=0, column=0)
        tk.Label(grid_frame, text=f"{results['luckiest_player_per_game']['player'].name} - {results['luckiest_player_per_game']['amount_luck']} veces", 
                 font=("Arial", 15)).grid(row=0, column=1)
        tk.Label(grid_frame, text="Jugador con mas experiencia:", font=("Arial", 15)).grid(row=1, column=0)
        tk.Label(grid_frame, text=f"{results['more_experienced_player']['player'].name} - {results['more_experienced_player']['amount_experienced']} en experiencia", 
                 font=("Arial", 15)).grid(row=1, column=1)
        tk.Label(grid_frame, text="Genero mas ganador por juego:", font=("Arial", 15)).grid(row=2, column=0)
        tk.Label(grid_frame, text=f"{results['winner_gender_per_game']['gender']} - {results['winner_gender_per_game']['amount_wins']} veces", 
                 font=("Arial", 15)).grid(row=2, column=1)
        tk.Label(grid_frame, text="Genero mas ganador en total:", font=("Arial", 15)).grid(row=3, column=0)
        tk.Label(grid_frame, text=f"{results['winner_gender_total']['gender']} - {results['winner_gender_total']['total_rounds_won']} veces", 
                 font=("Arial", 15)).grid(row=3, column=1)
        tk.Label(scrollable_frame, text=f"Equipo ganador: {results['winner_team_total']['team'].name}", font=("Arial", 15)).pack(pady=10)
        for player_points in results['winner_team_total']['player_points']:
            tk.Label(scrollable_frame, text=f"{player_points['player']} - {player_points['points']} puntos", font=("Arial", 12)).pack(pady=5)
        tk.Label(scrollable_frame, text=f"Graficas de jugador vs juegos:", font=("Arial", 15)).pack(pady=10)
        grid2_frame = tk.Frame(scrollable_frame)
        grid2_frame.pack(fill=tk.BOTH, expand=True)
        row, column = 0, 0
        games = [i for i in range(1, 20000+1)]
        for player_vs_game in results['points_vs_games_per_player']:
            data ={"points": player_vs_game['points'], "games": games }
            tk.Button(grid2_frame, text=f"{player_vs_game['player'].name}", 
                command=lambda: self.show_graphics(data)).grid(row=row, column=column)
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
    
    def show_graphics(self, data):
        plt.figure(figsize=(10, 6))
        # Asegurarse de que games tenga la misma longitud que points
        games = list(range(1, len(data['points']) + 1))
        plt.plot(games, data['points'], color='blue')
        plt.scatter(games, data['points'], color='gray')
        plt.xlabel('Juegos')
        plt.ylabel('Puntos')
        plt.title('Grafica de jugador')
        plt.show()

if __name__ == "__main__":
    model: IModel = Model()
    view: IView = View()
    presenter = Presenter(model, view)
    view.mainloop()