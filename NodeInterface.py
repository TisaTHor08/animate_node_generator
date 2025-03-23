import tkinter as tk
from tkinter import colorchooser
import drawsvg as draw
import time
import math

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
        self.angle_rounding = 5.0  # Valeur d'arrondi par défaut pour les angles (en pixels)
        
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
        
        self.angle_rounding_label = tk.Label(self.controls_frame, text="Angle Rounding (in px)")
        self.angle_rounding_label.pack(pady=5)
        
        self.angle_rounding_entry = tk.Entry(self.controls_frame)
        self.angle_rounding_entry.insert(0, str(self.angle_rounding))
        self.angle_rounding_entry.pack(pady=5)
        
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
            self.detect_angles(self.dots)  # Détecter les angles et afficher les cases rouges
            for i in range(len(self.dots) - 1):
                self.canvas.create_line(self.dots[i], self.dots[i+1], fill=self.color, width=self.line_width_slider.get(), capstyle=tk.ROUND)
        self.dots = []  # Réinitialise les points après avoir tracé la ligne
    
    def detect_angles(self, points):
        # Détecte les angles et dessine une case rouge pour chaque angle
        for i in range(1, len(points) - 1):
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            if self.is_angle(p1, p2, p3):
                # Tracer une case rouge à l'angle
                x, y = p2
                radius = self.line_width_slider.get() * 2
                self.canvas.create_rectangle(x - radius, y - radius, x + radius, y + radius, outline="red", width=2)
                
                # Entourer les cases précédentes et suivantes en vert
                self.highlight_surrounding_cases(p1, p3)
                
                # Tracer la courbe de Bézier cubique et afficher la liste des points
                bezier_points = self.calculate_cubic_bezier_curve(p1, p2, p3)
                print(f"Angle n°{i}: {bezier_points}")
                self.draw_bezier_curve(bezier_points)
    
    def is_angle(self, p1, p2, p3):
        # Fonction pour déterminer si un point p2 est un angle formé par p1 et p3
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        # Calculer les vecteurs (p1 -> p2) et (p2 -> p3)
        v1x, v1y = x2 - x1, y2 - y1
        v2x, v2y = x3 - x2, y3 - y2
        
        # Calculer l'angle entre les deux vecteurs en utilisant le produit scalaire
        dot_product = v1x * v2x + v1y * v2y
        magnitude_v1 = math.sqrt(v1x**2 + v1y**2)
        magnitude_v2 = math.sqrt(v2x**2 + v2y**2)
        
        if magnitude_v1 * magnitude_v2 == 0:
            return False
        
        cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
        angle = math.acos(cos_theta)
        
        # Si l'angle est proche de 90 degrés, c'est un angle
        return abs(angle - math.pi / 2) < 0.2
    
    def highlight_surrounding_cases(self, p1, p3):
        # Entourer les cases précédentes (p1) et suivantes (p3) en vert
        for p in [p1, p3]:
            x, y = p
            radius = self.line_width_slider.get() * 2
            self.canvas.create_rectangle(x - radius, y - radius, x + radius, y + radius, outline="green", width=2)
    
    def calculate_cubic_bezier_curve(self, p1, p2, p3):
        # Obtenir la valeur d'arrondi entrée par l'utilisateur
        self.angle_rounding = float(self.angle_rounding_entry.get())
        
        # Calcul des points de contrôle en utilisant l'arrondi de l'angle
        control1 = (p1[0] + (p2[0] - p1[0]) / (2 + self.angle_rounding), p1[1] + (p2[1] - p1[1]) / (2 + self.angle_rounding))
        control2 = (p3[0] - (p3[0] - p2[0]) / (2 + self.angle_rounding), p3[1] - (p3[1] - p2[1]) / (2 + self.angle_rounding))
        
        # Calculer 10 points sur la courbe de Bézier cubique
        bezier_points = []
        for t in [i / 9 for i in range(10)]:
            x = (1 - t) ** 3 * p1[0] + 3 * (1 - t) ** 2 * t * control1[0] + 3 * (1 - t) * t ** 2 * control2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p1[1] + 3 * (1 - t) ** 2 * t * control1[1] + 3 * (1 - t) * t ** 2 * control2[1] + t ** 3 * p3[1]
            bezier_points.append((x, y))
        return bezier_points
    
    def draw_bezier_curve(self, points):
        # Relier les points de la courbe de Bézier par une ligne rouge
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill="red", width=2)
    
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
                print(f"Line length: {line_length}, Duration: {duration} seconds")

                # Ajouter l'animation de trace
                for i in range(1, len(line)):
                    line_elem.L(line[i][0] - margin_x, line[i][1] - margin_y)

                # Appliquer l'animation (début de la ligne invisible, fin de la ligne entièrement visible)
                line_elem.animation('stroke-dasharray', '0,{line_length}', duration=duration, begin="0s", repeatCount="indefinite")
                to_dasharray = f"{line_length},{line_length}"  # Commencer l'animation avec la ligne complètement invisible
                to_dasharray = f"{line_length},{line_length}"  # Se terminer avec la ligne entièrement visible
                dwg.append(line_elem)

        dwg.save_svg('output_animated.svg')
        print("Exported animated SVG to output_animated.svg")

    def print_intermediate_points(self, event):
        for key, value in self.intermediate_points.items():
            print(f"Ligne {key}: {value}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GridDrawingApp(root)
    root.mainloop()
