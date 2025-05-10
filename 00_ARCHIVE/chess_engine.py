"""
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining valid moves at current state.
It will also keep a move log.
"""
import numpy as np

    



class game_state():
    def __init__(self):
        # board is an 8x8 2 dimensional list, each element of the list has 2 characters
        # first character represents color of piece 'b' or 'w'
        # second character represents the type of piece 'K', 'Q', 'R', 'B', 'N', 'P'
        # '--' represents empty space with no piece
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.castleRights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}  # Castling rights for kingside and queenside
        self.castleRightsLog = [self.castleRights.copy()]  # Log of castling rights for undoing moves
        

        # Variables for extra features (not used in chess logic)
        self.lastMoveType = None  # Initialize to None Used for sound triggering
        self.capturedPieces = [] # Captured Piece


    
    # take smove as parameter and executes it (this will not work for casteling, en-passant, or pawn-promotion)
    def makeMove(self, move):
        print(f"Before move: whiteToMove = {self.whiteToMove}")  # Debug statement

        self.castleRightsLog.append(self.castleRights.copy())  # Log the castle rights before the move
        # Determine last move type for sound triggering
        if self.board[move.endRow][move.endCol] == "--":
            self.lastMoveType = "move"
        else:
            self.lastMoveType = "capture"
        
        
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move) # log move so we can undo it later
        self.whiteToMove = not self.whiteToMove # Swap players
        
        print(f"After move: whiteToMove = {self.whiteToMove}")  # Debug statement

        #update kings location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        #Update enpassantPossible Variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # only on two square pawn advances
            self.enpassantPossible = ((move.endRow + move.startRow)//2, move.startCol)
            
        else:
            self.enpassantPossible = ()

        #en Passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # Capturing pawn

        #pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N:") # can add this to ui later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece # auto assigning promotion to queen
        
        # Update castling rights if king or rook moves
        if move.pieceMoved in ['wK', 'bK', 'wR', 'bR']:
            if move.pieceMoved == 'wK':
                self.castleRights['wK'] = False
                self.castleRights['wQ'] = False
            elif move.pieceMoved == 'bK':
                self.castleRights['bK'] = False
                self.castleRights['bQ'] = False
            elif move.pieceMoved == 'wR':
                if move.startRow == 7 and move.startCol == 0:  # Queenside rook
                    self.castleRights['wQ'] = False
                elif move.startRow == 7 and move.startCol == 7:  # Kingside rook
                    self.castleRights['wK'] = False
            elif move.pieceMoved == 'bR':
                if move.startRow == 0 and move.startCol == 0:  # Queenside rook
                    self.castleRights['bQ'] = False
                elif move.startRow == 0 and move.startCol == 7:  # Kingside rook
                    self.castleRights['bK'] = False
            

        # Handle castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Kingside castling
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # Queenside castling
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'
        

        




    # This will undo the last move made
    def undoMove(self): 
        if len(self.moveLog) != 0:  # Make sure moveLog is not empty
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # Switch turns back

            # Restore castling rights
            if len(self.castleRightsLog) > 0:
                self.castleRights = self.castleRightsLog.pop()

            # Update king's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # Undo a two-square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # Undo pawn promotion
            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceMoved  # Restore the original pawn

            # Undo castling
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Kingside castling
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]  # Move rook back
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # Queenside castling
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]  # Move rook back
                    self.board[move.endRow][move.endCol + 1] = '--'

    # This function resets the lastMoveType after accessed from Chess_main (for sound)
    def getAndResetMoveType(self):
        moveType = self.lastMoveType
        self.lastMoveType = None  # Reset after reading
        return moveType
    
    # All moves considering checks
    
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible     # can potentially remove
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                #to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] #check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # enemy piece causing the check
                validSquares = [] # squares pieces can move to
                #if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check [2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: #once you get to piece end check
                            break
            #get rid of any moves that dont block check or move king
                for i in range(len(moves) -1, -1, -1): #go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K': # move doesnt move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #move doesnt block check or capture piece
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #not in check so all moves are fine
            moves = self.getAllPossibleMoves()


        self.enpassantPossible = tempEnpassantPossible
        print(f"Valid moves for {'White' if self.whiteToMove else 'Black'}: {moves}")  # Debug statement
        return moves

    # determine if current player is under attack
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # determine if enemy can attack square
    def squareUnderAttack(self, r, c, castlingCheck=False):
        originalWhiteToMove = self.whiteToMove
        try:
            self.whiteToMove = not self.whiteToMove  # Switch to opponent's moves
            oppMoves = self.getAllPossibleMoves(castlingCheck=castlingCheck)  # Pass the flag to prevent recursion
            for move in oppMoves:
                if move.endRow == r and move.endCol == c:
                    return True
            return False
        finally:
            self.whiteToMove = originalWhiteToMove  # Restore original value
    
    # All moves without considering checks
    def getAllPossibleMoves(self, castlingCheck=False):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves, castlingCheck=castlingCheck)  # Pass the flag
        print(f"All possible moves for {'White' if self.whiteToMove else 'Black'}: {moves}")  # Debug statement
        return moves


    """
    Create all piece move sets
    """
# Get all the Pawn moves for the Pawn located at row, col and add these moves to the list
    def getPawnMoves(self, r, c, moves, castlingCheck=False):
        piecePinned = False # get information about pin
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] ==c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'



        if self.board[r+moveAmount][c] == '--': # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r+moveAmount, c), self.board))
                if r == startRow and self.board[r+2*moveAmount][c] == '--': # 2 square pawn advance
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))
            
            # Captures
        if c-1 >= 0: # captures to the left
            if not piecePinned or pinDirection == (moveAmount, -1):   
                if self.board[r + moveAmount][c-1][0] == enemyColor: # check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board))
            if (r + moveAmount, c -1 ) == self.enpassantPossible:
                moves.append(Move((r, c), (r+moveAmount, c-1), self.board, isEnpassantMove=True))

        if c+1 <= 7: # captures to the left
            if not piecePinned or pinDirection == (moveAmount, 1):   
                if self.board[r+moveAmount][c+1][0] == enemyColor: # check if there is an enemy piece to capture
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board))
            if (r + moveAmount, c +1 ) == self.enpassantPossible:
                moves.append(Move((r, c), (r+moveAmount, c+1), self.board, isEnpassantMove=True))




# Get all the Rook moves for the Rook located at row, col and add these moves to the list
    def getRookMoves(self, r, c, moves, castlingCheck=False):
        piecePinned = False # get information about pin
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] ==c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # cant remove queen from pin on rook moves, only removes it on bishop moves
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range (1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # check if piece is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #empty space is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # enemy Piece Valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # Friendly piece invalid
                            break
                else: # off board
                    break

# Get all the Bishop moves for the Bishop located at row, col and add these moves to the list
    def getBishopMoves(self, r, c, moves, castlingCheck=False):
        piecePinned = False # get information about pin
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] ==c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range (1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # check if piece is on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': # empty spaces are valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # enemy Piece Valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # Friendly piece invalid
                            break
                else: # off board
                    break


# Get all the Knight moves for the Knight located at row, col and add these moves to the list
    def getKnightMoves(self, r, c, moves, castlingCheck=False):
        piecePinned = False # get information about pin
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] ==c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves: # dont need iterations(i) because knight has set moves
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # check if piece is on board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

# Get all the Queen moves for the Queen located at row, col and add these moves to the list
    def getQueenMoves(self, r, c, moves, castlingCheck=False):
        self.getRookMoves(r, c, moves, castlingCheck=castlingCheck)
        self.getBishopMoves(r, c, moves, castlingCheck=castlingCheck)

# Get all the King moves for the King located at row, col and add these moves to the list
    def getKingMoves(self, r, c, moves, castlingCheck=False):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    #place king back in original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        # Add castling moves only if not in castling check mode
        if not castlingCheck:
            self.addCastlingMoves(r, c, moves, allyColor)

    def addCastlingMoves(self, r, c, moves, allyColor):
        if self.inCheck:
            return  # Can't castle while in check

        if allyColor == 'w':
            if self.castleRights['wK'] and self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
                if not self.squareUnderAttack(r, c + 1, castlingCheck=True) and not self.squareUnderAttack(r, c + 2, castlingCheck=True):
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))  # Kingside castling
            if self.castleRights['wQ'] and self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
                if not self.squareUnderAttack(r, c - 1, castlingCheck=True) and not self.squareUnderAttack(r, c - 2, castlingCheck=True):
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))  # Queenside castling
        else:
            if self.castleRights['bK'] and self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
                if not self.squareUnderAttack(r, c + 1, castlingCheck=True) and not self.squareUnderAttack(r, c + 2, castlingCheck=True):
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))  # Kingside castling
            if self.castleRights['bQ'] and self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
                if not self.squareUnderAttack(r, c - 1, castlingCheck=True) and not self.squareUnderAttack(r, c - 2, castlingCheck=True):
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))  # Queenside castling



#returns if player is in check, a list of pins, a list of checks
    def checkForPinsAndChecks(self):
        pins = [] # squares where the allied pinned piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0<= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        #5 possibilities in this complex conditional
                        #   1. orthogonally away from king and piece is rook
                        #   2. diagonally away from king and piece is bishop
                        #   3. 1 square away diagonally from king and piece is a pawn
                        #   4. any direction and piece is a queen
                        #   5. any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # enemy piece not applying check
                            break
                else:
                    break # off board

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks





class Move():
    # maps keys to values (Creating Dictionaries to map coordinates to chess notation.)
    # key : value
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4,
                   '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                   'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False): # potentially where sound effects will be called from
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion
        self.isPawnPromotion = (self.pieceMoved =='wP' and self.endRow ==0) or (self.pieceMoved == 'bP' and self.endRow == 7)  # set pawn promotion to true if white pawn makes it to end
        
        #en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        
        # Castle Move
        self.isCastleMove = isCastleMove

        # Unique move ID for comparison
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    def to_dict(self):
        """Convert move to a dictionary for JSON serialization."""
        return {
            'startRow': self.startRow,
            'startCol': self.startCol,
            'endRow': self.endRow,
            'endCol': self.endCol,
            'pieceMoved': self.pieceMoved,
            'pieceCaptured': self.pieceCaptured,
            'isPawnPromotion': self.isPawnPromotion,
            'isEnpassantMove': self.isEnpassantMove,
            'isCastleMove': self.isCastleMove  # Include isCastleMove
        }

    @staticmethod
    def from_dict(data, board):
        """Convert a dictionary back to a Move object."""
        return Move(
            (data['startRow'], data['startCol']),
            (data['endRow'], data['endCol']),
            board,
            isEnpassantMove=data.get('isEnpassantMove', False),
            isCastleMove=data.get('isCastleMove', False)  # Include isCastleMove
        )

    """
    Overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self): # shows the chess notation from coordnitates
        # adapt this code to be proper chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def __str__(self):
        return f"{self.pieceMoved} from {self.getRankFile(self.startRow, self.startCol)} to {self.getRankFile(self.endRow, self.endCol)}"

    def __repr__(self):
        return f"Move({self.pieceMoved}, {self.getRankFile(self.startRow, self.startCol)} -> {self.getRankFile(self.endRow, self.endCol)})"



