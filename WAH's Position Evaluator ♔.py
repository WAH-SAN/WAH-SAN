import tkinter as tk
from PIL import Image, ImageTk
import os
import chess
import subprocess
import threading

# Add Stockfish path to the system PATH variable
os.environ["PATH"] += os.pathsep + r'C:\Users\wheth\Desktop\DEVELOPING\2024_Chess\stockfish'

# Set the path to the folder containing the piece images
pieces_path = r'C:\Users\wheth\Desktop\DEVELOPING\2024_Chess\allchesspiecesfile'
stockfish_path = r'C:\Users\wheth\Desktop\DEVELOPING\2024_Chess\stockfish\stockfish-windows-x86-64-modern'

class ChessboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WAH's Position Evaluator ♔")
        self.root.geometry("700x550")

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='white')
        self.canvas.pack(side=tk.LEFT)

        self.right_frame = tk.Frame(self.root, bg='lightgray')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.piece_images = {}
        self.draw_chessboard()
        self.load_pieces()

        self.selected_piece = None
        self.selected_square = None
        self.placed_pieces = {}
        self.board = chess.Board(None)  # Start with an empty board for custom setup

        self.side_to_move = tk.StringVar(value='white')

        self.move_menu = tk.OptionMenu(self.right_frame, self.side_to_move, 'white', 'black', command=self.update_side_to_move)
        self.move_menu.grid(row=0, column=0, columnspan=2, pady=10)

        self.undo_button = tk.Button(self.right_frame, text="Undo", command=self.undo_last_move)
        self.undo_button.grid(row=1, column=0, pady=10)

        self.clear_button = tk.Button(self.right_frame, text="Clear", command=self.clear_board)
        self.clear_button.grid(row=1, column=1, pady=10)

        self.setup_complete_button = tk.Button(self.right_frame, text="Setup Complete", command=self.switch_to_play_mode)
        self.setup_complete_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.recommended_move_text = tk.Text(self.right_frame, height=4, width=20, state=tk.DISABLED)
        self.recommended_move_text.grid(row=3, column=0, columnspan=2, pady=10)

        self.canvas.bind("<Button-1>", self.select_or_place_piece)

        self.suggested_move = None
        self.is_setup_complete = False  # Flag to check if setup is complete

    def switch_to_play_mode(self):
        self.is_setup_complete = True
        self.evaluate_current_position()
        # Reset selected piece to ensure the board is ready for play
        self.selected_piece = None
        self.board.turn = chess.WHITE  # Ensure the board starts with White's turn

    def select_or_place_piece(self, event):
        if not self.is_setup_complete:
            # Handle piece selection and placement during setup
            self.handle_piece_selection(event)
        else:
            # Handle piece movement during play
            self.handle_piece_movement(event)

    def handle_piece_selection(self, event):
        col, row = event.x // 50, event.y // 50
        square = chess.square(col, 7 - row)
        if self.selected_piece:
            self.place_piece(square)
        else:
            # Select square if a piece is clicked; prepare for move in play mode
            piece = self.board.piece_at(square)
            if piece:
                self.selected_square = square

    def handle_piece_movement(self, event):
        if not self.is_setup_complete:
            return  # Ignore if setup is not complete
        col, row = event.x // 50, event.y // 50
        square = chess.square(col, 7 - row)
        if self.selected_square is None and self.board.piece_at(square) is not None:
            self.selected_square = square
        elif self.selected_square is not None:
            self.attempt_move(self.selected_square, square)

    def attempt_move(self, from_square, to_square):
        move = chess.Move(from_square, to_square)
        if move in self.board.legal_moves:
            self.board.push(move)
            self.selected_square = None
            self.refresh_board_from_board_state()
            self.evaluate_current_position()
        else:
            self.selected_square = None  # Deselect if the move is illegal

    # Other methods (draw_chessboard, load_pieces, place_piece, refresh_board_from_board_state, place_image_at_square, undo_last_move, clear_board, evaluate_current_position, evaluate_position, read_stockfish_output, update_recommended_move_text, update_side_to_move) remain unchanged.


    def draw_chessboard(self):
        square_size = 50
        # Switch the colors by reversing their assignment
        colors = ['#e0e0e0', '#008000']  # Light color first, then dark color
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = col * square_size, row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=f"square{row}{col}")
                self.canvas.create_text(x1 + 25, y1 + 25, text=f'{chr(65 + col)}{8 - row}', fill='black')


    def load_pieces(self):
        piece_names = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
        row = 4  # Start row for piece selection in the right frame
        for i, piece_name in enumerate(piece_names):
            piece_image = Image.open(os.path.join(pieces_path, f'{piece_name}.png')).convert("RGBA")
            piece_image = piece_image.resize((40, 40), Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(piece_image)
            self.piece_images[piece_name] = photo_image
            button = tk.Button(self.right_frame, image=photo_image, command=lambda pn=piece_name: self.select_piece(pn))
            button.grid(row=row + i // 2, column=i % 2, pady=2, padx=2, sticky="nsew")

    def select_piece(self, piece_name):
        self.selected_piece = piece_name
        self.selected_square = None  # Reset selected square to allow piece placement

    def place_piece(self, square):
        if self.selected_piece and not self.board.piece_at(square):
            piece_symbol = self.selected_piece[1].upper() if self.selected_piece[0] == 'w' else self.selected_piece[1].lower()
            piece = chess.Piece.from_symbol(piece_symbol)
            self.board.set_piece_at(square, piece)
            # Track piece placement for undo functionality during setup
            self.placed_pieces[square] = piece_symbol
            self.refresh_board_from_board_state()


    def refresh_board_from_board_state(self):
        self.canvas.delete("all")
        self.draw_chessboard()
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = 'w' if piece.color == chess.WHITE else 'b'
                piece_name = f'{color}{piece.symbol().upper()}'
                self.place_image_at_square(piece_name, square)

    def place_image_at_square(self, piece_name, square):
        col, row = chess.square_file(square), chess.square_rank(square)
        x, y = col * 50 + 25, (7 - row) * 50 + 25
        piece_image = self.piece_images[piece_name]
        self.canvas.create_image(x, y, image=piece_image, tags=f"piece{square}")


    def clear_board(self):
        self.board.clear_board()
        self.placed_pieces.clear()
        self.refresh_board_from_board_state()

    def evaluate_current_position(self):
        # Get the FEN string of the current board position
        fen = self.board.fen()
        # Start the evaluation of this position
        self.evaluate_position(fen, 'w' if self.board.turn else 'b')

    def evaluate_position(self, fen, side):
        self.thinking_time = 5  # Set thinking time (in seconds)
        stockfish = subprocess.Popen(
            [stockfish_path],
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        commands = f'position fen {fen}\ngo movetime {self.thinking_time * 1000}\n'
        stockfish.stdin.write(commands)
        stockfish.stdin.flush()

        self.update_thinking_countdown(self.thinking_time)  # Start the countdown
        threading.Thread(target=self.read_stockfish_output, args=(stockfish,)).start()

    def update_thinking_countdown(self, remaining_time):
        if remaining_time >= 0:
            self.recommended_move_text.config(state=tk.NORMAL)
            self.recommended_move_text.delete("2.0", tk.END)  # Clear the countdown area
            self.recommended_move_text.insert(tk.END, f"\nThinking: {remaining_time}s")
            self.recommended_move_text.config(state=tk.DISABLED)
            self.root.after(1000, lambda: self.update_thinking_countdown(remaining_time - 1))  # Update every second

    def read_stockfish_output(self, stockfish):
        depth_info = ""
        while True:
            line = stockfish.stdout.readline().strip()
            if "bestmove" in line:
                best_move = line.split()[1]
                if best_move == "(none)":
                    best_move_str = "No move found"
                else:
                    move = self.board.parse_uci(best_move)
                    best_move_str = self.board.san(move)
                break
            elif "info" in line and "depth" in line:
                depth_info = line

        self.root.after(0, lambda: self.update_recommended_move_text(best_move_str, depth_info))

    def update_recommended_move_text(self, best_move_str, depth_info=""):
        self.recommended_move_text.config(state=tk.NORMAL)
        self.recommended_move_text.delete("1.0", "2.0")  # Clear previous best move and countdown
        self.recommended_move_text.insert("1.0", f"Best Move: {best_move_str}\n")
        self.recommended_move_text.config(state=tk.DISABLED)
        # Optionally update depth_info; removed for clarity in this example



    def update_recommended_move_text_live(self, info_line):
        # This method updates the GUI with Stockfish's current best evaluation live
        self.root.after(0, lambda: self.recommended_move_text.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.recommended_move_text.delete("1.0", tk.END))
        self.root.after(0, lambda: self.recommended_move_text.insert(tk.END, info_line))
        self.root.after(0, lambda: self.recommended_move_text.config(state=tk.DISABLED))


    def update_side_to_move(self, _=None):
        # Ensure the board's turn matches the selected option
        self.board.turn = chess.WHITE if self.side_to_move.get() == 'white' else chess.BLACK

    def switch_to_play_mode(self):
        self.is_setup_complete = True
        # Ensure the board starts with the correct side's turn according to the user's selection
        self.board.turn = chess.WHITE if self.side_to_move.get() == 'white' else chess.BLACK
        self.evaluate_current_position()
        # Reset selected piece and square to ensure the board is ready for play
        self.selected_piece = None
        self.selected_square = None
        self.refresh_board_from_board_state()



    def undo_last_move(self):
        if not self.is_setup_complete:
            # Undo piece placement during setup
            if self.placed_pieces:
                last_square = list(self.placed_pieces.keys())[-1]
                self.board.remove_piece_at(last_square)
                del self.placed_pieces[last_square]
        else:
            # Undo a move during play
            if self.board.move_stack:
                self.board.pop()

        self.refresh_board_from_board_state()
        if self.is_setup_complete:
            # Re-evaluate position after undo during play mode
            self.evaluate_current_position()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessboardApp(root)
    root.mainloop()
