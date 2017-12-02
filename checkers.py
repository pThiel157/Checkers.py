# Welcome to Checkers Sim!
# Written by Pablo Thiel


import time
import string
import random



class game:
  
    # controls the central flow of the game. This is called at the very end of the file.
    def __init__(self):
        
        # here we have a bunch of game initialization stuff
        print 'Welcome!'
        time.sleep(.75)
        
        # p1 is always a human player
        self.p1 = human_player(1)
        
        # p2 can be a human or AI player depending on what the player chooses
        if self.check_for_ai():
            self.p2 = ai_player(2)
        else:
            self.p2 = human_player(2)
            
        # here we make the game board
        self.create_board()
        
        # set the piece counts (to keep track of pieces to determine when the game ends)
        self.p1_piece_count = self.board.size * 2
        self.p2_piece_count = self.board.size * 2
        
        print "Excellent! Let's begin the game..."
        time.sleep(1.5)
        
        self.board.show()
        
        # main game loop:
        while True:
            move = self.p1.get_move_input(self.board)
            self.make_move(move)
            if self.check_for_gameover()[0]:   # if the game is finished, we break out of the gameloop
                break
            move = self.p2.get_move_input(self.board)
            self.make_move(move)
            if self.check_for_gameover()[0]:   # once again, if the game is finished, we break out of the gameloop
                break
        
        if self.check_for_gameover()[1] == 1:
            print 'Game over! Player 1 wins!'
        else:
            print 'Game over! Player 2 wins!'
        
        
    # asks the player whether they want to play against an ai opponent and returns True or False accordingly.
    def check_for_ai(self):
        ai_choice = raw_input('Would you like to play with an AI opponent? (y/n): ')
        if string.lower(ai_choice) == 'y':
            return True
        elif string.lower(ai_choice) == 'n':
            return False
        else:
            print "Your answer must be in the form of 'y' or 'n'!"
            time.sleep(1.25)
            return self.check_for_ai()
            
      
    # asks the player to select a board size and builds a new board with said size, storing it in the game's 'board' property.
    def create_board(self):      
        size = raw_input("Please input board size (any even number between 10-26): ")
        
        if not (is_numbers(size) and 10 <= int(size) <= 26 and int(size) % 2 == 0):
            print 'Illegal board size: Board size must be an even number between 10 and 26!'
            time.sleep(1.25)
            self.create_board()
        else:
            self.board = board(int(size))
            
    
    # returns a boolean representing if either player's pieces are all gone and an integer representing the winning player.
    def check_for_gameover(self):
        if self.p1_piece_count == 0:
            return [True, 2]   # the second value represents which player won (i.e. 1 for player 1 and 2 for player 2)
        elif self.p2_piece_count == 0:
            return [True, 1]
        else:
            return [False, -1]
        
      
    # sets the destination space to the object in the origin space and then replaces the object in the origin space with
    # the board's default character, thus moving the piece. This method also the piece-capturing in jumps
    def make_move(self, move):
        
        x1 = move[0]
        y1 = move[1]
        x2 = move[2]
        y2 = move[3]
        
        piece = self.board.get_space(x1, y1)
        
        # here we handle jumping if the move is a jump
        if piece.is_legal_diagonal_jump(x2, y2):
            between_piece = self.board.get_in_between_space(x1, y1, x2, y2)
            self.capture(between_piece)   # removes the jumped piece
            piece.set_pos(x2, y2)
            self.board.set_space(x2, y2, piece)
            self.board.set_space(x1, y1, self.board.default_char) 
            self.check_for_kinging(piece)   # checks if the move has placed the piece in a spot to be kinged
            self.check_for_extra_jump(x2, y2)   # here we check if the piece can jump again
        else:
            piece.set_pos(x2, y2)
            self.board.set_space(x2, y2, piece)
            self.board.set_space(x1, y1, self.board.default_char)
            self.check_for_kinging(piece)   # checks if the move has placed the piece in a spot to be kinged
            
        self.board.show()
            
    
    # removes the captured piece from the board and decrements the piece count for that piece's team
    def capture(self, piece):
        
        if isinstance(piece, p1_piece):
            self.p1_piece_count -= 1
        else:
            self.p2_piece_count -= 1
            
        self.board.set_space(piece.x, piece.y, self.board.default_char)
        
        
    # given the position of a piece which has just jumped, checks if it can jump again and makes that jump if possible
    # If the piece can jump again, we let the player choose whether or not he/she wants to jump and which jump to take
    # (if multiple jumps are possible). If the piece is an p2 piece and an AI is being used, it always takes the jump
    # (choosing the first jump it finds if several are available).
    def check_for_extra_jump(self, x, y):
        piece = self.board.get_space(x, y)
        
        # all the tests for p1 pieces (i.e. moving up the board only):
        if isinstance(piece, p1_piece):
            if (x - 2 >= 0 and y + 2 < self.board.size
                and self.board.get_space(x - 2, y + 2) == self.board.default_char
                and isinstance(self.board.get_in_between_space(x, y, x - 2, y + 2), p2_piece)):
                
                self.confirm_extra_jump(x, y)
                
            if (x + 2 < self.board.size and y + 2 < self.board.size
                and self.board.get_space(x + 2, y + 2) == self.board.default_char
                and isinstance(self.board.get_in_between_space(x, y, x + 2, y + 2), p2_piece)):
                
                self.confirm_extra_jump(x, y)
            
            # specific tests for p1 kings (i.e. moving down the board as well):
            if isinstance(piece, p1_king):
                if (x - 2 >= 0 and y - 2 >= 0
                    and self.board.get_space(x - 2, y - 2) == self.board.default_char
                    and isinstance(self.board.get_in_between_space(x, y, x - 2, y - 2), p2_piece)):
                
                    self.confirm_extra_jump(x, y)
                
                if (x + 2 < self.board.size and y - 2 >= 0
                    and self.board.get_space(x + 2, y - 2) == self.board.default_char
                    and isinstance(self.board.get_in_between_space(x, y, x + 2, y - 2), p2_piece)):
                
                    self.confirm_extra_jump(x, y)
    
        # now onto tests for p2 pieces (i.e. moving down the board only):
        else:
            if (x - 2 >= 0 and y - 2 >= 0
                and self.board.get_space(x - 2, y - 2) == self.board.default_char
                and isinstance(self.board.get_in_between_space(x, y, x - 2, y - 2), p1_piece)):
                
                # if it's an AI player, we always take the jump. Otherwise, we check with the player
                if isinstance(self.p2, ai_player):
                    self.board.show()
                    print 'Jumped!'
                    print 'Jumping again...'
                    time.sleep(1)
                    self.make_move([x, y, x - 2, y - 2])
                else:
                    self.confirm_extra_jump(x, y)
            
            if (x + 2 < self.board.size and y - 2 >= 0
                and self.board.get_space(x + 2, y - 2) == self.board.default_char
                and isinstance(self.board.get_in_between_space(x, y, x + 2, y - 2), p1_piece)):
                
                # if it's an AI player, we always take the jump. Otherwise, we check with the player
                if isinstance(self.p2, ai_player):
                    self.board.show()
                    print 'Jumped!'
                    print 'Jumping again...'
                    time.sleep(1)
                    self.make_move([x, y, x + 2, y - 2])
                else:
                    self.confirm_extra_jump(x, y)
                
            # tests for opponent kings (i.e. moving up the board as well):
            if isinstance(piece, p2_king):
                if (x - 2 >= 0 and y + 2 < self.board.size
                    and self.board.get_space(x - 2, y + 2) == self.board.default_char
                    and isinstance(self.board.get_in_between_space(x, y, x - 2, y + 2), p1_piece)):
                    
                    # if it's an AI player, we always take the jump. Otherwise, we check with the player
                    if isinstance(self.p2, ai_player):
                        self.board.show()
                        print 'Jumped!'
                        print 'Jumping again...'
                        time.sleep(1)
                        self.make_move([x, y, x - 2, y + 2])
                    else:
                        self.confirm_extra_jump(x, y)
                
                if (x + 2 < self.board.size and y + 2 < self.board.size
                    and self.board.get_space(x + 2, y + 2) == self.board.default_char
                    and isinstance(self.board.get_in_between_space(x, y, x + 2, y + 2), p1_piece)):
                    
                    # if it's an AI player, we always take the jump. Otherwise, we check with the player
                    if isinstance(self.p2, ai_player):
                        self.board.show()
                        print 'Jumped!'
                        print 'Jumping again...'
                        time.sleep(1)
                        self.make_move([x, y, x + 2, y + 2])
                    else:
                        self.confirm_extra_jump(x, y)
                        
    
    # informs the player that another jump is possible and gives them the option of choosing an available extra jump or
    # staying still and not jumping again.
    def confirm_extra_jump(self, x1, y1):
        self.board.show()
        print 'You can jump again! Choose a space to jump to or choose the space of your own piece to stay still:'
        destination = raw_input('')
        
        # parses player input
        x2 = letter_number_parse(destination)[0]
        y2 = letter_number_parse(destination)[1]
        
        piece = self.board.get_space(x1, y1)
        
        if isinstance(piece, p1_piece):
            player = self.p1
        else:
            player = self.p2
        
        # if the player chooses the same spot, we interpret that as instruction to stay still
        if x2 == x1 and y2 == y1:
            return
        # otherwise we check if the move is a legal jump and make the move if it is
        elif piece.is_legal_diagonal_jump(x2, y2) and player.is_legal_move(self.board, x1, y1, x2, y2)[0]:
            self.make_move([x1, y1, x2, y2])
        # if the move isn't legal, we tell the player and let them make another input
        else:
            print 'Illegal move: You must select either a legal tile to jump to or the tile of your own piece'
            time.sleep(1.75)
            self.confirm_extra_jump(x1, y1)
            
    
    # checks if the piece is in a position to be kinged and kings it if it is
    def check_for_kinging(self, piece):
        # if a p1 piece reaches the top of the board, we king it
        if isinstance(piece, p1_piece) and piece.y == self.board.size - 1:
            self.king(piece)
        # if an p2 piece reaches the bottom of the board, we king it
        elif piece.y == 0:
            self.king(piece)
            
    
    # replaces a piece with its kinged variety
    def king(self, piece):
        if isinstance(piece, p1_piece):
            king_piece = p1_king(piece.x, piece.y)
            self.board.set_space(piece.x, piece.y, king_piece)
        else:
            king_piece = p2_king(piece.x, piece.y)
            self.board.set_space(piece.x, piece.y, king_piece)
                

# represents the gameboard
class board:
  
    # given a size and default character, initializes a board of that size and using that character to represent empty board spaces.
    def __init__(self, size = 10, c = '.'):  # note: board size is customizable!
        self.rep = []
        self.size = size                                       
        self.default_char = c
    
        # creates a size * size board
        for i in range(size):
            self.rep = self.rep + [[c] * size]
        
        # populates the board with pieces
        for i in range(size/2):
            
            # top 4 rows:
            self.rep[size - 1][1 + 2*i] = p2_piece(1 + 2*i, size - 1)   # adding one to the second index offsets the pieces so that
            self.rep[size - 2][2*i] = p2_piece(2*i, size - 2)           # we get a nice checkerboard-style distribution.
            self.rep[size - 3][1 + 2*i] = p2_piece(1 + 2*i, size - 3)
            self.rep[size - 4][2*i] = p2_piece(2*i, size - 4)
            
            # bottom 4 rows:
            self.rep[3][1 + 2*i] = p1_piece(1 + 2*i, 3)
            self.rep[2][2*i] = p1_piece(2*i, 2)
            self.rep[1][1 + 2*i] = p1_piece(1 + 2*i, 1)
            self.rep[0][2*i] = p1_piece(2*i, 0)
  
    
    # given an x and y coordinate, returns the item held at that board space.
    def get_space(self, x, y):
    
        answer = self.rep[y][x]
        return answer
    
    # given an x and y coordinate, fills that board space with a new item.
    def set_space(self, x, y, new_thing):
    
        self.rep[y][x] = new_thing
    
    
    # returns the space in between two given tiles.
    def get_in_between_space(self, x1, y1, x2, y2):
        assert (abs(x1 - x2) == abs(y1 - y2) == 2)   # insures that the spaces do indeed have a space between them
    
        return self.get_space((x1 + x2) / 2, (y1 + y2) / 2)
    
    
    # returns the next space behind two spaces in a diagonal line. (Updated Note: as of now this method is never
    # actually used, but it might be helpful in certain circumstances if the program is ever extended).
    def get_behind_space(self, x1, y1, x2, y2):
        assert(abs(x1 - x2) == abs(y1 - y2) == 1)   # insures the two spaces are adjacent to each other
    
        return self.get_space(2 * x2 - x1, 2 * y2 - y1)
    
    
    # clears space on the screen and displays the board
    def show(self):
        print '\n' * 30
        print self
  
    
    # represents the board in a nice, easy to read format with guide rows and columns facilitating human player input.
    def __repr__(self):
        result = ""
    
        # converts the list of lists into a nicely formatted string representing the board
        for r in range(self.size):
            row = ""
            for i in self.rep[r]:
                row = row + str(i) + " "
            result = "\n" + row + ' ' + str(r + 1) + result   # the addition of the str(i) makes a handy guide column for
                                                              # the player denoting which number corresponds to which row
        # now we make a guide row containing the letters corresponding to the x axis
        guide_row = ''
        for i in range(self.size):
            guide_row = guide_row + string.lowercase[i] + ' '
      
        # ... and append it to our result
        result = result + '\n' + guide_row
        return result + '\n'
    
    
    
# parent class for both human and AI players
class player:
    
    # takes in and stores an int team (either 1 or 2) representing the team the player is on
    def __init__(self, team):
        
        self.team = team
        
        
    def is_legal_move(self, board, x1, y1, x2, y2):
        
        # orients the tests according to which player the move is for
        if self.team == 1:
            friend = p1_piece
            foe = p2_piece
        elif self.team == 2:
            friend = p2_piece
            foe = p1_piece
        
        # checks that the move's origin and destination fall within the ranges of the board
        if not (0 <= x1 <= board.size - 1
            and 0 <= y1 <= board.size - 1
            and 0 <= x2 <= board.size - 1
            and 0 <= y2 <= board.size - 1):
            return [False, 'You must choose spaces within the range of the board!']
        
        piece = board.get_space(x1, y1)
    
        # checks that the piece being moved is a friendly piece
        if not isinstance(piece, friend):
            return [False, 'You must choose a tile holding one of your own pieces!']
        
        # checks that the destination space is empty
        elif isinstance(board.get_space(x2, y2), game_piece):
            return [False, 'Destination space must be empty!']
      
        # checks that the move is a diagonal step or jump
        elif not (piece.is_legal_diagonal_step(x2, y2) or piece.is_legal_diagonal_jump(x2, y2)):
            return [False, 'Move must be a legal diagonal step or jump!']
        
        # checks that jumps are made over enemy pieces
        elif piece.is_legal_diagonal_jump(x2, y2) and not isinstance(board.get_in_between_space(x1, y1, x2, y2), foe):
            return [False, 'You can only jump over opponent pieces!']
      
        # returns True if none of these rules are violated
        else:
            return [True, '']
        
        

# adds additional functionality for human players
class human_player(player):
    
    def get_move_input(self, board):
        
        # interfaces with human player
        print 'PLAYER ' + str(self.team) + ' TURN:'
        
        # insures the player's inputs are in the acceptable form
        acceptable_input = False
        while not acceptable_input:
            print 'Choose a piece to move:'
            origin = raw_input('')
            if not (len(origin) >= 2 and origin[0] in string.ascii_letters and is_numbers(origin[1:])):
                print 'Ill-formed input: Your input must be in the form of a letter followed by a number!'
                time.sleep(1.25)
            else:
                acceptable_input = True
           
        # insures the player's inputs are in the acceptable form     
        acceptable_input = False
        while not acceptable_input:
            print 'Choose a tile to move it to:'
            destination = raw_input('')
            if not (len(destination) >= 2 and destination[0] in string.ascii_letters and is_numbers(destination[1:])):
                print 'Ill-formed input: Your input must be in the form of a letter followed by a number!'
                time.sleep(1.25)
            else:
                acceptable_input = True
            
        # parses and stores human input into x-y-coordinates
        x1 = letter_number_parse(origin)[0]
        y1 = letter_number_parse(origin)[1]
        x2 = letter_number_parse(destination)[0]
        y2 = letter_number_parse(destination)[1]
        
        # checks if the move is legal
        legality = self.is_legal_move(board, x1, y1, x2, y2)
        
        # if the move is illegal, we tell the player why it failed and give him/her to take another turn.
        # Otherwise, we simply make the move.
        if not legality[0]:
            print 'Illegal move: ' + legality[1]
            time.sleep(1.75)
            board.show()
            return self.get_move_input(board)
        else:
            return [x1, y1, x2, y2]

    

# extends player for AI players
class ai_player(player):
    
    # handles turns taken by AI players. Generates and tests 4 random coordinates within the ranges of the board
    # until it finds a combination which results in a legal move. It then makes the move.
    def get_move_input(self, board):
        
        print 'OPPONENT TURN:'
        time.sleep(1)
        print 'thinking very hard...'
        time.sleep(1.75)   # waiting 2 seconds. The most intense type of thinking there is.
        
        # generates random coordinates
        found_legal_move = False
        while not found_legal_move:
            x1 = int(random.random() * (board.size - 1))
            y1 = int(random.random() * (board.size - 1))
            x2 = int(random.random() * (board.size - 1))
            y2 = int(random.random() * (board.size - 1))
            
            # tests for legality
            if self.is_legal_move(board, x1, y1, x2, y2)[0]:
                found_legal_move = True
        
        # returns the move once a legal one is found
        return [x1, y1, x2, y2]
    
    

# the parent class for all pieces in the game
class game_piece:
    
    # stores the newly-created piece's board position
    def __init__(self, x = -1, y = -1):
        self.x = x
        self.y = y
    
    # changes the piece's board position
    def set_pos(self, x, y):
        self.x = x
        self.y = y
        
        
 
# class for all regular player 1 pieces and parent class for player 1 kings
class p1_piece(game_piece):
  
    def __repr__(self):
        return 'O'
    
  
    def is_legal_move(self, x2, y2):
        return self.is_diagonal_step(x2, y2) or self.is_diagonal_step(x2, y2)
    
    
    def is_legal_diagonal_step(self, x2, y2):
        return (x2 == self.x + 1 or x2 == self.x - 1) and (y2 == self.y + 1)
    
  
    def is_legal_diagonal_jump(self, x2, y2):
        return (x2 == self.x + 2 or x2 == self.x - 2) and (y2 == self.y + 2)
    
    

# class for player 1 kings
class p1_king(p1_piece):
  
    def __repr__(self):
        return 'K'
    
    
    def is_legal_diagonal_step(self, x2, y2):
        return (x2 == self.x + 1 or x2 == self.x - 1) and (y2 == self.y + 1 or y2 == self.y - 1)
    
    
    def is_legal_diagonal_jump(self, x2, y2):
        return (x2 == self.x + 2 or x2 == self.x - 2) and (y2 == self.y + 2 or y2 == self.y - 2)
    
    

# class for all regular player 2 pieces and parent class for player 2 kings
class p2_piece(game_piece):
  
    def __repr__(self):
        return '0'
    
    def is_legal_move(self, x2, y2):
        return self.is_diagonal_step(x2, y2) or self.is_diagonal_step(x2, y2)
    
    
    def is_legal_diagonal_step(self, x2, y2):
        return (x2 == self.x + 1 or x2 == self.x - 1) and (y2 == self.y - 1)
    
  
    def is_legal_diagonal_jump(self, x2, y2):
        return (x2 == self.x + 2 or x2 == self.x - 2) and (y2 == self.y - 2)
    


# class for player 2 kings
class p2_king(p2_piece):
  
    def __repr__(self):
        return 'X'
    
    def is_legal_diagonal_step(self, x2, y2):
        return (x2 == self.x + 1 or x2 == self.x - 1) and (y2 == self.y + 1 or y2 == self.y - 1)
    
    
    def is_legal_diagonal_jump(self, x2, y2):
        return (x2 == self.x + 2 or x2 == self.x - 2) and (y2 == self.y + 2 or y2 == self.y - 2)
  
  
  
  
# takes a string of letters and numbers and converts them into coordinates (e.g. 'a2' -> [0, 1]).
def letter_number_parse(str):
    
    # first we split the string up into substrings representing the row and column of the input
    row = str[0]
    col = str[1:]
    
    # now we convert these strings into their corresponding coordinate values...
    row_coord = string.lowercase.index(row.lower())
    col_coord = int(col) - 1
  
    # ...and return them in a list
    return [row_coord, col_coord]



# takes a string and returns true if all its characters are integers. Used to test whether a user input is valid
def is_numbers(str):
    for c in str:
        if not c in string.digits:
            return False
    return True
  
  


# here we run the game!
game()

