import tkinter as tk
from tkinter import colorchooser
import svgwrite

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
        
        self.canvas.bind("<Button-3>", self.place_circle)
        self.canvas.bind("<ButtonPress-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.draw_temp_points)
        self.canvas.bind("<ButtonRelease-1>", self.draw_line)

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
            for i in range(len(self.dots) - 1):
                self.canvas.create_line(self.dots[i], self.dots[i+1], fill=self.color, width=self.line_width_slider.get(), capstyle=tk.ROUND)
        self.dots = []  # Réinitialise les points après avoir tracé la ligne
    
    def reset(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.lines.clear()  # Réinitialiser toutes les lignes
    
    def export_svg(self):
        dwg = svgwrite.Drawing("output.svg", profile='tiny', size=(self.grid_size*self.cell_size, self.grid_size*self.cell_size))

        # Dessiner les lignes
        for line in self.lines:
            if line and isinstance(line[0], tuple):
                for i in range(len(line) - 1):
                    dwg.add(dwg.line(start=line[i], end=line[i+1], stroke=self.color, stroke_width=self.line_width_slider.get(), stroke_linecap='round'))
        
        # Dessiner les cercles
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    dwg.add(dwg.circle(center=(x, y), r=(self.line_width_slider.get() * 3) // 2, fill=self.color))

        dwg.save()
        print("Exported to output.svg")




if __name__ == "__main__":
    root = tk.Tk()
    app = GridDrawingApp(root)
    root.mainloop()
