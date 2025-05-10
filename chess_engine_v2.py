
import chess as chess
import chess.engine


class GameState():
    def __init__(self, stockfish_path=None):
        #Chess Board is 8x8 square that is defined by positional numbers (0 - 63) and pieceType characters (R, K, q, Q, etc)
        self.chessBoard = chess.Board()
        self.move_log = []
        self.stockfish_engine = None
        self.stockfishDifficultyDict = {'1250': 1, '1350': 2, '1450': 3, '1550': 4, '1650': 5, '1750': 6, '1850': 7, '1950': 8, '2050': 9, '2150': 10,
                                    '2250': 11, '2350': 12, '2450': 13, '2550': 14, '2650': 15, '2750': 16, '2850': 17, '2950': 18, '3050': 19, '3150': 20} 
        self.stockfishDifficulty = '1250'  # Default difficulty level
        # Initialize the Stockfish engine if a path is provided
        if stockfish_path:
            self.initialize_stockfish(stockfish_path)


    def initialize_stockfish(self, stockfish_path):
        """
        Initializes the Stockfish engine with the given path.
        
        :param stockfish_path: Path to the Stockfish executable.
        """
        try:
            self.stockfish_engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            print("Stockfish initialized successfully.")
            self.stockfish_engine.configure({"Skill Level": self.stockfishDifficultyDict[self.stockfishDifficulty]})  # Set skill level to 10 (medium difficulty)
           
        except FileNotFoundError:
            print("Error: Stockfish executable not found. Check the path.")
            
    def set_stockfish_difficulty(self, difficulty):
        """
        Sets the Stockfish engine's difficulty level.
        
        :param difficulty: A string representing the desired difficulty (e.g., '1250', '1350').
        """
        if self.stockfish_engine:
            # Reconfigure the Stockfish engine with the new skill level
            skill_level = difficulty
            self.stockfish_engine.configure({"Skill Level": skill_level})
            reverse_dict = {v: k for k, v in self.stockfishDifficultyDict.items()}
            rating = reverse_dict.get(difficulty)
            print(f"Stockfish difficulty set to {rating} (Skill Level {difficulty}).")
            self.stockfishDifficulty = rating
        else:
            print(f"Invalid difficulty: {difficulty}. Please choose a valid difficulty.")

    def get_ai_move(self, time_limit=1.0):
        """
        Gets the best move from Stockfish for the current board position.
        :param time_limit: Time in seconds for Stockfish to calculate the move.
        :return: The best move as a chess.Move object.
        """
        if not self.stockfish_engine:
            print("Error: Stockfish engine is not initialized.")
            return None

        result = self.stockfish_engine.play(self.chessBoard, chess.engine.Limit(time=time_limit))
        return result.move


    def coordToChessSquare(self, coordinate):
        row = coordinate[0] # Grab coordniates from tuple
        col = coordinate[1]
        # Convert coordinates to chess square
        return chess.square_name(chess.square(col, 7 - row))

    def makeMove(self, start_coord, end_coord):

        start_square = self.coordToChessSquare(start_coord)  # Convert start coord to chess square
        end_square = self.coordToChessSquare(end_coord)      # Convert end coord to chess square

        start_square = self.coordToChessSquare(start_coord)  # Convert start coord to chess square
        end_square = self.coordToChessSquare(end_coord)      # Convert end coord to chess square

        self.move = chess.Move.from_uci(f'{start_square}{end_square}')  # Create move from UCI format (e.g., 'e2e4')

        # Check if the move is legal
        if self.move in self.chessBoard.legal_moves:

            # Record the move in SAN format before making it
            san_move = self.chessBoard.san(self.move)
            self.move_log.append(san_move)  # Add the SAN move to the move log

            # Make the move on the board
            self.chessBoard.push(self.move)  
            return True  # Move was successful
        else:
            if self.move:  # Ensure a move exists
                # Check if the piece being moved is a pawn
                piece = self.chessBoard.piece_at(self.move.from_square)
                if piece and piece.piece_type == chess.PAWN:
                    print(self.move)
                    # Check if the pawn is moving to the last rank
                    target_rank = chess.square_rank(self.move.to_square)
                    if (piece.color == chess.WHITE and target_rank == 7) or (piece.color == chess.BLACK and target_rank == 0):

                        return ('pawnPromotion', self.move)  # Pawn promotion detected
            return False  # Move was invalid

    def undoMove(self):
        if len(self.chessBoard.move_stack) > 0:
            self.chessBoard.pop()
            if self.move_log:
                self.move_log.pop()  # Remove the last move from the move log


    def getValidMoves(self, sqSelected):
        row, col = sqSelected
        square = chess.square(col, 7 - row)
        valid_moves = []

        for move in self.chessBoard.legal_moves:
            if move.from_square == square:
                # Convert the target square back to (row, col)
                target_row = 7 - chess.square_rank(move.to_square)
                target_col = chess.square_file(move.to_square)
                valid_moves.append((target_row, target_col))

        return valid_moves

    def check_game_status(self):
        """
        Checks if the current position is a checkmate, stalemate, or a draw.
        
        :param board: chess.Board object
        :return: A string describing the game state or None if the game is ongoing.
        """
        if self.chessBoard.is_checkmate():
            return "Checkmate"
        elif self.chessBoard.is_stalemate():
            return "Stalemate"
        elif self.chessBoard.is_insufficient_material():
            return "insufficient material"
        
        elif self.chessBoard.is_seventyfive_moves():
            return "75-move"
        elif self.chessBoard.is_fivefold_repetition():
            return "Fivefold"
        elif self.chessBoard.is_check():
            return "Check" #{'White' if self.chessBoard.turn == chess.WHITE else 'Black'} is in check.

        return None  # The game is still ongoing. (Alter this return value to test the game states)
        
    def doPawnPromotion(self, promotionPiece, promotionSquare):
        print("Pawn promotion detected")
        if promotionPiece and promotionSquare:
            # Convert the promotion square to chess board coordinates
            from_square = promotionSquare.from_square
            to_square = promotionSquare.to_square  

            # Create the promotion move
            move = chess.Move(from_square, to_square, promotion=promotionPiece)

            # Now, execute the move
            if move in self.chessBoard.legal_moves:
                self.chessBoard.push(move)
                print(f"Pawn promoted to {promotionPiece}")
            else:
                print("Invalid move.")

    def get_eval(self):
        """Get evaluation from Stockfish and normalize it."""
        info = self.stockfish_engine.analyse(self.chessBoard, chess.engine.Limit(time=0.1))
        score = info["score"].relative.score(mate_score=10000)  # Use high value for mate
        return max(-1000, min(1000, score)) / 1000  # Normalize to [-1,1]



    def close_stockfish(self):
        """
        Closes the Stockfish engine.
        """
        if self.stockfish_engine:
            self.stockfish_engine.quit()
            print("Stockfish engine closed.")