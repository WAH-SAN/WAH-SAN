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
        self.root.geometry("700x700")

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg='white')
        self.canvas.pack(side=tk.LEFT, padx=(10, 0))

        self.right_frame = tk.Frame(self.root, bg='lightgray', width=300, height=700)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.piece_images = {}
        self.is_flipped = False
        self.selected_piece = None
        self.selected_square = None
        self.board = chess.Board(None)
        self.is_setup_complete = False

        self.top_right_coordinate = 'H8'  # Default top right coordinate
        self.initialize_top_right_coordinate_button()

        self.load_pieces()
        self.initialize_ui_elements()


    def initialize_ui_elements(self):
        self.fen_input = tk.Entry(self.right_frame, width=20)
        self.fen_input.pack(pady=5)

        self.load_fen_button = tk.Button(self.right_frame, text="Load FEN", command=self.load_fen_position)
        self.load_fen_button.pack(pady=5)

        self.side_to_move_var = tk.StringVar(value='White')
        self.side_to_move_menu = tk.OptionMenu(self.right_frame, self.side_to_move_var, 'White', 'Black', command=self.update_side_to_move)
        self.side_to_move_menu.pack(pady=5)

        # Add the Flip Board button
        self.flip_board_button = tk.Button(self.right_frame, text="Flip Board", command=self.flip_board)
        self.flip_board_button.pack(pady=5)

        self.setup_complete_button = tk.Button(self.right_frame, text="Setup Complete", command=self.switch_to_play_mode)
        self.setup_complete_button.pack(pady=5)

        self.undo_button = tk.Button(self.right_frame, text="Undo", command=self.undo_last_move)
        self.undo_button.pack(pady=5)

        self.clear_button = tk.Button(self.right_frame, text="Clear", command=self.clear_board)
        self.clear_button.pack(pady=5)

        self.recommended_move_text = tk.Text(self.right_frame, height=4, width=25, state=tk.DISABLED)
        self.recommended_move_text.pack(pady=5)

        self.canvas.bind("<Button-1>", self.select_or_place_piece)
        self.draw_chessboard()
        # Existing initialization code...
        





        # Initialize other UI elements as before...

    def update_side_to_move(self, _=None):
        self.board.turn = chess.WHITE if self.side_to_move_var.get() == 'white' else chess.BLACK
        self.is_flipped = self.board.turn == chess.BLACK  # Update board orientation
        self.refresh_board_from_board_state()
        if self.is_setup_complete:
            self.evaluate_current_position()  # Re-evaluate position if setup is complete


    def switch_to_play_mode(self):
        self.is_setup_complete = True
        self.refresh_board_from_board_state()

    # Include other corrected methods as before...

    def select_or_place_piece(self, event):
        if not self.is_setup_complete:
            # Setup mode logic remains unchanged.
            ...
        else:
                    # Handle continuous gameplay.
            # Calculate the clicked square based on the event coordinates
            col, row = event.x // 50, event.y // 50
            # Adjust the square calculation if the board is flipped
            square = chess.square(col, 7 - row) if self.is_flipped else chess.square(col, row)
            # Continue with the logic to select or place a piece
            if self.selected_square:
                self.attempt_move(self.selected_square, square)
            else:
                piece = self.board.piece_at(square)
                if piece and piece.color == self.board.turn:
                    self.selected_square = square





    def handle_piece_selection_during_setup(self, square):
        # Assuming you have a method to get a piece type from a user selection or similar
        piece = self.get_selected_piece_type()
        if piece:
            self.board.set_piece_at(square, piece)
            self.refresh_board_from_board_state()

    def handle_piece_movement_during_play(self, square):
        if self.selected_square and square != self.selected_square:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.refresh_board_from_board_state()
            self.selected_square = None  # Reset the selection regardless of move legality
        else:
            self.selected_square = square  # Select the square if no piece was previously selected


    # Include other methods as before...

    def refresh_board_from_board_state(self):
        self.canvas.delete("all")
        self.is_flipped = self.board.turn == chess.BLACK  # Automatically set based on turn
        self.draw_chessboard()
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                self.place_image_at_square(self.get_piece_image_name(piece), square)



    def get_piece_image_name(self, piece):
        # This method should return the filename or key for the piece's image
        color = 'w' if piece.color == chess.WHITE else 'b'
        return f"{color}{piece.symbol().upper()}"

    def get_selected_piece_type(self):
        # Placeholder for actual logic to determine the selected piece type
        # This could be based on user input from another part of the UI
        pass




    def draw_chessboard(self):
        square_size = 50
        colors = ['#e0e0e0', '#008000']
        for row in range(8):
            for col in range(8):
                adjusted_row, adjusted_col = (7 - row, col) if self.is_flipped else (row, col)
                color = colors[(row + col) % 2]
                x1, y1 = adjusted_col * square_size, adjusted_row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                coord_text = f'{chr(97 + col)}{8 - row}' if not self.is_flipped else f'{chr(97 + (7-col))}{row+1}'
                self.canvas.create_text(x1 + 25, y1 + 25, text=coord_text, fill='black')

    # Ensure to define load_fen_position, load_pieces, select_piece, place_piece, undo_last_move, evaluate_current_position, evaluate_position, read_stockfish_output, update_recommended_move_text, update_side_to_move methods.
    def flip_board(self):
        """Flips the board visually without affecting the game state."""
        self.is_flipped = not self.is_flipped
        self.refresh_board_from_board_state()




    def switch_to_play_mode(self):
        self.is_setup_complete = True
        self.evaluate_current_position()
        # Reset selected piece to ensure the board is ready for play
        self.selected_piece = None
        self.board.turn = chess.WHITE  # Ensure the board starts with White's turn

    def select_or_place_piece(self, event):
        if not self.is_setup_complete:
            # Handle piece selection and placement during setup
            col, row = event.x // 50, event.y // 50
            square = chess.square(col, 7 - row)
            if self.selected_piece:
                self.place_piece(square)
            else:
                piece = self.board.piece_at(square)
                if piece:
                    self.selected_square = square
                    # Add any additional setup mode logic here
        else:
            # Handle piece movement during play
            col, row = event.x // 50, event.y // 50
            square = chess.square(col, 7 - row)
            if self.selected_square is None and self.board.piece_at(square) is not None:
                self.selected_square = square
                # Logic for when a piece is selected but not yet moved
            elif self.selected_square is not None:
                self.attempt_move(self.selected_square, square)
                # Logic for attempting to move a piece


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
            # Clear the selected square after making a move
            self.selected_square = None
            # Update the board orientation based on the current player
            self.is_flipped = self.board.turn == chess.BLACK
            # Refresh the board to reflect the new game state
            self.refresh_board_from_board_state()
            # Trigger a new evaluation of the position
            self.evaluate_current_position()
        else:
            # Clear the selection if the move is illegal
            self.selected_square = None



    # Other methods (draw_chessboard, load_pieces, place_piece, refresh_board_from_board_state, place_image_at_square, undo_last_move, clear_board, evaluate_current_position, evaluate_position, read_stockfish_output, update_recommended_move_text, update_side_to_move) remain unchanged.


    def draw_chessboard(self):
        self.canvas.delete("all")  # Clear the canvas first
        colors = ['#e0e0e0', '#008000']  # Define colors for the squares
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                x1, y1 = (col * 50, row * 50) if not self.is_flipped else ((7 - col) * 50, (7 - row) * 50)
                x2, y2 = x1 + 50, y1 + 50
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                # Additional logic for labels, if necessary



    def load_pieces(self):
        # Define the list of piece names based on the images you have
        piece_names = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']

        # Assuming this method needs adjustment
        piece_frame = tk.Frame(self.right_frame)  # Create a new frame for pieces
        piece_frame.pack(pady=5)  # Pack the frame within self.right_frame

        # Now use pack() within piece_frame for each piece button
        for i, piece_name in enumerate(piece_names):
            piece_image = Image.open(os.path.join(pieces_path, f'{piece_name}.png')).convert("RGBA")
            piece_image = piece_image.resize((40, 40), Image.Resampling.LANCZOS)
            photo_image = ImageTk.PhotoImage(piece_image)
            self.piece_images[piece_name] = photo_image
            # This lambda captures the current value of piece_name by defaulting it in the function definition
            button = tk.Button(piece_frame, image=photo_image, command=lambda pn=piece_name: self.select_piece(pn))
            button.pack(side=tk.TOP, pady=2)  # Adjust packing as needed
            # This ensures the reference to photo_image is kept, preventing garbage collection
            button.photo = photo_image




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
        """Refreshes the board's visual state based on the current game state."""
        self.canvas.delete("all")
        self.draw_chessboard()  # Redraw the board with the current orientation
        
        # Place pieces on the board based on the current game state
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                self.place_image_at_square(self.get_piece_image_name(piece), square)




    def place_image_at_square(self, piece_name, square):
        # Adjust placement based on whether the board is flipped
        if not self.is_flipped:
            col, row = chess.square_file(square), chess.square_rank(square)
        else:
            col, row = 7 - chess.square_file(square), 7 - chess.square_rank(square)
        x, y = col * 50 + 25, row * 50 + 25
        image = self.piece_images[piece_name]
        self.canvas.create_image(x, y, image=image, tags=f"piece{square}")



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
        # This now only updates the turn for stockfish evaluation, not the board perspective
        turn = self.side_to_move_var.get().lower()
        self.board.turn = chess.WHITE if turn == 'white' else chess.BLACK
        if self.is_setup_complete:
            self.evaluate_current_position()



    def switch_to_play_mode(self):
        # This function is called after the FEN is loaded or the board is set up manually.
        self.is_setup_complete = True
        self.update_side_to_move()  # Ensure the board is flipped and evaluated based on side to move.




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




            
###################################################

    def switch_to_play_mode(self):
        self.is_setup_complete = True
        self.board.turn = chess.WHITE if self.side_to_move_var.get() == 'white' else chess.BLACK
        self.evaluate_current_position()

    def update_side_to_move(self, _=None):
        self.board.turn = chess.WHITE if self.side_to_move_var.get() == 'white' else chess.BLACK
        self.is_flipped = self.board.turn == chess.BLACK  # Flip board based on who's turn it is.
        self.refresh_board_from_board_state()
        if self.is_setup_complete:
            self.evaluate_current_position()  # Re-evaluate the position after updating the side to move.








    def load_fen_position(self):
        fen = self.fen_input.get()
        try:
            self.board.set_fen(fen)
            # Automatically adjust board orientation based on FEN turn
            self.is_flipped = self.board.turn == chess.BLACK
            self.refresh_board_from_board_state()
        except ValueError as e:
            print("Invalid FEN string:", e)

    def draw_chessboard(self):
        """Draws the chessboard based on the current state."""
        square_size = 50
        colors = ['#e0e0e0', '#008000']
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                if self.top_right_coordinate == 'H8':
                    x1, y1 = (col * square_size, row * square_size) if not self.is_flipped else ((7 - col) * square_size, (7 - row) * square_size)
                else:
                    x1, y1 = ((7 - col) * square_size, row * square_size) if not self.is_flipped else (col * square_size, (7 - row) * square_size)
                x2, y2 = x1 + square_size, y1 + square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                # Adjust coordinate text based on the current orientation and top right coordinate
                coord_text = self.calculate_coord_text(col, row)
                self.canvas.create_text(x1 + 5, y1 + 5, text=coord_text, anchor="nw", fill="black")

    def calculate_coord_text(self, col, row):
        """Calculates the coordinate text based on the board's configuration."""
        if self.top_right_coordinate == 'H8':
            if not self.is_flipped:
                return f'{chr(97 + col)}{8 - row}'
            else:
                return f'{chr(97 + (7 - col))}{row + 1}'
        else:
            if not self.is_flipped:
                return f'{chr(97 + (7 - col))}{8 - row}'
            else:
                return f'{chr(97 + col)}{row + 1}'


    def initialize_top_right_coordinate_button(self):
        """Initializes the button for selecting the top right coordinate."""
        self.top_right_coord_var = tk.StringVar(value='H8')
        self.top_right_coord_menu = tk.OptionMenu(self.right_frame, self.top_right_coord_var, 'A1', 'H8', command=self.update_top_right_coordinate)
        self.top_right_coord_menu.pack(pady=5)

    def update_top_right_coordinate(self, _=None):
        """Updates the internal state based on the top right coordinate selection."""
        self.top_right_coordinate = self.top_right_coord_var.get()
        self.refresh_board_from_board_state()  # Refresh the board to reflect the new orientation













if __name__ == "__main__":
    root = tk.Tk()
    app = ChessboardApp(root)
    root.mainloop()
