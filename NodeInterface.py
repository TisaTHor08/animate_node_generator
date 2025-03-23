import tkinter as tk
from tkinter import colorchooser
import drawsvg as draw
import time

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
        # Définir les coordonnées du rectangle de la zone de dessin
        margin_x, margin_y = 15, 15
        width = 585 - 15
        height = 585 - 15
        
        dwg = draw.Drawing(width, height, origin=(margin_x, margin_y))

        # Dessiner les lignes avec la nouvelle translation
        for line in self.lines:
            if line and isinstance(line[0], tuple):
                for i in range(len(line) - 1):
                    start_x, start_y = line[i]
                    end_x, end_y = line[i+1]
                    dwg.append(draw.Line(sx=start_x - margin_x, sy=start_y - margin_y, 
                                         ex=end_x - margin_x, ey=end_y - margin_y, 
                                         stroke=self.color, stroke_width=self.line_width_slider.get(), stroke_linecap='round'))
        
        # Dessiner les cercles avec la nouvelle translation
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    dwg.append(draw.Circle(center=(x - margin_x, y - margin_y), 
                                           r=(self.line_width_slider.get() * 3) // 2, fill=self.color))

        dwg.save_svg('output.svg')
        print("Exported to output.svg")

    def export_animated_svg(self):
        margin_x, margin_y = 15, 15
        width = 585 - 15
        height = 585 - 15
        
        dwg = draw.Drawing(width, height, origin=(margin_x, margin_y))

        # Ajouter les cercles (toujours visibles)
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    dwg.append(draw.Circle(cx=x - margin_x, cy=y - margin_y, 
                                        r=(self.line_width_slider.get() * 3) // 2, fill=self.color))

        # Vitesse constante en pixels par seconde
        speed = 100  # pixels par seconde

        # Ajouter une animation de stylo pour chaque ligne, qui trace tous les segments
        for line in self.lines:
            if line and isinstance(line[0], tuple):
                # Créer un élément de chemin pour l'animation de "stylo"
                line_elem = draw.Path(stroke=self.color, stroke_width=self.line_width_slider.get(), fill='none')

                # Commencer à la première coordonnée
                line_elem.M(line[0][0] - margin_x, line[0][1] - margin_y)

                # Calculer la longueur totale de la ligne
                line_length = 0
                for i in range(1, len(line)):
                    line_length += ((line[i][0] - line[i-1][0])**2 + (line[i][1] - line[i-1][1])**2) ** 0.5
                
                # Calculer la durée de l'animation en fonction de la longueur de la ligne et de la vitesse
                duration = line_length / speed  # La durée est la longueur divisée par la vitesse

                # Print pour vérifier la durée calculée
                print(f"Durée calculée pour la ligne : {duration:.2f} secondes (longueur: {line_length:.2f} px, vitesse: {speed} px/s)")

                # Démarrer le chronomètre
                start_time = time.time()

                # Ajouter chaque segment successivement à partir de la première coordonnée
                for i in range(1, len(line)):
                    line_elem.L(line[i][0] - margin_x, line[i][1] - margin_y)

                # Définir l'animation avec un `stroke-dasharray` constant
                from_dasharray = f"1, {line_length * 1}"  # Segment très court au début
                to_dasharray = f"{line_length * 1}, 0"  # Segment long à la fin
                # Appliquer l'animation pour tracer la ligne
                line_elem.append_anim(
                    draw.Animate('stroke-dasharray', dur=f'{duration}s', values=f'{from_dasharray}; {to_dasharray}; {from_dasharray}', repeatCount="indefinite")
                )
                """
                # Appliquer l'animation inverse pour effacer la ligne avec un délai de 0,5 seconde
                line_elem.append_anim(
                    draw.Animate('stroke-dasharray', dur=f'{duration}s', from_=to_dasharray, to=from_dasharray, 
                                begin=f'{duration}s')  # Délai de 0,5s avant d'effacer
                )

                # Ajouter une animation de tracé répétée après l'effacement
                line_elem.append_anim(
                    draw.Animate('stroke-dasharray', dur=f'{duration}s', from_=from_dasharray, to=to_dasharray,
                                begin=f'{duration * 2}s', repeatCount="indefinite")  # Recommence après effacement
                )
                # Appliquer l'animation inverse pour effacer la ligne avec un délai de 0,5 seconde
                line_elem.append_anim(
                    draw.Animate('stroke-dasharray', dur=f'{duration}s', from_=to_dasharray, to=from_dasharray, 
                                begin=f'{duration * 3}s', repeatCount="indefinite")  # Délai de 0,5s avant d'effacer
                )"""

                # Ajouter l'élément au dessin
                dwg.append(line_elem)

        # Sauvegarder l'animation dans un fichier SVG
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
