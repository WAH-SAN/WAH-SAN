import tkinter as tk
from tkinter import ttk
import chess
import chess.engine
import threading
from PIL import Image, ImageTk
import time
from datetime import datetime
import os
import math
import pytz

class AnalogClock:
    def __init__(self, canvas, center, size):
        self.canvas = canvas
        self.center = center
        self.size = size
        self.radius = size // 2
        self.hands = {}
        self.draw_face()
        self.update_time()

    def draw_face(self):
        x, y = self.center
        self.canvas.create_rectangle(x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill="black", outline="white")
        numerals = ['XII', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
        for i, numeral in enumerate(numerals):
            angle = math.radians(i * 30 - 90)
            numeral_x = x + math.cos(angle) * (self.radius - 15)
            numeral_y = y + math.sin(angle) * (self.radius - 15)
            self.canvas.create_text(numeral_x, numeral_y, text=numeral, fill="white", font=("Helvetica", 10))

    def draw_hand(self, angle, length, width, tag):
        angle_rad = math.radians(angle - 90)
        x, y = self.center
        end_x = x + length * math.cos(angle_rad)
        end_y = y + length * math.sin(angle_rad)
        self.canvas.delete(tag)
        self.hands[tag] = self.canvas.create_line(x, y, end_x, end_y, width=width, fill="white", tag=tag)

    def update_time(self):
        sydney_tz = pytz.timezone('Australia/Sydney')
        now = datetime.now(sydney_tz)
        hour = now.hour % 12 + now.minute / 60
        minute = now.minute + now.second / 60
        second = now.second

        self.draw_hand(hour * 30, self.radius * 0.5, 6, "hour")
        self.draw_hand(minute * 6, self.radius * 0.8, 4, "minute")
        self.draw_hand(second * 6, self.radius * 0.9, 2, "second")

        self.canvas.after(1000, self.update_time)

class ChessApp:
    def __init__(self, master):
        self.master = master
        self.master.title("WAH's Stockfish 16 v Stockfish 16 ♛")
        self.master.configure(bg="black")
        
        self.engine_path = r"C:\Users\wheth\Desktop\DEVELOPING\2024_Chess\stockfish\stockfish-windows-x86-64-modern"
        self.piece_image_path = r"C:\Users\wheth\Desktop\DEVELOPING\2024_Chess\allchesspiecesfile"
        self.square_size = 60
        self.board = chess.Board()
        self.move_counter = 0
        self.white_wins = 0
        self.black_wins = 0
        self.draws = 0
        
        # Define info_frame attribute here
        self.info_frame = tk.Frame(self.master, bg="black")
        self.info_frame.pack(side=tk.RIGHT, padx=10, anchor='n')
        self.moves_san = []  # Initialize the list to track moves in SAN here
        self.setup_gui()  # Call setup_gui method to initialize GUI components
        self.piece_images = self.load_piece_images()
        self.update_gui()  # Update GUI after loading piece images
        self.thread = threading.Thread(target=self.game_loop)
        self.thread.daemon = True
        self.thread.start()

    def setup_gui(self):
        self.canvas = tk.Canvas(self.master, width=480, height=480, bg="light gray")  # Set background color to light gray
        self.canvas.pack(side=tk.LEFT)
        
        self.clock_canvas = tk.Canvas(self.info_frame, width=200, height=200, bg='black')
        self.clock_canvas.pack(padx=10, pady=10)
        self.clock = AnalogClock(self.clock_canvas, (100, 100), 180)

        self.setup_game_stats_ui()

    # Rest of the ChessApp class...

    def setup_menu(self):
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)
        
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)
        
        self.modern_defence_active = tk.BooleanVar()
        self.modern_defence_active.set(False)  # Modern Defence is off by default
        self.options_menu.add_checkbutton(label="Modern Defence", onvalue=True, offvalue=False, variable=self.modern_defence_active, command=self.toggle_modern_defence)
        
        self.game_active = True  # Assuming you want to control game loop with this flag


    # Rest of the ChessApp class...
            

    def setup_gui(self):
        self.canvas = tk.Canvas(self.master, width=480, height=480, bg="light gray")  # Set background color to light gray
        self.canvas.pack(side=tk.LEFT)
        self.info_frame = tk.Frame(self.master, bg="black")
        self.info_frame.pack(side=tk.RIGHT, padx=10, anchor='n')

        self.clock_canvas = tk.Canvas(self.info_frame, width=200, height=200, bg='black')
        self.clock_canvas.pack(padx=10, pady=10)
        self.clock = AnalogClock(self.clock_canvas, (100, 100), 180)
        self.setup_menu()  # Add this line at the end of your existing setup_gui method

        self.setup_game_stats_ui()

    def setup_game_stats_ui(self):
        # Speed Slider setup
        self.speed_slider = tk.Scale(self.info_frame, from_=0.1, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, bg="black", fg="white", label="Move Speed")
        self.speed_slider.set(1)
        self.speed_slider.pack(fill='x', pady=5)
        self.most_recent_move_label = tk.Label(self.info_frame, text="Most Recent Move: N/A", fg="white", bg="black")
        self.most_recent_move_label.pack(fill='x', pady=5)
        
        # Labels for game statistics
        self.move_counter_label = tk.Label(self.info_frame, text="Move Counter: 0", fg="white", bg="black")
        self.move_counter_label.pack(fill='x', pady=5)
        
        self.white_wins_label = tk.Label(self.info_frame, text="White Wins: 0", fg="white", bg="black")
        self.white_wins_label.pack(fill='x', pady=5)
        
        self.black_wins_label = tk.Label(self.info_frame, text="Black Wins: 0", fg="white", bg="black")
        self.black_wins_label.pack(fill='x', pady=5)
        
        self.draws_label = tk.Label(self.info_frame, text="Draws: 0", fg="white", bg="black")
        self.draws_label.pack(fill='x', pady=5)
        
        self.eval_label = tk.Label(self.info_frame, text="Evaluation: N/A", fg="white", bg="black")
        self.eval_label.pack(fill='x', pady=5)

    def load_piece_images(self):
        piece_images = {}
        pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
        for piece in pieces:
            image_path = os.path.join(self.piece_image_path, f'{piece}.png')
            print(f"Loading image from: {image_path}")  # Debug print
            image = Image.open(image_path).convert('RGBA')
            image = image.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
            piece_images[piece] = ImageTk.PhotoImage(image)
            print(f"Loaded {piece}")  # Confirmation print
        return piece_images

    def translate_move_limit(self):
        slider_time = self.speed_slider.get()
        translated_time = slider_time * 1000
        #print(slider_time)
        #print(translated_time)
        return translated_time #translated time is a variable

    def update_gui(self):
        self.draw_board()  # Draw the board after loading piece images
        self.master.after(int(self.translate_move_limit()), self.update_gui) #ref own object = 'self.X''



    def draw_board(self):
        #print("Drawing board...")  # Debug print
        self.canvas.delete("all")
        colors = {True: "#F0D9B5", False: "#006400"}  # Light square: Tan, Dark square: Dark Green

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2 == 0]
                x1, y1 = col * self.square_size, row * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_symbol = piece.symbol()
                if piece_symbol.upper() == piece_symbol:
                    piece_symbol = 'w' + piece_symbol
                else:
                    piece_symbol = 'b' + piece_symbol.upper()
                self.draw_piece(square, piece_symbol)

    def draw_piece(self, square, piece_symbol):
        #print(f"Drawing piece at square {square}...")  # Debug print
        x = chess.square_file(square) * self.square_size
        y = (7 - chess.square_rank(square)) * self.square_size
        self.canvas.create_image(x, y, image=self.piece_images[piece_symbol], anchor=tk.NW)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~GAME LOOP
   # Right before your game loop, initialize a list to track moves in SAN
    
    def game_loop(self):
        while True:
            self.reset_game()
            self.moves_san = []  # Reinitialize for tracking moves in SAN for the new game
            self.game_active = True
            with chess.engine.SimpleEngine.popen_uci(self.engine_path) as engine:
                while not self.board.is_game_over(claim_draw=True) and self.game_active:
                    # Implement Modern Defence if selected
                    if self.modern_defence_active.get():
                        if self.board.fullmove_number == 1 and self.board.turn == chess.BLACK and "g6" not in self.moves_san:
                            self.board.push_san("g6")
                            self.moves_san.append("g6")
                            self.update_gui()
                            continue
                        elif self.board.fullmove_number == 2 and self.board.turn == chess.BLACK and "Bg7" not in self.moves_san and "g6" in self.moves_san:
                            self.board.push_san("Bg7")
                            self.moves_san.append("Bg7")
                            self.update_gui()
                            continue
                    
                    # Engine play
                    time_limit = self.speed_slider.get()
                    result = engine.play(self.board, chess.engine.Limit(time=time_limit))
                    move_san = self.board.san(result.move)
                    self.moves_san.append(move_san)
                    self.board.push(result.move)
                    
                    # Update GUI and game state
                    self.move_counter += 1
                    self.update_move_counter_label()
                    self.update_moves_label(move_san)
                    self.update_evaluation(engine)
                    
                    # Check for draw conditions explicitly
                    if self.board.can_claim_threefold_repetition():
                        print("Draw by threefold repetition")
                        self.draws += 1
                        self.update_game_stats_ui()
                        break
                    if self.board.can_claim_fifty_moves():
                        print("Draw by fifty-move rule")
                        self.draws += 1
                        self.update_game_stats_ui()
                        break
                    if self.board.is_stalemate():
                        print("Draw by stalemate")
                        self.draws += 1
                        self.update_game_stats_ui()
                        break
                    if self.board.is_insufficient_material():
                        print("Draw by insufficient material")
                        self.draws += 1
                        self.update_game_stats_ui()
                        break

                    # Handle game over conditions
                    if self.board.is_game_over():
                        result = self.board.result()
                        if result == "1-0":
                            self.white_wins += 1
                            print("White wins by checkmate")
                        elif result == "0-1":
                            self.black_wins += 1
                            print("Black wins by checkmate")
                        else:
                            self.draws += 1
                            print("Game ended in a draw")
                        self.update_game_stats_ui()
                        time.sleep(2)  # Pause before next game
                        break

    def update_game_stats_ui(self):
        # Update your UI to reflect the new draw/win counters
        self.move_counter_label.config(text=f"Move Counter: {self.move_counter}")
        self.white_wins_label.config(text=f"White Wins: {self.white_wins}")
        self.black_wins_label.config(text=f"Black Wins: {self.black_wins}")
        self.draws_label.config(text=f"Draws: {self.draws}")
        self.eval_label.config(text="Evaluation: N/A")  # Reset or update evaluation as needed

    def toggle_modern_defence(self):
        # Toggle Modern Defence functionality
        print("Modern Defence Toggled:", self.modern_defence_active.get())

    def update_moves_label(self, move_san):
        # Directly use the move_san string, which is already in SAN format
        self.most_recent_move_label.config(text=f"Most Recent Move: {move_san}")

    def update_evaluation(self, engine):
        info = engine.analyse(self.board, chess.engine.Limit(time=0.1))
        score = info["score"].white() if info.get("score") else None
        eval_str = "Evaluation: N/A"
        if score is not None:
            # Convert score to a centipawn value if possible, otherwise show mate score
            if score.is_mate():
                eval_str = "Evaluation: Mate in {}".format(score.mate())
            else:
                eval_str = "Evaluation: {:.2f}".format(score.score() / 100.0)
        self.eval_label.config(text=eval_str)

    def reset_game(self):
        self.board.reset()
        self.move_counter = 0
        self.most_recent_move_label.config(text="Most Recent Move: N/A")
        self.eval_label.config(text="Evaluation: N/A")

    def update_move_counter_label(self):
        self.move_counter_label.config(text=f"Move Counter: {self.move_counter}")

    def update_winner_label(self):
        result = self.board.result()
        if result == "1-0":
            self.white_wins += 1
            self.white_wins_label.config(text=f"White Wins: {self.white_wins}")
        elif result == "0-1":
            self.black_wins += 1
            self.black_wins_label.config(text=f"Black Wins: {self.black_wins}")
        elif result == "1/2-1/2":
            self.draws += 1
            self.draws_label.config(text=f"Draws: {self.draws}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
