import tkinter as tk
import svgwrite
import math

class GridApp:
    def __init__(self, master, grid_size=20, cell_size=30):
        self.master = master
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.points = []  # Liste des points principaux
        self.lines = []  # Liste des lignes coudées
        self.start_point = None
        self.temp_points = []  # Liste pour stocker les points intermédiaires pendant la création de la ligne
        self.current_line = None

        # Couleurs par défaut et épaisseur
        self.point_color = "red"  # Couleur des points principaux
        self.line_color = "blue"
        self.line_width = 2
        self.temp_point_color = "green"  # Couleur des points intermédiaires
        self.show_inter_points = True  # Affichage par défaut des points intermédiaires
        self.smooth_lines = False  # Par défaut, les lignes ne sont pas lisses

        # Canvas principal
        self.canvas = tk.Canvas(master, width=grid_size * cell_size, height=grid_size * cell_size)
        self.canvas.grid(row=0, column=0)

        # Panneau latéral pour les paramètres
        self.sidebar = tk.Frame(master)
        self.sidebar.grid(row=0, column=1, padx=10)

        self.create_sidebar()

        self.create_grid()
        self.canvas.bind("<Button-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.add_intermediate_points)
        self.canvas.bind("<ButtonRelease-1>", self.end_line)

    def create_sidebar(self):
        tk.Label(self.sidebar, text="Couleur des points principaux").grid(row=0, column=0, sticky="w")
        self.point_color_entry = tk.Entry(self.sidebar)
        self.point_color_entry.insert(0, self.point_color)
        self.point_color_entry.grid(row=0, column=1)
        self.point_color_entry.bind("<KeyRelease>", self.update_point_color)

        tk.Label(self.sidebar, text="Couleur des lignes").grid(row=1, column=0, sticky="w")
        self.line_color_entry = tk.Entry(self.sidebar)
        self.line_color_entry.insert(0, self.line_color)
        self.line_color_entry.grid(row=1, column=1)
        self.line_color_entry.bind("<KeyRelease>", self.update_line_color)

        tk.Label(self.sidebar, text="Épaisseur des lignes").grid(row=2, column=0, sticky="w")
        self.line_width_entry = tk.Entry(self.sidebar)
        self.line_width_entry.insert(0, self.line_width)
        self.line_width_entry.grid(row=2, column=1)
        self.line_width_entry.bind("<KeyRelease>", self.update_line_width)

        # Case à cocher pour afficher/masquer les points intermédiaires
        self.show_inter_points_var = tk.BooleanVar(value=self.show_inter_points)
        tk.Checkbutton(self.sidebar, text="Afficher les points intermédiaires", variable=self.show_inter_points_var,
                       command=self.toggle_intermediate_points).grid(row=3, columnspan=2, pady=5)

        # Case à cocher pour activer/désactiver les lignes lisses
        self.smooth_lines_var = tk.BooleanVar(value=self.smooth_lines)
        tk.Checkbutton(self.sidebar, text="Lignes lisses", variable=self.smooth_lines_var,
                       command=self.toggle_smooth_lines).grid(row=4, columnspan=2, pady=5)

    def create_grid(self):
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, fill="lightgray")
            self.canvas.create_line(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, fill="lightgray")

    def start_line(self, event):
        # Enregistrer le point de départ (point principal)
        self.start_point = (event.x // self.cell_size, event.y // self.cell_size)
        self.points.append(self.start_point)
        self.temp_points = [self.start_point]  # Réinitialiser la liste des points intermédiaires
        self.canvas.create_oval(self.start_point[0] * self.cell_size, self.start_point[1] * self.cell_size,
                                (self.start_point[0] + 1) * self.cell_size, (self.start_point[1] + 1) * self.cell_size, 
                                fill=self.point_color, tags="main_point")  # Ajouter le point principal
        self.current_line = None  # Réinitialiser la ligne en cours

    def add_intermediate_points(self, event):
        # Ajouter des points intermédiaires quand le clic est maintenu
        current_pos = (event.x // self.cell_size, event.y // self.cell_size)

        # Si le dernier point ajouté est différent du point actuel, ajouter un nouveau point intermédiaire
        if current_pos != self.temp_points[-1]:
            self.temp_points.append(current_pos)

            # Effacer la ligne précédente
            if self.current_line:
                self.canvas.delete(self.current_line)

            # Dessiner la ligne entre les points intermédiaires
            self.current_line = self.canvas.create_oval(self.temp_points[-1][0] * self.cell_size,
                                                        self.temp_points[-1][1] * self.cell_size,
                                                        (self.temp_points[-1][0] + 1) * self.cell_size,
                                                        (self.temp_points[-1][1] + 1) * self.cell_size,
                                                        fill=self.line_color, width=self.line_width, tags="temp_line")

            # Dessiner des lignes entre chaque paire de points intermédiaires
            for i in range(1, len(self.temp_points)):
                self.canvas.create_line(self.temp_points[i-1][0] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i-1][1] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i][0] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i][1] * self.cell_size + self.cell_size / 2, 
                                        fill=self.line_color, width=self.line_width)

            # Dessiner les points intermédiaires uniquement si la case est cochée
            if self.show_inter_points:
                self.canvas.create_oval(current_pos[0] * self.cell_size, current_pos[1] * self.cell_size,
                                        (current_pos[0] + 1) * self.cell_size, (current_pos[1] + 1) * self.cell_size,
                                        fill=self.temp_point_color, tags="intermediate_point")

    def end_line(self, event):
        # Définir le dernier point au moment du relâchement du clic
        end_point = (event.x // self.cell_size, event.y // self.cell_size)
        if end_point != self.temp_points[-1]:
            self.temp_points.append(end_point)

        # Dessiner la ligne finale entre tous les points intermédiaires
        self.lines.append(self.temp_points)
        
        # Supprimer la ligne droite entre le point de départ et d'arrivée
        self.canvas.delete(self.current_line)

        # Dessiner la série de lignes coudées ou lisses
        if self.smooth_lines:
            self.draw_smooth_lines()
        else:
            for i in range(1, len(self.temp_points)):
                self.canvas.create_line(self.temp_points[i-1][0] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i-1][1] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i][0] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i][1] * self.cell_size + self.cell_size / 2, 
                                        fill=self.line_color, width=self.line_width)

        # Ajouter les points principaux à la liste des points (mais les points intermédiaires ne sont pas visibles)
        self.points.extend(self.temp_points)

        # Réinitialiser le point de départ
        self.start_point = None
        self.temp_points = []  # Réinitialiser la liste des points intermédiaires

    def draw_smooth_lines(self):
        """Dessine des lignes lisses (utilise des cercles comme stylo pour tracer les courbes)."""
        for i in range(1, len(self.temp_points)):
            p0 = self.temp_points[i-1]
            p1 = self.temp_points[i]
            cx = (p0[0] + p1[0]) * self.cell_size / 2
            cy = (p0[1] + p1[1]) * self.cell_size / 2
            # Utiliser un arc pour tracer la ligne courbée
            self.canvas.create_oval(p0[0] * self.cell_size + self.cell_size / 2,
                                    p0[1] * self.cell_size + self.cell_size / 2,
                                    p1[0] * self.cell_size + self.cell_size / 2,
                                    p1[1] * self.cell_size + self.cell_size / 2,
                                    width=self.line_width, outline=self.line_color, tags="smooth_line")

    def update_point_color(self, event):
        """Met à jour la couleur des points principaux."""
        self.point_color = self.point_color_entry.get()
        self.redraw_points()

    def update_line_color(self, event):
        """Met à jour la couleur des lignes."""
        self.line_color = self.line_color_entry.get()
        self.redraw_lines()

    def update_line_width(self, event):
        """Met à jour l'épaisseur des lignes."""
        try:
            self.line_width = int(self.line_width_entry.get())
            self.redraw_lines()
        except ValueError:
            pass  # Ignore si la valeur n'est pas un entier valide

    def toggle_intermediate_points(self):
        """Activer ou désactiver l'affichage des points intermédiaires."""
        self.show_inter_points = self.show_inter_points_var.get()
        self.redraw_intermediate_points()

    def toggle_smooth_lines(self):
        """Activer ou désactiver l'affichage des lignes lisses."""
        self.smooth_lines = self.smooth_lines_var.get()
        self.redraw_lines()

    def redraw_points(self):
        """Redessine tous les points avec la nouvelle couleur."""
        self.canvas.delete("main_point")  # Supprimer les anciens points
        for point in self.points:
            self.canvas.create_oval(point[0] * self.cell_size, point[1] * self.cell_size,
                                    (point[0] + 1) * self.cell_size, (point[1] + 1) * self.cell_size, 
                                    fill=self.point_color, tags="main_point")

    def redraw_lines(self):
        """Redessine toutes les lignes avec la nouvelle couleur et épaisseur."""
        self.canvas.delete("lines")  # Supprimer les anciennes lignes
        for line in self.lines:
            if self.smooth_lines:
                self.draw_smooth_lines()
            else:
                for i in range(1, len(line)):
                    start = line[i-1]
                    end = line[i]
                    self.canvas.create_line(start[0] * self.cell_size + self.cell_size / 2,
                                            start[1] * self.cell_size + self.cell_size / 2,
                                            end[0] * self.cell_size + self.cell_size / 2,
                                            end[1] * self.cell_size + self.cell_size / 2, 
                                            fill=self.line_color, width=self.line_width, tags="lines")

    def redraw_intermediate_points(self):
        """Redessine les points intermédiaires en fonction de l'état de la case à cocher."""
        self.canvas.delete("intermediate_point")  # Supprimer les anciens points intermédiaires
        if self.show_inter_points:
            for line in self.lines:
                for point in line:
                    self.canvas.create_oval(point[0] * self.cell_size, point[1] * self.cell_size,
                                            (point[0] + 1) * self.cell_size, (point[1] + 1) * self.cell_size, 
                                            fill=self.temp_point_color, tags="intermediate_point")

# Application Tkinter
root = tk.Tk()
app = GridApp(root)
root.mainloop()
