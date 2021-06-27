import sys
import random
import os
import colors


# choose design here:
DEFAULT_CHARACTER = "."
DEFAULT_CHARACTER_SHIP = colors.ICyan + "S" + colors.Color_Off
DEFAULT_CHARACTER_HIT = colors.IRed + "X" + colors.Color_Off
DEFAULT_CHARACTER_MISS = colors.IGreen + "O" + colors.Color_Off


def clearConsole():
    #should clear the current screen in the console
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def checkInput(a, amax):
    #check if a string <<a>> is a numeral between zero and amax
    if (not a.isnumeric()):
        return False
    elif ((int(a) < 0 )or (int(a) > amax )):
        return False
    else:
        return True

def printOperation(x):
    #evaluates a string x for varius commands and executes them.
    help = """##########################################
    Helpscreen for the game battleships. Useful commands:
    help        - shows this screen
    restart     - restarts the game
    exit        - quits the current game
    
    How to play:
        At the start of the game, you can choose to play 
        with the standard settings (recommended):
            10x10 board with 4,3,2,1 Ships
        Or fit the game-parameters to your liking
        
        Coordinates to place your ships and fire a 
        barrage are requested by the programm and
        have to be inserted with the keyboard. If
        the input is nonsense, (i.e. a character for
        a coordinate) the player is prompted to 
        repeat his input. 
        
        Both players should play fairly and not peek
        at the screen when the partner is playing.
    
    """
    if (x == "help"):
        print(help)
    if (x == "restart"):
        python = sys.executable
        os.execl(python, python, *sys.argv)
    if (x == "exit"):
        sys.exit()





def overlap(x, y, o, board, size):
    #check if the given board, together with a ship at position (x,y), produces an illegal gamestate
    xmax = len(board[0]) - 1
    ymax = len(board) - 1

    #First, check if the origin of the ship or any adjacent position is occupied:
    # If that is the case, we have an overlap
    if (board[x][y] == DEFAULT_CHARACTER_SHIP):
        return True
    if searchNeighbors(x, y, board):
        return True

    #We need to get the orientation of the ship to evaluate further:
    #Example:
    #     0 1 2 3       For this board and a ship of size 3, the input (1, 0) is fine
    #  0  . . . .       with a horizontal orientation, but creates an illegal board for
    #  1  . . . .       a vertical orientation. [If two ship-characters S are adjacent
    #  2  . . S .       on the board, they must be from the same ship]
    #  3  . . . .

    #first, check wether the ship with the chosen orientation actually fits on the board
    if ((o == "h") and (x + size - 1 >= len(board[0]))):
        return True
    if ((o == "v") and (y + size - 1 >= len(board))):
        return True
    #since we already checked the first position of the ship for neighbors, we now check the last one:
    if (o == "h"):
        if searchNeighbors(x + size - 1, y, board):
            return True
    if (o == "o"):
        if searchNeighbors(x, y + size - 1, board):
            return True
    #Now iterate over the full length of the ship and check for illegal boards:
    #[no other ships adjacent or overlapping]
    for i in range(size):
        if (o == "h"):
            if ((board[x + i][y] == DEFAULT_CHARACTER_SHIP) or (
                    board[x + i][min(ymax, y + 1)] == DEFAULT_CHARACTER_SHIP) or (
                    board[x + i][max(0, y - 1)] == DEFAULT_CHARACTER_SHIP)):
                return True
        if (o == "v"):
            if ((board[x][y + i] == DEFAULT_CHARACTER_SHIP) or (
                    board[min(xmax, x + 1)][y + i] == DEFAULT_CHARACTER_SHIP) or (
                    board[max(0, x - 1)][y + i] == DEFAULT_CHARACTER_SHIP)):
                return True
    #if we didn't return True until now, we have a legal placement of the ship on the given board.

def searchNeighbors(x, y, board):
    #checks the position (x,y) and it's adjacent positions for ships on a given board:
    xmax = len(board[0])
    ymax = len(board)

    #search-space is {(x,y+1), (x,y-1), (x+1,y), (x-1,y)}
    space = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for coords in space:
        x1 = x + coords[0]
        y1 = y + coords[1]
        if (((x1 >= 0) and (x1 < xmax)) and ((y1 >= 0) and (y1 < ymax))):
            #if we find a ship on the board we have found a neighbor
            if (board[x1][y1] == DEFAULT_CHARACTER_SHIP):
                return True


class GameState(object):
    #The GameState object manages the game. The game-parameters are set in it's constructor
    #and it passes them on to the subsequently created Player-objects.
    #set the game-parameters in the constructor:
    def __init__(self, x=10, y=10, n1=4, n2=3, n3=2, n4=1):
        self.x = x
        self.y = y
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        self.p1 = Player(x, y, n1, n2, n3, n4)
        self.p2 = Player(x, y, n1, n2, n3, n4)

    def initBoard(self):
        #initialize the boards for the players
        self.p1Board = []
        self.p2Board = []
        for i in range(self.x):
            self.p1Board.append([])
            self.p2Board.append([])
            for j in range(self.y):
                self.p1Board[i].append(DEFAULT_CHARACTER)
                self.p2Board[i].append(DEFAULT_CHARACTER)
        print("Player 1, please place your ships!")
        #request players to place his ships on the board.
        # Additionaly, save a list of the ships as an attribute
        self.p1Board, self.p1Ships = self.p1.requestPlacement(self.p1Board)
        print("Player 1 finished the placement of his ship. Press any key to continue!")
        input("")
        clearConsole()
        print("Player 2, please place your ships!")
        self.p2Board, self.p2Ships = self.p2.requestPlacement(self.p2Board)
        print("Player 2 finished the placement of his ship. Press any key to continue!")
        input("")
        clearConsole()

    def startGame(self):
        #starts the game-loop
        #First, randomize the starting player. The turns of each player are
        #managed by a toggle variable: toggle \in {0,1}
        #current player,ship,board can then be accest by list[toggle]
        running = True
        player = [self.p1, self.p2]
        board = [self.p2Board, self.p1Board]
        ships = [self.p2Ships, self.p1Ships]
        toggle = random.getrandbits(1)
        clearConsole()
        print("The game is about to start. Get ready!\n")
        #variable running signals if the game is still going
        while running:
            #toggle gets flipped
            toggle = (toggle + 1) % 2

            print("Player " + str(toggle + 1) + ", please make your move!")
            #request a move from the current player and subsequently evaluate it
            x, y = player[toggle].requestMove(board[toggle])
            hit, sunk, ship = self.checkBarrage(x, y, toggle)
            if hit:
                board[toggle][x][y] = DEFAULT_CHARACTER_HIT
            else:
                board[toggle][x][y] = DEFAULT_CHARACTER_MISS
                print("You missed D:")
            #send data about the barrage [move] to the player so he can update his own guessBoard:
            player[toggle].updateBoard(x, y, hit, sunk, ship)
            # check game status by evaluating the boolean of the list of ships
            #[if ship empty, -> all ships of player have been sunk -> evaluates to False -> game over]
            running = bool(ships[toggle])
            print("End of your turn. Press any key to continue.")
            input("")
            if (running):
                clearConsole()
        print(colors.Purple + "Congratulations! Player " + str(toggle + 1) + " won the Game!" + colors.Color_Off)

    def checkBarrage(self, x, y, toggle):
        #evaluates a barrage on position (x,y). Differentiates between: {miss, hit, sunk}
        board = [self.p2Board, self.p1Board]
        ships = [self.p2Ships, self.p1Ships]
        if (board[toggle][x][y] == DEFAULT_CHARACTER_SHIP):
            #if a a ship is on position (x,y), we have to find wich ship is
            #going to be hit. Each ship-object knows it's own corrdinates,
            #so we just have to ask each ship in the list of the player, wether
            #it is hit.
            k = 0
            for ship in ships[toggle]:
                if (ship.check(x, y)):
                    print("That was a clean hit!")
                    #then, a quick check if the hit would sink the boat
                    #[last living position of the ship is hit]
                    if not (ship.alive()):
                        ships[toggle].pop(k)
                        print("You sank a boat!")
                        #if we have sunk a ship:
                        #return (hit:True, sunk:True, reference of the sunk ship)
                        #[-> we can then delete this ship from the list]
                        return True, True, ship
                    #if we have hit a ship, but it is still alive:
                    #return (hit:True, sunk:False, no reference to a ship)
                    #[so that we don't delete a ship from the list that is still alive!]
                    return True, False, None
                k += 1

        else:
            #if we hit open waters:
            #return (hit:False, sunk:False, None)
            return False, False, None


class Player(object):
    #Created by the GameState object. A Player has its own (at the start empty) board [guessBoard],
    #where it can save the moves and hits.
    def __init__(self, x, y, n1, n2, n3, n4):
        self.x = x
        self.y = y
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.n4 = n4
        #A player has a board where he marks his hits and misses!
        self.guessBoard = []
        for i in range(x):
            self.guessBoard.append([])
            for j in range(y):
                self.guessBoard[i].append(DEFAULT_CHARACTER)


    def printBoard(self, board):
        #prints the given board to the console.... ~.~"
        numbers = " "
        border = ""
        for i in range(len(board[0])):
            numbers += str(i) + " "
            border += "##"
        print(" " + numbers)
        for i in range(len(board)):
            line = str(i) + " "
            for j in range(len(board[i])):
                line += board[j][i] + " "
            print(line)


    def requestMove(self, board):
        #The player is prompted to input (x,y) coordinates for a barrage.
        #Illegal inputs are ignored and repeated
        xmax = len(board[0]) -1
        ymax = len(board) -1
        print("\n")
        self.printBoard(self.guessBoard)
        print("\n")

        #request input for x and y coordinates. While the input is faulty, repeat.
        x = input("x-coordinate of barrage: ")
        printOperation(x)
        while( not checkInput(x,xmax)):
            print("Please only use numerals as the input and it should be between " + "0 and " + str(xmax) )
            x = input("x-coordinate of barrage: ")
            printOperation(x)
        x = int(x)

        y = input("y-coordinate of barrage: ")
        printOperation(y)
        while (not checkInput(y, ymax)):
            print("Please only use numerals as the input and it should be between " + "0 and " + str(ymax) )
            y = input("x-coordinate of barrage: ")
            printOperation(y)
        y = int(y)
        print("\n")
        #return the coordinates
        return (x, y)

    def updateBoard(self, x, y, hit, sunk=False, ship=None):
        #Takes data from the GameState-Object and updates the guessBoard
        #to represent the new information for the user.
        xmax = len(self.guessBoard[0])
        ymax = len(self.guessBoard)
        #the result of the barrage on (x,y) gets updated:
        if hit:
            self.guessBoard[x][y] = DEFAULT_CHARACTER_HIT
        else:
            self.guessBoard[x][y] = DEFAULT_CHARACTER_MISS
        #if a ship is sunk, we search and mark all adjacent positions
        #of any coordinate of the ship as MISS, because the rules of
        #battleships dictate, that no other ship may be in these
        #positins. This helps the player strategize.
        if sunk:
            #search-space is {(x_i,y_i+1), (x_i,y_i-1), (x_i+1,y_i), (x_i-1,y_i)}
            #where (x_i,y_i) is the ith coordinate of the ship that got sunk.
            space = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for i in ship.coordinates:
                for j in space:
                    x1 = i[0] + j[0]
                    y1 = i[1] + j[1]
                    if (((x1 >= 0) and (x1 < xmax)) and ((y1 >= 0) and (y1 < ymax))):
                        if (self.guessBoard[x1][y1] == DEFAULT_CHARACTER):
                            self.guessBoard[x1][y1] = DEFAULT_CHARACTER_MISS
        self.printBoard(self.guessBoard)
        print("\n")

    def requestPlacement(self, board):
        # Requires an input of the player to place his ships on the given board.
        # number of ships, etc. are defined by the game-parameters.
        # Inputs that would lead to an illegal board are ignored. In that case,
        # the player is prompted to repeat his inputs.
        xmax = len(board[0]) - 1
        ymax = len(board) - 1
        #save the number of ships with length n \in {1,2,3,4} in a list
        #we will then place a ship of length n and decrease the counter by one.
        #when the counter reaches zero, remove the counter from the list
        #   ---> as long as todolist is not empty, we have ships to place.
        todo = [self.n1, self.n2, self.n3, self.n4]


        self.printBoard(board)
        currentSize = 1
        #splace created ship-objects in this list to return them to the GameState.
        ships = []
        # as long as ships are left to place, do this loop
        while (todo):
            #if the counter of current size in the todolist is zero, remove the element
            if (todo[0] == 0):
                todo.pop(0)
                currentSize += 1
                continue

            fault = True
            shipCoordinates = []
            #here, we check the inputs. While the input is illegal, repeat the process.
            #First, check if th input fits on the current board.
            while (fault):
                fault = False
                print("x - coordinate of ship with length " + str(currentSize))
                x = input("x: ")
                printOperation(x)
                while (not checkInput(x, xmax)):
                    print("Please only use numerals as the input and the ship should fit on the board")
                    x = input("x: ")
                    printOperation(x)
                x = int(x)
                print("y - coordinate of ship with length " + str(currentSize))
                y = input("y: ")
                printOperation(y)
                while (not checkInput(y, ymax)):
                    print("Please only use numerals as the input and the ship should fit on the board")
                    y = input("y: ")
                    printOperation(y)
                y = int(y)

                o = input("orientation of ship with length " + str(currentSize) + " [h/v]: ")
                printOperation(o)
                while (o not in ["h","v"]):
                    print("Please specify the orientation of the ship. Either horizontal[h] or vertical[v].")
                    o = input("orientation of ship with length " + str(currentSize) + " [h/v]: ")
                    printOperation(o)
                #Now we have to check if the ship with origin (x,y) and orientation o will fit on the board!
                #And overlap() looks for overlapping/adjacent ships.
                if overlap(x, y, o, board, currentSize):
                        #in case it doesn't, the player has to position the ship again.
                    fault = True
                    print("you have another ship overlapping the current one!")
            #after placing a ship with legal coordinates, decrement the counter of ships with
            #the current size
            todo[0] -= 1
            #Now we can place the ship on the board and use the occupied coordinates to
            #create a ship-object
            if (o == 'v'):
                for i in range(currentSize):
                    board[x][y + i] = DEFAULT_CHARACTER_SHIP
                    shipCoordinates.append([x, y + i])
            if (o == 'h'):
                for i in range(currentSize):
                    board[x + i][y] = DEFAULT_CHARACTER_SHIP
                    shipCoordinates.append([x + i, y])

            clearConsole()

            self.printBoard(board)
            #append the Ship-object to the list of ships
            ships.append(Ship(shipCoordinates))
        #after placing all ships, return the modified board and the list of Ship-objects
        return board, ships


class Ship(object):
    #Ship-objects are created to ease the management of the gamestate. A Ship-object knows
    #its own coordinates, as well as where it was hit already. Therfore, it also knows if
    #it is alive or not. The GameState can just ask a ship wether it is sunk or not!
    def __init__(self, coordinates):
        #save the coordinates of the ship in here
        self.coordinates = coordinates
        #a hit is registered in the self.hits list
        self.hits = []
        for i in range(len(coordinates)):
            self.hits.append(False)

    def check(self, x, y):
        #the ship can be asked, if a certain position (x,y) would be a hit
        k = 0
        #to do this, iterate over the coordinates and if the position is found,
        #we register a hit in self.hits and return
        #the boolean True [because we have a hit]
        for i in self.coordinates:
            if [x, y] == i:
                self.hits[k] = True
                return True
            k += 1

    def alive(self):
        #evaluate the and-operator for dead=True and elements in the
        #hit list. If the ship is alive, one of the elements in self.hits
        #is False, and dead will be False aswell
        dead = True
        for hit in self.hits:
            dead = dead and hit
        return not dead

#Sketch for Single-Player
"""class Computer(Player):
    def strategize(self):
        if not (self.strategy):
            #TODO: implement logic to search a potential move
            pass
        else:
            pass

    def requestMove(self, board):
        x, y = self.strategize()
        return(x, y)

    def updateBoard(self, x, y, hit, sunk=False, ship=None):
        xmax = len(self.guessBoard[0])
        ymax = len(self.guessBoard)
        if hit:
            self.guessBoard[x][y] = DEFAULT_CHARACTER_HIT
        else:
            self.guessBoard[x][y] = DEFAULT_CHARACTER_MISS
        if sunk:
            space = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for i in ship.coordinates:
                for j in space:
                    x1 = i[0] + j[0]
                    y1 = i[1] + j[1]
                    if (((x1 >= 0) and (x1 < xmax)) and ((y1 >= 0) and (y1 < ymax))):
                        if (self.guessBoard[x1][y1] == DEFAULT_CHARACTER):
                            self.guessBoard[x1][y1] = DEFAULT_CHARACTER_MISS
        self.printBoard(self.guessBoard)
        print("\n")

    def requestPlacement(self, board):
        self.strategy = []
        todo = [self.n1, self.n2, self.n3, self.n4]
        # as long as ships are left to place, do this loop

        # this is for quick testing and will be deleted later
        self.strategy = []
        currentSize = 1
        ships = []
        while (todo):

            if (todo[0] == 0):
                todo.pop(0)
                currentSize += 1
                continue
            # check for wrong inputs
            fault = True
            shipCoordinates = []

            while (fault):
                fault = False
                r = random.getrandbits(1)
                if r:
                    o = "h"
                    x = random.randint(0, self.x - currentSize)
                    y = random.randint(0, self.y - 1)
                else:
                    o = "v"
                    x = random.randint(0, self.x - 1)
                    y = random.randint(0, self.y - currentSize)

                if overlap(x, y, o, board, currentSize):
                    fault = True

            todo[0] -= 1
            if (o == 'v'):
                for i in range(currentSize):
                    board[x][y + i] = DEFAULT_CHARACTER_SHIP
                    shipCoordinates.append([x, y + i])
            if (o == 'h'):
                for i in range(currentSize):
                    board[x + i][y] = DEFAULT_CHARACTER_SHIP
                    shipCoordinates.append([x + i, y])
            self.printBoard(board)

            ships.append(Ship(shipCoordinates))

        return board, ships


"""


#Here, the player may choose different settings for the game. Either start with standard settings
#i.e. ten by ten playing filed with 4,3,2,1 ships of length 1,2,3,4. All inputs are checked for
#illegal inputs and may prompt the player to repeat it's input.
print("Welcome to Battleships - Multiplayer! Would you like to play with the standard settings?")
x = input("y/n: ")
printOperation(x)


while (x not in ["y", "n", "Y", "N"]):
    x = input("y/n")
    printOperation(x)
#if the player wishes to play with standard settings, we create the GameState-object with
#standard parameters.
if ((x == "y") or (x == "Y")):
    game = GameState()
else:
    x = (input("Choose width of the Board: "))
    printOperation(x)
    while (not checkInput(x, 1000)):
        print("Please use an Integer as input! ")
        x = (input("Choose width of the Board: "))
        printOperation(x)
    x = int(x)

    y = input("Choose height of the Board: ")
    printOperation(y)
    while (not checkInput(y, 1000)):
        print("Please use an Integer as input! ")
        y = input("Choose height of the Board: ")
        printOperation(y)
    y = int(y)

    n1 = input("Choose number of submarines (ships of length one): ")
    printOperation(n1)
    while (not checkInput(n1, 1000)):
        print("Please use an Integer as input! ")
        n1 = input("Choose number of submarines (ships of length one): ")
        printOperation(n1)
    n1 = int(n1)


    n2 = input("Choose number of destroyer (ships of length two): ")
    printOperation(n2)
    while (not checkInput(n2, 1000)):
        print("Please use an Integer as input! ")
        n2 = input("Choose number of destroyer (ships of length two): ")
        printOperation(n2)
    n2 = int(n2)

    n3 = input("Choose number of cruiser (ships of length three): ")
    printOperation(n3)
    while (not checkInput(n3, 1000)):
        print("Please use an Integer as input! ")
        n3 = input("Choose number of cruiser (ships of length three): ")
        printOperation(n3)
    n3 = int(n3)

    n4 = input("Choose number of battleship (ships of length four): ")
    printOperation(n4)
    while (not checkInput(n4, 1000)):
        print("Please use an Integer as input! ")
        n4 = input("Choose number of battleship (ships of length four): ")
        printOperation(n4)
    n4 = int(n4)
    #otherwise, set the game-parameters to the chosen inputs.
    game = GameState(x, y, n1, n2, n3, n4)
#tell the GameState-object to initialize the board and start the game.
game.initBoard()
game.startGame()
