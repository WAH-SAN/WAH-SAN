import tkinter as tk
from tkinter import Button
import pyautogui
import os

class CaptureTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.rect = None
        self.initial_x = None
        self.initial_y = None
        self.configure_window()
        self.output_directory = r'C:\Users\wheth\Desktop\DEVELOPING\chessboard-recognizer-master\chessboard_png'
        self.output_filename = 'chessboard.png'
        # Ensure the output directory exists
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        self.bind_mouse_events()  # Setup mouse event bindings for drawing

    def configure_window(self):
        self.title("WAH's Reticle")
        self.geometry("800x600")
        self.canvas = tk.Canvas(self, cursor="cross", bg='red', highlightthickness=2, highlightbackground="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.attributes('-alpha', 0.3)  # Make the window semi-transparent

        # Capture button placed at the bottom
        self.capture_btn = Button(self, text="Capture", command=self.capture_area)
        self.capture_btn.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_mouse_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.extend_draw)

    def start_draw(self, event):
        # Reset rectangle
        if self.rect is not None:
            self.canvas.delete(self.rect)
        self.initial_x = event.x
        self.initial_y = event.y
        self.rect = self.canvas.create_rectangle(self.initial_x, self.initial_y, event.x, event.y, outline="black")

    def extend_draw(self, event):
        self.canvas.coords(self.rect, self.initial_x, self.initial_y, event.x, event.y)

    def capture_area(self):
        if self.rect:  # Ensure a selection has been made
            x0, y0, x1, y1 = self.canvas.coords(self.rect)
            if x1 > x0 and y1 > y0:  # Ensure coordinates are valid
                self.withdraw()  # Hide the window
                img = pyautogui.screenshot(region=(self.winfo_rootx() + x0, self.winfo_rooty() + y0, x1 - x0, y1 - y0))
                img.save(os.path.join(self.output_directory, self.output_filename))
                print(f"Screenshot saved to {os.path.join(self.output_directory, self.output_filename)}")
                self.after(100, lambda: self.attributes('-alpha', 0.3))  # Make window visible again
            else:
                print("Invalid selection area.")
        else:
            print("No selection made.")

if __name__ == "__main__":
    app = CaptureTool()
    app.mainloop()
