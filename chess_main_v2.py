
#Import Modules
import sys
import pygame as pg
import chess
import chess.engine
import numpy as np
import math 
import pygame_gui as pgui
import random


#Import files
import chess_engine_v2 as chess_engine
import button_logic


pg.init()

#Global Variables
global colors
colors = {'chessSquares': [pg.Color(235, 236, 211), pg.Color(125, 148, 93)], 'mainBackground': pg.Color("black"),
          'mainTabColor': pg.Color("dark grey"), 'aiBackground': pg.Color(219, 172, 52)}

# main screen and board variables
gameVersion = "v2.0.0"
gameTitle = "Chess " + gameVersion
SQ_SIZE = 80
DIMENSION = 8
WIDTH, HEIGHT = (SQ_SIZE * (DIMENSION+4)), (SQ_SIZE * (DIMENSION+1))
MAX_FPS = 15
IMAGES = {}
coordinate_list = [(int(row), int(col)) for row, col in np.ndindex(DIMENSION, DIMENSION)]
manager = pgui.UIManager((WIDTH, HEIGHT))
manager.get_theme().load_theme("theme.json")
#Chess Object Variables intended for UI
pieces = {'wP': 'P', 'wR': 'R', 'wN': 'N', 'wB': 'B', 'wQ': 'Q', 'wK': 'K', 
          'bP': 'p', 'bR': 'r', 'bN': 'n', 'bB': 'b', 'bQ': 'q', 'bK': 'k'}
BOARDRANGE = 64 #number of squares on the board

# button font and colors
gui_font = pg.font.SysFont('arial', 20, True)
menuButtonColor = '#555555'
loadButtonColor = '#b3af5d'
pauseButtonColor = '#475F77'

#Initialize global dictionary of images. This will be called exactly once in the main
def loadImages():
    global UNDOIMAGE
    UNDOIMAGE = pg.transform.scale(pg.image.load("assets/images/symbols/undo64.png").convert_alpha(), (30,30))
    for imagePiece, namePiece in pieces.items():
        if namePiece in ['P', 'p']:
            IMAGES[namePiece] = pg.transform.scale(pg.image.load("assets/images/option2/1024px/" + imagePiece + ".png").convert_alpha(), (SQ_SIZE * 0.8, SQ_SIZE * 0.8)) # pawns are sligtly smaller
        else:
            IMAGES[namePiece] = pg.transform.scale(pg.image.load("assets/images/option2/1024px/" + imagePiece + ".png").convert_alpha(), (SQ_SIZE * 0.9, SQ_SIZE * 0.9)) # Chess Pieces are sligtly bigger
    #Note: we can access an image by saying 'IMAGES['P']'
#Initialize sound effects
def loadSounds():
    global pieceMoveSound, pieceCaptureSound, notificationSound 
    pieceMoveSound = pg.mixer.Sound('assets/sounds/move_self.wav')
    pieceCaptureSound = pg.mixer.Sound('assets/sounds/capture.wav')
    notificationSound = pg.mixer.Sound('assets/sounds/notify.wav')

"""
Code Main Driver. This will handle user input and updating the graphics
"""


def main():
    #Main Variables
    pg.display.set_caption(gameTitle + '- GameBoard')
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color(colors['mainBackground']))

    #start instances (eg. gs = chess.GameState())
    stockfish_path = "stockfish/stockfish-macos-m1-apple-silicon"  # Update with your Stockfish path
    gs = chess_engine.GameState(stockfish_path)
    

    #Load Media (taxing processes that should be done once)
    loadImages()
    loadSounds()

    #load buttons
    # button objects and Logic
    undoButton = button_logic.Button(None, 45, 40, ((SQ_SIZE * 0.25), (SQ_SIZE *(DIMENSION)) + (SQ_SIZE * 0.3)+1), screen, UNDOIMAGE, 6, menuButtonColor, 'white') # send variable data to button script
    aiToggleButton = button_logic.Button("Toggle AI", 100, 40, (SQ_SIZE +(SQ_SIZE * 0.25), HEIGHT - SQ_SIZE * .7), screen,
                                         gui_font, 6, '#555555', 'white')
    difficultySlider = pgui.elements.UIHorizontalSlider(
    relative_rect=pg.Rect((SQ_SIZE * 3, SQ_SIZE * DIMENSION + (SQ_SIZE * .4)), (300, 30)),  # Position and size
    start_value=5,  # Default value
    value_range=(0, 20),  # Min and Max values
    manager=manager)
    
    # Label to display current slider value
    slider_value_label = pgui.elements.UILabel(
    relative_rect=pg.Rect((SQ_SIZE * 3, SQ_SIZE * DIMENSION + (SQ_SIZE * .1)), (100, 30)),  # Centered below slider
    text="Value: 5",
    manager=manager
    )


    # Textbox area
    textbox_rect = pg.Rect((WIDTH - (SQ_SIZE * 4)+ 10, 10), (SQ_SIZE * 4 - 20, SQ_SIZE * 4 - 20))  # x, y, width, height
    textbox = None  # Start with no text box
    last_move_string = ""  # Initialize with an empty string
    


    #State Flag Variables
    running = True
    moveMade = False
    animate = False
    pawnPromotion = False
    inCheck = False
    player_turn = True  # True for white, False for black
    ai_enabled = False   # AI is enabled by default
    game_over = False
    sliderInteracting = False

    #MAIN GAME LOOP
    while running:
        time_delta = clock.tick(MAX_FPS) / 1000.0  # Calculate time delta for smooth animations
        for event in pg.event.get():
            manager.process_events(event)
            if event.type == pg.QUIT:
                running = False
            #Mouse and keyboard events
            elif event.type == pg.MOUSEBUTTONDOWN:
                moveMade, animate, moved_piece, captured_piece = mouseHandler(gs)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_z: #undo move when 'z' is pressed
                    if ai_enabled:
                        if len(gs.move_log) >= 2:
                            gs.undoMove()
                            gs.undoMove()
                            moveMade = True
                            animate = False
                    else:
                        gs.undoMove()
                        moveMade = True
                        animate = False

                    if len(gs.move_log) == 0:
                        gs.move_log = []  # Reset the move log
                        last_move_string = ""  # Clear the displayed move log
                        textbox = create_or_update_textbox("", textbox_rect, manager, textbox)  # Clear the textbox

            #button handler
            if undoButton.check_click():
                if ai_enabled:
                    if len(gs.move_log) >= 2:  # Remove both last player move and AI move
                        gs.undoMove()
                        gs.undoMove()
                        moveMade = True
                        animate = False
                else:
                    gs.undoMove()
                    moveMade = True
                    animate = False

                if len(gs.move_log) == 0:
                    gs.move_log = []  # Reset the move log
                    last_move_string = ""  # Clear the displayed move log
                    textbox = create_or_update_textbox("", textbox_rect, manager, textbox)  # Clear the textbox

                

            if aiToggleButton.check_click():  # Toggle AI button
                ai_enabled = not ai_enabled  # Enable/disable AI
                player_turn = True  # Ensure player starts if AI is disabled

            if event.type == pgui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == difficultySlider:
                    # Round value and snap slider
                    rounded_value = round(difficultySlider.get_current_value())
                    difficultySlider.set_current_value(rounded_value)
                    
                    # Update label text
                    slider_value_label.set_text(f"Value: {rounded_value}")

                    # Clear the label area
                    label_rect = slider_value_label.relative_rect
                    screen.fill(colors['mainBackground'], label_rect)

                    # Update only the label area
                    pg.display.update(label_rect)
                    sliderInteracting = True
                    
                    # Update label text
                    slider_value_label.set_text(f"Value: {rounded_value}")
                    pg.display.flip()
            elif event.type == pg.MOUSEBUTTONUP and sliderInteracting:
                pg.draw.rect(screen, colors['mainBackground'], [WIDTH - (SQ_SIZE * 4)+10, SQ_SIZE*4, SQ_SIZE * 4, HEIGHT//2])
                pg.draw.rect(screen, colors['mainTabColor'], [0, HEIGHT - SQ_SIZE, WIDTH - SQ_SIZE * 4 + 6, SQ_SIZE], 6 )
                pg.draw.rect(screen, colors['mainTabColor'], [WIDTH - (SQ_SIZE * 4), 0, SQ_SIZE * 4, HEIGHT], 6 )
                rounded_value = round(difficultySlider.get_current_value())
                gs.set_stockfish_difficulty(rounded_value)  # Update the difficulty in the chess engine
                sliderInteracting = False  # Reset the interaction flag



        

        if ai_enabled and not gs.chessBoard.turn and not animate:
            ai_move = gs.get_ai_move()
            if ai_move:
                ai_san_move = gs.chessBoard.san(ai_move)
                gs.move_log.append(ai_san_move)  # Register move in log
                gs.chessBoard.push(ai_move)
                player_turn = True  # Switch back to player
                moveMade = True  # Set moveMade to True for the animation
                animate = True

                

        # executables whenever a move is made
        if moveMade:
            draw_eval_bar(screen, gs)
            if isinstance(moveMade, tuple):
                print(moveMade)
                if moveMade[0] == 'pawnPromotion':
                    if gs.chessBoard.turn:
                        pieceDict = {'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'N': chess.KNIGHT}
                        choice = input("Pawn Promotion: Choose a piece to promote to (Q, R, B, N): ")
                        choiceUpper = choice.strip().upper()
                        promotionPiece = pieceDict.get(choiceUpper, None)
                        gs.doPawnPromotion(promotionPiece, moveMade[1])
                    else:
                        gs.doPawnPromotion(chess.QUEEN, moveMade[1])  # AI chooses Queen for pawn promotion

            if gs.move_log and len(gs.move_log) > 0:
                drawText(textbox_rect, gs, last_move_string, textbox, checkGameStatus) # Update the textbox with the move log
            if animate:
                animateMove(gs.chessBoard.move_stack[-1], screen, gs, clock, moved_piece, captured_piece, ai_enabled)  # Animate the last move made
                moveSound(moved_piece, captured_piece)  # Play sound for the move
            moveMade = False
            animate = False
            player_turn = not player_turn  # Switch turns


        #Update the UI manager
        manager.update(time_delta)
        
        #Check for game status
        checkGameStatus = gs.check_game_status()
        if checkGameStatus in ("Checkmate", "Stalemate", "insufficient material", "75-move", "Fivefold"):
            game_over = True
        else:
            game_over = False

        
        #Draw the board and other graphics
        drawGameState(screen, gs, checkGameStatus, ai_enabled)
        

        #draw UI after Game State
        drawButtons(screen, gs, undoButton, aiToggleButton) # Replace with pygameGui button
        if not game_over:
            manager.draw_ui(screen) #UI should be drawn after game state

        clock.tick(MAX_FPS)
        pg.display.update()

    gs.close_stockfish()



"""
input handlers and user input events
"""
#global variables
sqSelected = () # deselect
playerClicks = [] # clear player clicks

def mouseHandler(gs):
    global sqSelected, playerClicks
    location = pg.mouse.get_pos()  # (x, y) location of mouse
    col = int(location[0] // SQ_SIZE)
    row = int(location[1] // SQ_SIZE)

    if sqSelected == (row, col):  # User clicked the same square twice
        sqSelected = ()  # Deselect
        playerClicks = []  # Clear player clicks
    else:
        sqSelected = (row, col)
        playerClicks.append(sqSelected)  # Append for both first and second clicks

    if sqSelected not in coordinate_list:  # Checks for clicks outside of board
        sqSelected = ()  # Deselect
        playerClicks = []  # Clear player clicks

    if len(playerClicks) == 2:  # After second click
        start_coord = playerClicks[0]
        end_coord = playerClicks[1]

        # capture the moved and captured pieces before the move is made
        start_square = chess.square(start_coord[1], 7 - start_coord[0])
        end_square = chess.square(end_coord[1], 7 - end_coord[0])
        moved_piece = gs.chessBoard.piece_at(start_square)
        captured_piece = gs.chessBoard.piece_at(end_square)

        move = gs.makeMove(start_coord, end_coord)  # Pass start and end coordinates directly
        if move == True:
            sqSelected = ()  # Deselect
            playerClicks = []  # Clear player clicks
            return True, True, moved_piece, captured_piece  # Move made successfully
        elif isinstance(move, tuple) and move[0] == 'pawnPromotion':
            sqSelected = ()  # Deselect
            playerClicks = []  # Clear player clicks
            return move, True, moved_piece, captured_piece  # Pawn promotion detected
        else:
            playerClicks = [sqSelected]  # Reset player clicks to the last valid square
    return False, False, None, None  # No move made



        #move = chess_engine.Move(playerClicks[0], playerClicks[1], gs.board) #call move function
        #for i in range(len(validMoves)):
            #if move == validMoves[i]:
                #gs.makeMove(validMoves[i])
                #moveMade = True
                #animate = True
                #sqSelected = () # Reset user selected
                #playerClicks = [] # clear player clicks
       # if not moveMade:
            #playerClicks = [sqSelected]

def drawButtons(screen, gs, undoButton, aiToggleButton):
    undoButtonHandler(screen, gs, undoButton) # redraw the undo button
    aiToggleButtonHandler(screen, gs, aiToggleButton) # redraw the AI toggle button

def undoButtonHandler(screen, gs, undoButton):
    # Draw the undo button
    #Redraw behind button
        button_background_rect = pg.Rect(
        undoButton.bottom_rect.x, 
        undoButton.bottom_rect.y, 
        undoButton.bottom_rect.width, 
        undoButton.bottom_rect.height + undoButton.top_rect.height - 40
        )
        screen.fill(('black'), button_background_rect)
        undoButton.draw(screen)
        pg.display.flip()
        
def aiToggleButtonHandler(screen, gs, aiToggleButton):
    #Redraw behind button
        button_background_rect = pg.Rect(
        aiToggleButton.bottom_rect.x, 
        aiToggleButton.bottom_rect.y, 
        aiToggleButton.bottom_rect.width, 
        aiToggleButton.bottom_rect.height + aiToggleButton.top_rect.height - 40
        )
        screen.fill(('black'), button_background_rect)
        aiToggleButton.draw(screen)  # Draw the AI toggle button
        pg.display.flip()




"""
Draw all the graphics on the screen (board, pieces, etc.)
"""
#drawGameState is the parent function: 
#       all other functions pertaining to main game graphics will be called here
def drawGameState(screen, gs, checkGameStatus, ai_enabled):
    drawBoard(screen, gs, ai_enabled)
    highlightLastMove(screen, gs)  # Highlight the last move made
    inCheck(screen, gs, checkGameStatus)
    highlightSelectedPiece(screen, gs, sqSelected)
    drawPieces(screen, gs)
    highlightSquaresValid(screen, gs, sqSelected)
    isGameOver(screen, gs, checkGameStatus)  # Check for game over conditions
    


def drawBoard(screen, gs, ai_enabled):
    font = pg.font.SysFont('arial', 18)  # Small font for rank and file labels
    currentDifficulty = gs.stockfishDifficulty
    difficulty_text = font.render(f"AI Elo: {currentDifficulty}", True, colors['aiBackground'])
    engineActive = font.render(f"AI Engine Active", True, colors['aiBackground'])

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors['chessSquares'][((row+col) % 2)]
            #Draw chess squares
            pg.draw.rect(screen, color, pg.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

            # Draw rank labels (1 to 8) on the left side of the board
            if col == 0:  # Only draw rank labels on the first column
                rank_label = font.render(str(8 - row), True, pg.Color("black"))
                screen.blit(rank_label, (col * SQ_SIZE + 2, row * SQ_SIZE + 2))  # Slightly offset inside the square

            # Draw file labels (a to h) at the bottom of the board
            if row == 7:  # Only draw file labels on the last row
                file_label = font.render(chr(ord('a') + col), True, pg.Color("black"))
                screen.blit(file_label, (col * SQ_SIZE + SQ_SIZE - 10, row * SQ_SIZE + SQ_SIZE - 20))  # Offset inside the square

            #Draw menu areaspg.Color(colors['aiBackground'])
            if ai_enabled:
                screen.blit(difficulty_text, (WIDTH - (SQ_SIZE * 4) + 10, SQ_SIZE*4))  # Display AI difficulty
                screen.blit(engineActive, (WIDTH - (SQ_SIZE * 4) + 10, SQ_SIZE*4 + 20))  # Display AI difficulty
            else:
                pg.draw.rect(screen, colors['mainBackground'], [WIDTH - (SQ_SIZE * 4), SQ_SIZE*4, SQ_SIZE * 4, HEIGHT//2])
                pg.draw.rect(screen, colors['mainTabColor'], [0, HEIGHT - SQ_SIZE, WIDTH - SQ_SIZE * 4 + 6, SQ_SIZE], 6 )
                pg.draw.rect(screen, colors['mainTabColor'], [WIDTH - (SQ_SIZE * 4), 0, SQ_SIZE * 4, HEIGHT], 6 )

            #draw chess board boundries (Lines between squares)
            for i in range(9):
                pg.draw.line(screen, 'black', (0, SQ_SIZE * i), ((SQ_SIZE * DIMENSION), SQ_SIZE * i), 2)
                pg.draw.line(screen, 'black', (SQ_SIZE * i, 0), (SQ_SIZE * i, (SQ_SIZE * DIMENSION)), 2)

                

def drawPieces(screen, gs):
    for i in range(BOARDRANGE):
        r = 7 - (i // 8)  # Flip the row index to match the chessboard's orientation
        c = i % 8    # Column index
        piece = gs.chessBoard.piece_at(i)
        
        if piece:  # Check if there's a piece at this square
            piece_symbol = piece.symbol()  # Get the symbol of the piece ('P', 'R', etc.)
            if piece_symbol in IMAGES:  # Ensure the image for the piece exists
                if piece_symbol in ['P', 'p']:
                    screen.blit(IMAGES[piece_symbol], pg.Rect(c*SQ_SIZE+9, r*SQ_SIZE+11, SQ_SIZE, SQ_SIZE)) # pawns are slightly smaller so drawn differently
                else:
                    screen.blit(IMAGES[piece_symbol], pg.Rect(c*SQ_SIZE+6, r*SQ_SIZE+7, SQ_SIZE, SQ_SIZE))  # chess pieces are sligtly larger so drawn diffferently

def highlightSelectedPiece(screen, gs, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        pieceSelected = gs.chessBoard.piece_at(chess.square(col, 7 - row))  # Get the piece at the selected square
        pieceColor = gs.chessBoard.color_at(chess.square(col, 7 - row))  # Get the piece at the selected square
        if pieceSelected is not None and pieceColor == gs.chessBoard.turn:
            # Highlight the selected square
            s = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA) # Update here to adjust graphic shown
            s.set_alpha(100) # Set transparency (0 = fully transparent, 255 = fully opaque)
            s.fill((0, 255, 0, 100)) # Fill with a color (green in this case)
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE)) # draw the square

def highlightSquaresValid(screen, gs, sqSelected):
    """
    Highlights the selected squares on the chessboard.
    :param screen: The Pygame screen to draw on.
    :param sqSelected: The currently selected square (row, col) or empty tuple.
    :param playerClicks: List of clicked squares [(row1, col1), (row2, col2)].
    """
    if sqSelected != ():
        row, col = sqSelected
        pieceSelected = gs.chessBoard.piece_at(chess.square(col, 7 - row))  # Get the piece at the selected square
        pieceColor = gs.chessBoard.color_at(chess.square(col, 7 - row))  # Get the piece at the selected square
        if pieceSelected is not None and pieceColor == gs.chessBoard.turn:
            # Highlight possible moves
            validMoves = gs.getValidMoves(sqSelected)
            for move in validMoves:
                target_row, target_col = move
                center_x = target_col * SQ_SIZE + SQ_SIZE // 2
                center_y = target_row * SQ_SIZE + SQ_SIZE // 2
                radius = SQ_SIZE // 6  # Adjust size of the circle

                circle_surface = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)  # Create a surface for the circle

                pg.draw.circle(circle_surface, (100, 100, 100, 100), (SQ_SIZE // 2, SQ_SIZE // 2), radius)  # Yellow with transparency
                screen.blit(circle_surface, (target_col * SQ_SIZE, target_row * SQ_SIZE))  # Draw the circle on the board

def highlightLastMove(screen, gs): # highlights the start and end squares of the last move
    if gs.chessBoard.move_stack:
        move = gs.chessBoard.move_stack[-1]  # Get the last move made
        start_square = (7 - chess.square_rank(move.from_square), chess.square_file(move.from_square))
        end_square = (7 - chess.square_rank(move.to_square), chess.square_file(move.to_square))

        # Create a transparent surface
        s = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)
        s.fill((136, 8, 8, 40))  # Yellow transparent fill

        # Draw highlight on the start square
        screen.blit(s, (start_square[1] * SQ_SIZE, start_square[0] * SQ_SIZE))


        # Create a transparent surface for the border
        border_surface = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)
        border_surface.fill((136, 8, 8, 40))  # Yellow transparent border (more transparent)

        # Draw border by placing a slightly larger transparent square on top
        screen.blit(border_surface, (end_square[1] * SQ_SIZE, end_square[0] * SQ_SIZE))

def inCheck(screen, gs, checkGameStatus):
    if checkGameStatus in ("Check", "Checkmate"):
        king_square = gs.chessBoard.king(gs.chessBoard.turn)  # Get the king's position
        row, col = 7 - chess.square_rank(king_square), chess.square_file(king_square)  # Convert to board coordinates
        

        glow_alpha = 70 # starting transparency
        # Create a transparent surface
        glow_surface = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)
        
        # Adjust alpha to create a pulsing effect
        glow_alpha = 70 + int(45 * math.sin(pg.time.get_ticks() * 0.005))  # Pulses over time
        
        # Draw a semi-transparent red circle
        pg.draw.circle(glow_surface, (255, 0, 0, glow_alpha), (SQ_SIZE // 2, SQ_SIZE // 2 + 3), SQ_SIZE // 2 - 5)
        
        # Blit the glow to the screen at the king's position
        screen.blit(glow_surface, (col * SQ_SIZE, row * SQ_SIZE))

def isGameOver(screen, gs, checkGameStatus):
    if checkGameStatus == "Checkmate" and gs.chessBoard.turn == chess.WHITE:
        checkMatetext = "Checkmate! Black Wins"
    else:
        checkMatetext = "Checkmate! White Wins"
    #, "Stalemate", "insufficient material", "75-move", "Fivefold"
    if checkGameStatus == "Checkmate":
        
        # Create a transparent surface
        s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        s.fill((0, 0, 0, 150))  # Black transparent fill
        screen.blit(s, (0, 0))  # Draw the overlay

        # Display game over message
        font = pg.font.SysFont('arial', 50)
        text = font.render(checkMatetext, True, pg.Color("green"))
        text_rect = text.get_rect(center=(SQ_SIZE *4, SQ_SIZE *4))
       
       # Draw a rectangle under the text
        rect_padding = 20  # Add padding around the text
        background_rect = pg.Rect(
            text_rect.x - rect_padding // 2,
            text_rect.y - rect_padding // 2,
            text_rect.width + rect_padding,
            text_rect.height + rect_padding,
        )
        pg.draw.rect(screen, pg.Color("black"), background_rect)  # Black rectangle
        pg.draw.rect(screen, pg.Color("white"), background_rect, 2)  # White border

        screen.blit(text, text_rect)  # Draw the game over message
        if not hasattr(isGameOver, "confetti_list"):
            isGameOver.confetti_list = generate_confetti(300, WIDTH, HEIGHT)  # Generate 100 confetti particles

        # Animate the confetti
        animate_confetti(isGameOver.confetti_list, screen)

def create_or_update_textbox(new_text, textbox_rect, manager, textbox=None):
    """
    Creates or updates a dynamically updating text box using pygame_gui.
    
    :param new_text: The text to display.
    :param textbox_rect: The rectangle area of the text box.
    :param manager: The pygame_gui UIManager instance.
    :param textbox: The existing text box (if any), used for updates.
    :return: The updated or new text box object.
    """
    if textbox is None:
        # Create the text box if it doesn't exist
        textbox = pgui.elements.UITextBox(
            new_text,
            relative_rect=textbox_rect,
            manager=manager,
            object_id="#textbox",
        )
    elif textbox.html_text != new_text:  # Only update if the text has changed
        textbox.set_text(new_text)

    return textbox

def drawText(textbox_rect, gs, last_move_string, textbox, checkGameStatus):
        if checkGameStatus == "Checkmate":
            if textbox is not None:
                textbox.kill()
            return None, last_move_string
    # Concatenate moves into groups of three pairs (six moves) per line
        move_list = []
        line = ""
        for i, move in enumerate(gs.move_log):
            if i % 2 == 0:  # White's move
                line += f"<b>{i // 2 + 1}.</b> {move} "  # Add move number and White's move
            else:  # Black's move
                line += f"{move}  "  # Add Black's move

            # Add a line break after every three pairs of moves (six moves)
            if (i + 1) % 6 == 0:
                move_list.append(line.strip())  # Add the line to the move list
                line = ""  # Reset the line

        # Add any remaining moves to the move list
        if line:
                    move_list.append(line.strip())

        # Join the move list into a single string with line breaks
        move_string = "\n".join(move_list)

        # Only update the textbox if the move string has changed
        if move_string != last_move_string:
            textbox = create_or_update_textbox(move_string, textbox_rect, manager, textbox)
            last_move_string = move_string  # Update the last move string

def draw_eval_bar(screen, gs):
    """Draw an evaluation bar based on Stockfish evaluation."""
    eval_score = gs.get_eval()
    BAR_WIDTH = 10

    bar_height = (SQ_SIZE * DIMENSION) * (0.5 - eval_score / 2)  # Map eval to height 
    pg.draw.rect(screen, (255, 255, 255), (SQ_SIZE * DIMENSION, bar_height, BAR_WIDTH, HEIGHT - bar_height)) #whites evaluation
    pg.draw.rect(screen, (pg.Color('black')), (SQ_SIZE * DIMENSION, 0, BAR_WIDTH, bar_height)) # blacks evaluation

    # Draw an outline around the evaluation bar
    outline_rect = pg.Rect(SQ_SIZE * DIMENSION, 0, BAR_WIDTH, HEIGHT)  # Full height of the bar
    pg.draw.rect(screen, pg.Color('grey'), outline_rect, 2)  # Red outline with a width of 2 pixels

"""
Event Handlers
"""
def animateMove(move, screen, gs, clock, moved_piece, captured_piece, ai_enabled):
    turn = gs.chessBoard.turn
    board = gs.chessBoard
    
    color = colors['chessSquares']

    # Retrieve the moved piece and the captured piece

    start_square = (7 - chess.square_rank(move.from_square), chess.square_file(move.from_square))
    end_square = (7 - chess.square_rank(move.to_square), chess.square_file(move.to_square))
    move_coordinates = (start_square, end_square)
    dR = end_square[0] - start_square[0]
    dC = end_square[1] - start_square[1]
    distance = abs(dR) + abs(dC)
    scalingFactor = 3
    baseFrameCount = 8
    frameCount = int(scalingFactor * np.sqrt(distance) + baseFrameCount)
    for frame in range(frameCount + 1):
        r, c = (move_coordinates[0][0] + dR*frame/frameCount, move_coordinates[0][1] + dC*frame/frameCount)
        drawBoard(screen, gs, ai_enabled)
        drawPieces(screen, gs)
        #erase the piece moved from its ending square
        colorBoard = color[(move_coordinates[1][0] + move_coordinates[1][1]) % 2]
        endSquare = pg.Rect(move_coordinates[1][1] * SQ_SIZE+2, move_coordinates[1][0] * SQ_SIZE+2, SQ_SIZE*.95, SQ_SIZE*.95)
        #insert if statement to differentiate between pawn and other pieces
        if moved_piece is not None:
            if moved_piece.symbol() in ['P', 'p']:
                endPiece = pg.Rect(move_coordinates[1][1] * SQ_SIZE + 9, move_coordinates[1][0] * SQ_SIZE + 11, SQ_SIZE, SQ_SIZE)
            else:
                endPiece = pg.Rect(move_coordinates[1][1] * SQ_SIZE + 6, move_coordinates[1][0] * SQ_SIZE + 7, SQ_SIZE, SQ_SIZE)
            pg.draw.rect(screen, colorBoard, endSquare)

            #draw captured piece onto rectangle
            if captured_piece is not None:
                screen.blit(IMAGES[captured_piece.symbol()], endPiece)
            if moved_piece.symbol() in ['P', 'p']:
                screen.blit(IMAGES[moved_piece.symbol()], pg.Rect(c * SQ_SIZE + 9, r * SQ_SIZE + 11, SQ_SIZE, SQ_SIZE))
            else:
                screen.blit(IMAGES[moved_piece.symbol()], pg.Rect(c * SQ_SIZE + 6, r * SQ_SIZE + 7, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        clock.tick(60)
        
def moveSound(moved_piece, captured_piece):
    if moved_piece is not None:
        if captured_piece is not None:
            pieceCaptureSound.play()
        else:
            pieceMoveSound.play()     

class Confetti:
    def __init__(self, x, y, color, speed):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = random.randint(3, 7)  # Random size for each confetti particle

    def update(self):
        # Move the confetti particle downward
        self.y += self.speed
        # Add some horizontal drift
        self.x += random.uniform(-1, 1)

    def draw(self, screen):
        # Draw the confetti particle as a small rectangle
        pg.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
    
def generate_confetti(num_particles, screen_width, screen_height):
    confetti_list = []
    for _ in range(num_particles):
        x = random.randint(0, screen_width)
        y = random.randint(-screen_height, 0)  # Start above the screen
        color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])
        speed = random.uniform(1, 5)  # Random falling speed
        confetti_list.append(Confetti(x, y, color, speed))
    return confetti_list

def animate_confetti(confetti_list, screen):
    for confetti in confetti_list:
        confetti.update()
        confetti.draw(screen)



if __name__ == "__main__":
    main()