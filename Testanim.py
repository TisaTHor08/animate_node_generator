import tkinter as tk
from tkinter import colorchooser
import drawsvg as draw

class GridDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid Drawing App")
        
        self.cell_size = 30
        self.grid_size = 20
        self.color = "black"
        self.line_width = 3
        self.dots = []
        self.lines = []  # Liste de lignes, chaque ligne est une liste de points
        self.intermediate_points = {}  # Dictionnaire pour stocker les points intermédiaires
        
        self.canvas = tk.Canvas(root, width=self.cell_size*self.grid_size, height=self.cell_size*self.grid_size, bg="white")
        self.canvas.pack(side=tk.LEFT)
        self.draw_grid()
        
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.color_button = tk.Button(self.controls_frame, text="Choose Color", command=self.choose_color)
        self.color_button.pack(pady=5)
        
        self.line_width_slider = tk.Scale(self.controls_frame, from_=1, to=10, orient=tk.HORIZONTAL, label="Line Width")
        self.line_width_slider.set(self.line_width)
        self.line_width_slider.pack(pady=5)
        
        self.reset_button = tk.Button(self.controls_frame, text="Reset", command=self.reset)
        self.reset_button.pack(pady=5)
        
        self.export_button = tk.Button(self.controls_frame, text="Export SVG", command=self.export_svg)
        self.export_button.pack(pady=5)
        
        self.animated_var = tk.BooleanVar()
        self.animated_checkbox = tk.Checkbutton(self.controls_frame, text="Animated", variable=self.animated_var)
        self.animated_checkbox.pack(pady=5)
        
        self.canvas.bind("<Button-3>", self.place_circle)
        self.canvas.bind("<ButtonPress-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.draw_temp_points)
        self.canvas.bind("<ButtonRelease-1>", self.draw_line)
        self.root.bind("<l>", self.print_intermediate_points)  # Lier la touche "L" à l'événement

    def draw_grid(self):
        for i in range(self.grid_size + 1):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, fill="gray")
            self.canvas.create_line(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, fill="gray")
    
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color
    
    def place_circle(self, event):
        x, y = (event.x // self.cell_size) * self.cell_size + self.cell_size//2, (event.y // self.cell_size) * self.cell_size + self.cell_size//2
        radius = (self.line_width_slider.get() * 3) // 2
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=self.color, outline=self.color)
        self.lines.append([(x, y, 'circle')])  # Créer un nouveau "groupe de points" pour cette ligne
    
    def start_line(self, event):
        self.dots = []  # Réinitialise la liste des points pour une nouvelle ligne
    
    def draw_temp_points(self, event):
        x, y = (event.x // self.cell_size) * self.cell_size + self.cell_size//2, (event.y // self.cell_size) * self.cell_size + self.cell_size//2
        if (x, y) not in self.dots:
            self.dots.append((x, y))
    
    def draw_line(self, event):
        if len(self.dots) > 1:
            self.lines.append(self.dots)  # Ajouter la nouvelle ligne à la liste des lignes
            self.intermediate_points[len(self.lines)] = self.dots  # Stocker les points intermédiaires dans le dictionnaire
            for i in range(len(self.dots) - 1):
                self.canvas.create_line(self.dots[i], self.dots[i+1], fill=self.color, width=self.line_width_slider.get(), capstyle=tk.ROUND)
        self.dots = []  # Réinitialise les points après avoir tracé la ligne
    
    def reset(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.lines.clear()  # Réinitialiser toutes les lignes
        self.intermediate_points.clear()  # Réinitialiser le dictionnaire
    
    def export_svg(self):
        if self.animated_var.get():
            self.export_animated_svg()
        else:
            self.export_static_svg()
    
    def export_static_svg(self):
        dwg = draw.Drawing(self.grid_size * self.cell_size, self.grid_size * self.cell_size, origin='center')

        # Dessiner les lignes
        for line in self.lines:
            if line and isinstance(line[0], tuple):
                for i in range(len(line) - 1):
                    # Passer les coordonnées sous forme de valeurs individuelles (sx, sy, ex, ey)
                    dwg.append(draw.Line(sx=line[i][0], sy=line[i][1], ex=line[i+1][0], ey=line[i+1][1], stroke=self.color, stroke_width=self.line_width_slider.get(), stroke_linecap='round'))
        
        # Dessiner les cercles
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    dwg.append(draw.Circle(center=(x, y), r=(self.line_width_slider.get() * 3) // 2, fill=self.color))

        dwg.save_svg('output.svg')
        print("Exported to output.svg")
    
    def export_animated_svg(self):
        dwg = draw.Drawing(self.grid_size * self.cell_size, self.grid_size * self.cell_size, origin='center')

        # Ajouter les cercles (toujours visibles) - on conserve les points intermédiaires
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    circle_elem = draw.Circle(cx=x, cy=y, r=(self.line_width_slider.get() * 3) // 2, fill=self.color)
                    dwg.append(circle_elem)

        # Ajouter les lignes avec un "stylo" qui trace chaque segment progressivement
        for line in self.lines:
            if line and isinstance(line[0], tuple):
                for i in range(len(line) - 1):
                    start_point = line[i]
                    end_point = line[i + 1]
                    
                    # Créer un élément de chemin pour l'animation
                    line_elem = draw.Path(stroke=self.color, stroke_width=self.line_width_slider.get(), fill='none')

                    # Ajouter une animation de stylo pour chaque segment
                    line_elem.M(start_point[0], start_point[1])  # Début du segment
                    line_elem.L(end_point[0], end_point[1])  # Fin du segment

                    # Animation pour dessiner le segment progressivement
                    line_elem.append_anim(
                        draw.Animate('stroke-dashoffset', dur='2s', from_="100", to="0", repeatCount='indefinite')
                    )
                    line_elem.append_anim(
                        draw.Animate('stroke-dasharray', dur='2s', from_="1, 200", to="200, 0", repeatCount='indefinite')
                    )

                    dwg.append(line_elem)

        dwg.save_svg('output_animated.svg')
        print("Exporté vers output_animated.svg")

    def print_intermediate_points(self, event):
        for key, value in self.intermediate_points.items():
            print(f"Line {key}: {value}")

# À la fin de ton code
if __name__ == "__main__":
    root = tk.Tk()
    app = GridDrawingApp(root)
    root.mainloop()  # Démarrer la boucle d'événements de Tkinter
