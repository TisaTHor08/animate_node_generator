import tkinter as tk
from tkinter import colorchooser, ttk
import drawsvg as draw
import time

class ModernStyle:
    def __init__(self):
        self.bg_color = "#2C3E50"
        self.fg_color = "#ECF0F1"
        self.accent_color = "#3498DB"
        self.button_hover = "#2980B9"
        self.canvas_bg = "#34495E"
        self.grid_color = "#7F8C8D"
        self.font = ("Helvetica", 10)
        
    def style_button(self, button):
        button.configure(
            bg=self.accent_color,
            fg=self.fg_color,
            font=self.font,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        button.bind("<Enter>", lambda e: button.configure(bg=self.button_hover))
        button.bind("<Leave>", lambda e: button.configure(bg=self.accent_color))
    
    def style_frame(self, frame):
        frame.configure(bg=self.bg_color, padx=10, pady=10)
    
    def style_checkbox(self, checkbox):
        checkbox.configure(
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.font,
            selectcolor=self.accent_color
        )

class GridDrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid Drawing App")
        self.style = ModernStyle()
        
        self.cell_size = 30
        self.grid_size = 20
        self.color = self.style.accent_color
        self.line_width = 3
        self.dots = []
        self.lines = []
        self.intermediate_points = {}
        
        # Configure main window
        self.root.configure(bg=self.style.bg_color)
        
        # Create and style canvas
        self.canvas = tk.Canvas(
            root,
            width=self.cell_size*self.grid_size,
            height=self.cell_size*self.grid_size,
            bg=self.style.canvas_bg,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, padx=15, pady=15)
        self.draw_grid()
        
        # Create and style controls frame
        self.controls_frame = tk.Frame(root)
        self.style.style_frame(self.controls_frame)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
        
        # Title label
        title_label = tk.Label(
            self.controls_frame,
            text="Drawing Controls",
            font=("Helvetica", 14, "bold"),
            bg=self.style.bg_color,
            fg=self.style.fg_color
        )
        title_label.pack(pady=(0, 15))
        
        # Style and pack controls
        self.color_button = tk.Button(self.controls_frame, text="Choose Color", command=self.choose_color)
        self.style.style_button(self.color_button)
        self.color_button.pack(pady=8, fill=tk.X)
        
        # Style sliders
        slider_style = {
            "bg": self.style.bg_color,
            "fg": self.style.fg_color,
            "troughcolor": self.style.accent_color,
            "font": self.style.font
        }
        
        self.line_width_slider = tk.Scale(
            self.controls_frame,
            from_=1, to=10,
            orient=tk.HORIZONTAL,
            label="Line Width",
            **slider_style
        )
        self.line_width_slider.set(self.line_width)
        self.line_width_slider.pack(pady=8, fill=tk.X)
        
        self.speed_slider = tk.Scale(
            self.controls_frame,
            from_=50, to=500,
            orient=tk.HORIZONTAL,
            label="Animation Speed (px/s)",
            **slider_style
        )
        self.speed_slider.set(100)
        self.speed_slider.pack(pady=8, fill=tk.X)
        
        # Action buttons
        self.reset_button = tk.Button(self.controls_frame, text="Reset", command=self.reset)
        self.style.style_button(self.reset_button)
        self.reset_button.pack(pady=8, fill=tk.X)
        
        self.export_button = tk.Button(self.controls_frame, text="Export SVG", command=self.export_svg)
        self.style.style_button(self.export_button)
        self.export_button.pack(pady=8, fill=tk.X)
        
        # Checkboxes
        self.animated_var = tk.BooleanVar()
        self.animated_checkbox = tk.Checkbutton(
            self.controls_frame,
            text="Animated",
            variable=self.animated_var
        )
        self.style.style_checkbox(self.animated_checkbox)
        self.animated_checkbox.pack(pady=8)
        
        self.rounded_corners_var = tk.BooleanVar()
        self.rounded_corners_checkbox = tk.Checkbutton(
            self.controls_frame,
            text="Rounded Corners",
            variable=self.rounded_corners_var
        )
        self.style.style_checkbox(self.rounded_corners_checkbox)
        self.rounded_corners_checkbox.pack(pady=8)
        
        self.canvas.bind("<Button-3>", self.place_circle)
        self.canvas.bind("<ButtonPress-1>", self.start_line)
        self.canvas.bind("<B1-Motion>", self.draw_temp_points)
        self.canvas.bind("<ButtonRelease-1>", self.draw_line)
        self.root.bind("<l>", self.print_intermediate_points)  # Lier la touche "L" à l'événement

    def draw_grid(self):
        for i in range(self.grid_size + 1):
            self.canvas.create_line(
                i * self.cell_size, 0,
                i * self.cell_size, self.grid_size * self.cell_size,
                fill=self.style.grid_color,
                width=1,
                dash=(2, 4)
            )
            self.canvas.create_line(
                0, i * self.cell_size,
                self.grid_size * self.cell_size, i * self.cell_size,
                fill=self.style.grid_color,
                width=1,
                dash=(2, 4)
            )
    
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
    
    def calculate_grid_boundaries(self):
        # Calculate the actual grid boundaries
        first_cell_x = self.cell_size // 2
        first_cell_y = self.cell_size // 2
        last_cell_x = (self.grid_size * self.cell_size) - (self.cell_size // 2)
        last_cell_y = (self.grid_size * self.cell_size) - (self.cell_size // 2)
        return first_cell_x, first_cell_y, last_cell_x, last_cell_y

    def export_static_svg(self):
        # Get grid boundaries
        first_cell_x, first_cell_y, last_cell_x, last_cell_y = self.calculate_grid_boundaries()
        width = last_cell_x - first_cell_x + self.cell_size
        height = last_cell_y - first_cell_y + self.cell_size
        
        dwg = draw.Drawing(width, height)

        # Adjust coordinates relative to grid boundaries
        for line in self.lines:
            if line and isinstance(line[0], tuple):
                for i in range(len(line) - 1):
                    start_x, start_y = line[i]
                    end_x, end_y = line[i+1]
                    dwg.append(draw.Line(sx=start_x - first_cell_x, sy=start_y - first_cell_y, 
                                       ex=end_x - first_cell_x, ey=end_y - first_cell_y, 
                                       stroke=self.color, stroke_width=self.line_width_slider.get(),
                                       stroke_linecap='round' if self.rounded_corners_var.get() else 'butt'))
        
        # Adjust circle coordinates
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    dwg.append(draw.Circle(cx=x - first_cell_x, cy=y - first_cell_y, 
                                         r=(self.line_width_slider.get() * 3) // 2, fill=self.color))

        dwg.save_svg('output.svg')
        print("Exported to output.svg")

    def export_animated_svg(self):
        # Get grid boundaries
        first_cell_x, first_cell_y, last_cell_x, last_cell_y = self.calculate_grid_boundaries()
        width = last_cell_x - first_cell_x + self.cell_size
        height = last_cell_y - first_cell_y + self.cell_size
        
        dwg = draw.Drawing(width, height)

        # Adjust circle coordinates
        for line in self.lines:
            for item in line:
                if isinstance(item, tuple) and len(item) == 3 and item[2] == 'circle':
                    x, y, _ = item
                    dwg.append(draw.Circle(cx=x - first_cell_x, cy=y - first_cell_y, 
                                         r=(self.line_width_slider.get() * 3) // 2, fill=self.color))

        speed = self.speed_slider.get()

        for line in self.lines:
            if line and isinstance(line[0], tuple):
                line_elem = draw.Path(stroke=self.color, stroke_width=self.line_width_slider.get(), 
                                    fill='none', stroke_linecap='round' if self.rounded_corners_var.get() else 'butt',
                                    stroke_linejoin='round' if self.rounded_corners_var.get() else 'miter')

                # Adjust first coordinate
                line_elem.M(line[0][0] - first_cell_x, line[0][1] - first_cell_y)

                line_length = 0
                for i in range(1, len(line)):
                    line_length += ((line[i][0] - line[i-1][0])**2 + (line[i][1] - line[i-1][1])**2) ** 0.5
                
                duration = line_length / speed

                for i in range(1, len(line)):
                    line_elem.L(line[i][0] - first_cell_x, line[i][1] - first_cell_y)

                from_dasharray = f"1, {line_length * 1}"
                to_dasharray = f"{line_length * 1}, 0"
                line_elem.append_anim(
                    draw.Animate('stroke-dasharray', dur=f'{duration}s', values=f'{from_dasharray}; {to_dasharray}; {from_dasharray}', repeatCount="indefinite")
                )

                dwg.append(line_elem)

        dwg.save_svg('output_animated.svg')
        print("Exported to output_animated.svg")




    def print_intermediate_points(self, event):
        for key, value in self.intermediate_points.items():
            print(f"Line {key}: {value}")

# À la fin de ton code
if __name__ == "__main__":
    root = tk.Tk()
    app = GridDrawingApp(root)
    root.mainloop()  # Démarrer la boucle d'événements de Tkinter
