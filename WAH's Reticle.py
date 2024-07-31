import tkinter as tk
from tkinter import Button
import pyautogui
import os

# Set the directory where the chessboard image will be saved
output_directory = r'C:\Users\wheth\Desktop\DEVELOPING\chessboard-recognizer-master\chessboard_png'
output_filename = 'chessboard.png'

class ResizableReticle(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WAH's Reticle ♔")
        self.geometry("400x400")  # Initial size of the reticle

        self.canvas = tk.Canvas(self, cursor="cross", bg='white', highlightthickness=2, highlightbackground="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.capture_btn = Button(self, text="Capture", command=self.capture_area)
        self.capture_btn.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.bind("<Configure>", self.draw_grid_and_border)

    def draw_grid_and_border(self, event=None):
        self.canvas.delete("grid_line")
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        for i in range(1, 8):
            self.canvas.create_line((width / 8) * i, 0, (width / 8) * i, height, fill="black", tags="grid_line")
            self.canvas.create_line(0, (height / 8) * i, width, (height / 8) * i, fill="black", tags="grid_line")
        self.canvas.create_rectangle(2, 2, width-2, height-2, outline="white", tags="grid_line")

    def capture_area(self):
        self.withdraw()
        self.after(500, self.delayed_capture)

    def delayed_capture(self):
        x = self.winfo_rootx() + self.canvas.winfo_x()
        y = self.winfo_rooty() + self.canvas.winfo_y()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        image = pyautogui.screenshot(region=(x, y, width, height))

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        output_path = os.path.join(output_directory, output_filename)
        image.save(output_path)
        print(f"Saved screenshot to {output_path}")

        self.deiconify()
        self.attributes("-alpha", 0.5)

if __name__ == "__main__":
    app = ResizableReticle()
    app.attributes("-alpha", 0.5)
    app.mainloop()
