import tkinter as tk
import svgwrite

class GridApp:
    def __init__(self, master, grid_size=20, cell_size=30):
        self.master = master
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.points = []
        self.lines = []
        self.start_point = None
        self.current_line = None
        self.temp_points = []  # Liste pour stocker les points intermédiaires pendant la création de la ligne

        self.canvas = tk.Canvas(master, width=grid_size * cell_size, height=grid_size * cell_size)
        self.canvas.pack()

        self.create_grid()
        self.canvas.bind("<Button-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.add_intermediate_points)
        self.canvas.bind("<ButtonRelease-1>", self.end_line)

    def create_grid(self):
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, fill="lightgray")
            self.canvas.create_line(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, fill="lightgray")

    def start_line(self, event):
        # Enregistrer le point de départ
        self.start_point = (event.x // self.cell_size, event.y // self.cell_size)
        self.points.append(self.start_point)
        self.temp_points = [self.start_point]  # Réinitialiser la liste des points intermédiaires
        self.canvas.create_oval(self.start_point[0] * self.cell_size, self.start_point[1] * self.cell_size,
                                (self.start_point[0] + 1) * self.cell_size, (self.start_point[1] + 1) * self.cell_size, fill="red")
        self.current_line = None  # Réinitialiser la ligne en cours

    def add_intermediate_points(self, event):
        # Ajouter des points intermédiaires quand le clic est maintenu
        current_pos = (event.x // self.cell_size, event.y // self.cell_size)

        # Si le dernier point ajouté est différent du point actuel, ajouter un nouveau point intermédiaire
        if current_pos != self.temp_points[-1]:
            self.temp_points.append(current_pos)
            self.canvas.create_oval(current_pos[0] * self.cell_size, current_pos[1] * self.cell_size,
                                    (current_pos[0] + 1) * self.cell_size, (current_pos[1] + 1) * self.cell_size, fill="blue")

            # Effacer la ligne précédente
            if self.current_line:
                self.canvas.delete(self.current_line)

            # Dessiner la ligne entre les points intermédiaires
            self.current_line = self.canvas.create_line(self.temp_points[0][0] * self.cell_size + self.cell_size / 2,
                                                        self.temp_points[0][1] * self.cell_size + self.cell_size / 2,
                                                        current_pos[0] * self.cell_size + self.cell_size / 2,
                                                        current_pos[1] * self.cell_size + self.cell_size / 2, fill="blue")

            for i in range(1, len(self.temp_points)):
                self.canvas.create_line(self.temp_points[i-1][0] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i-1][1] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i][0] * self.cell_size + self.cell_size / 2,
                                        self.temp_points[i][1] * self.cell_size + self.cell_size / 2, fill="blue")

    def end_line(self, event):
        # Définir le dernier point au moment du relâchement du clic
        end_point = (event.x // self.cell_size, event.y // self.cell_size)
        if end_point != self.temp_points[-1]:
            self.temp_points.append(end_point)

        # Dessiner la ligne finale entre tous les points intermédiaires
        self.lines.append(self.temp_points)
        self.canvas.create_line(self.temp_points[0][0] * self.cell_size + self.cell_size / 2,
                                self.temp_points[0][1] * self.cell_size + self.cell_size / 2,
                                self.temp_points[-1][0] * self.cell_size + self.cell_size / 2,
                                self.temp_points[-1][1] * self.cell_size + self.cell_size / 2, fill="blue")

        for i in range(1, len(self.temp_points)):
            self.canvas.create_line(self.temp_points[i-1][0] * self.cell_size + self.cell_size / 2,
                                    self.temp_points[i-1][1] * self.cell_size + self.cell_size / 2,
                                    self.temp_points[i][0] * self.cell_size + self.cell_size / 2,
                                    self.temp_points[i][1] * self.cell_size + self.cell_size / 2, fill="blue")

        # Ajouter le dernier point à la liste des points
        self.points.extend(self.temp_points)

        # Réinitialiser le point de départ
        self.start_point = None
        self.temp_points = []  # Réinitialiser la liste des points intermédiaires

    def export_svg(self, filename="output.svg"):
        dwg = svgwrite.Drawing(filename, profile='tiny')
        for line in self.lines:
            for i in range(1, len(line)):
                start = line[i-1]
                end = line[i]
                dwg.add(dwg.line(start=(start[0] * self.cell_size, start[1] * self.cell_size),
                                 end=(end[0] * self.cell_size, end[1] * self.cell_size),
                                 stroke='blue'))
        for point in self.points:
            dwg.add(dwg.circle(center=(point[0] * self.cell_size, point[1] * self.cell_size),
                               r=5, fill='red'))
        dwg.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()
