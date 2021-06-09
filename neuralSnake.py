import cv2
import numpy as np
import random
from tkinter import *
import sys

class Board(object):
    def __init__(self, size=[(0, 0), (60, 80)], title='neuralSnake', bg=0, fg=1):
        self.size = size
        self.title = title
        self.bg = bg
        self.fg = fg
        self.board = np.zeros(self.size[1], np.uint8)
        self.clear()

    def clear(self):
        self.board[:] = self.bg

    def show(self, scope=10):
        h , w  = self.size[1]
        cv2.namedWindow(self.title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.title, w*scope, h*scope)
        cv2.imshow(self.title, self.board)

    def draw(self, positions, is_draw, what_draw):
        color = self.fg if is_draw else self.bg
        
        if what_draw == "snake":
            for position in positions:
                self.board[position] = color            
        elif what_draw == "food":
            self.board[positions] = color
        elif what_draw == "path":
           
            color = 20 if is_draw else self.bg
           # print(color, positions)
            for position in positions:
                self.board[position] = color

    def free(self, revert=False):
        free_block = self.fg if revert else self.bg
        return list(zip(*np.where(self.board == free_block)))

class Food(object):
    def __init__(self, board):
        self.board = board
        self.position = (0, 0)

    def randomize(self):
        self.draw(False)
        self.position = random.choice(self.board.free())
        self.draw(True)

    def draw(self, is_draw):
        self.board.draw(self.position, is_draw, "food")

class Snake(object):
    def __init__(self, board, slength=1, sdirection='6'):
        self.board = board
        self.board_limit = board.size
        self.direction = sdirection
        self.start_length = slength
        self.length = 0
        self.score = 0
        self.died = False
        self.directions = "2468"

    def check_food(self, food):
        if food.position == self.positions[0]:
            food.randomize()
            self.add_length()
            self.score += 1
            return True

    def add_length(self):
        new_position = self.positions[self.length]
        self.positions.append(new_position)
        self.length += 1

    def draw(self, is_draw):
        if self.direction in self.directions:
            self.board.draw(self.positions, is_draw, "snake")
        
    def randomize(self):
        self.positions = [ ( random.randrange(self.board_limit[0][0], self.board_limit[1][0] - 1), random.randrange(self.board_limit[0][1], self.board_limit[1][1] - 1) ) ]

    def move(self):
        pos_dir = self.possible_direcitons()
        self.directions = pos_dir if pos_dir else self.directions
        if self.direction in self.directions:
            if self.start_length > 0:
                self.start_length -= 1
                self.add_length()
            new_position = self.next_position(self.positions[0], self.direction)
            limit_check = self.point_in_rectangle(new_position, self.board_limit)
            if new_position not in self.positions and limit_check:
                self.positions.insert(0, new_position)
                self.positions.pop()
            else:
                print("GAME OVER")
                self.died = True

    def next_position(self, position, direction):
        y,x = position
        if  (direction == '8'): y -= 1 # up
        elif(direction == '2'): y += 1 # down
        elif(direction == '4'): x -= 1 # left
        elif(direction == '6'): x += 1 # right
        return (y,x)

    def possible_direcitons(self):
        ch = self.direction
        if ch in "46":
            return ch + "82"
        elif ch in "82":
            return ch + "46"
        else:
            return ""

    def point_in_rectangle(self, pos, rectangle):
        if  rectangle[0][0] <= pos[0] and \
            rectangle[0][1] <= pos[1] and \
            rectangle[1][0] >  pos[0] and \
            rectangle[1][1] >  pos[1] :
            return True
        else:
            return False

class AI(object):
    def __init__(self, board):
        self.board = board
        self.paths = []

    def is_valid(self, point, board, OPEN):
        y ,x = point
        h = len(board)   
        w = len(board[0]) 
        return ( 0 <= y < h  and 0 <= x < w ) and \
               ( board[point] in OPEN )

    def path(self, board, src, dest, OPEN=[0]):

        if not (self.is_valid(src , board, OPEN) and \
                self.is_valid(dest, board, OPEN) and \
                src != dest):
            return []
        node_queue = [ [src, 0] ]
        visited_nodes = { src: src }
        while node_queue != []:
            pt = node_queue.pop(0)
            if pt[0] == dest:
                path = [ dest ]
                while src != dest:
                    dest = visited_nodes[dest]
                    path.append(dest)
                self.paths = path[::-1]
                return self.paths
            for pos in self.directions(pt[0]):
                if ( self.is_valid(pos, board, OPEN) ) and \
                   ( not visited_nodes.get(pos) ):
                    visited_nodes[pos] = tuple( pt[0] )
                    node_queue.append([pos, pt[1]+1 ])
        return []


    def directions(self, position):
        y, x = position
        return [(y  , x+1),  
                (y  , x-1),  
                (y-1, x  ),  
                (y+1, x  )]  


    def convert_paths_to_keys(self, positions):
        keys =[]
        symbols = "6482"
        for i in range(len(positions)):
            if i < (len(positions) - 1):           
                item = positions[i]                
                nitem = positions[i+1]            
                dirs = list(self.directions(item)) 
                if nitem in dirs:                  
                    index = dirs.index(nitem)
                    keys.append(symbols[index])
        return keys

    def draw(self, is_draw):
        if self.paths != []:
            self.paths.pop(0)
        self.board.draw(self.paths, is_draw, "path")

    def ShowArray(self, arr):
        for row in arr:
            for col in row:
                print(col,end="")
                print("")

size = [(0, 0), (40, 30)]

title = 'Cursova AI Snake'

gameSpeed = 100

scope = 15

ground = (0, 200)

def newMenu(title, size):
    menu = Tk()
    menu.title(title)
    menu.geometry(size)
    menu.resizable(height=False, width=False)
    return menu

def closeMenu(menu):
    title = titleInp.get()
    gameSpeed = int(speedInp.get())
    print(size[1][0])
    size[1] = (int(sizeInpX.get()), int(sizeInpY.get()))
    scope = scopeInp.get()

    menu.quit()
    menu.withdraw()

if __name__ == "__main__":        
    menu = newMenu("Snake AI", "280x200")
    innerTitle = Label(menu, text = "Snake's Menu", font = ("Times New Roman", 14))
    innerTitle.grid(column=0, row=0, sticky = "w")

    titleLbl = Label(menu, text = "  1. Map title:\t", font = ("Times New Roman", 11))
    titleLbl.grid(column=0, row=1, sticky = "w")

    titleInp = Entry(menu, textvariable=title)
    titleInp.insert(0, 'Nuwm Snake AI')
    titleInp.place(relx=.7, rely=.21, anchor="c")
    titleInp.bind("<Return>", closeMenu)

    speedLbl = Label(menu, text = "  2. Game speed::\t", font = ("Times New Roman", 11))
    speedLbl.grid(column=0, row=2, sticky = "w")
    speedInp = Entry()
    speedInp.insert(0, 100)
    speedInp.place(relx=.7, rely=.32, anchor="c")
    speedInp.bind("<Return>", closeMenu)

    sizeLbl = Label(menu, text = "  3. Map size:\t", font = ("Times New Roman", 11))
    sizeLbl.grid(column=0, row=3, sticky = "w")

    sizeInpY = Entry(width = 10)
    sizeInpY.insert(0, 40)
    sizeInpY.place(x=166, y = 86, anchor="c")
    sizeInpY.bind("<Return>", closeMenu)

    sizeInpX = Entry(width = 10)
    sizeInpX.insert(0, 30)
    sizeInpX.place(x=226, y = 86, anchor="c")
    sizeInpX.bind("<Return>", closeMenu)

    scopeLbl = Label(menu, text = "  4. Scope:\t", font = ("Times New Roman", 11))
    scopeLbl.grid(column=0, row=4, sticky = "w")
    scopeInp = Entry()
    scopeInp.insert(0, 15)
    scopeInp.place(relx=.7, rely=.54, anchor="c")
    scopeInp.bind("<Return>", closeMenu)

    startLbl = Label(menu, text = "  5. Start AI:\t         ", font = ("Times New Roman", 11))
    startLbl.grid(column=0, row=5, sticky = "w")
    startBtn = Button(menu, text = "Go", width = 10, font = ("Times New Roman", 10), command = lambda: closeMenu(menu))
    startBtn.grid(column = 1, row = 5)
    menu.mainloop()

    cv2.destroyAllWindows()

board = Board(size, title, ground[0], ground[1])

slength = 1

snake = Snake(board, slength)

snake.randomize()

food = Food(board)

food.randomize()

ai = AI(board)

def get_key(wait):
    return chr(cv2.waitKey(wait) & 0xFF)

def render(snake):
    global gameSpeed
    global scope
    paths = []
    key = snake.direction
    while True:

        snake.check_food(food)
        
        snake.draw(False)
        snake.move()

        if snake.died: break
        ai.draw(True)
        
        snake.draw(True)
        food.draw(True)
        
        snake_head = snake.positions[0]
        food_pos = food.position
        
        board.board[snake_head] = 100
        board.board[food_pos] = 200
        
        board.show(scope)
        
        ai.draw(False)

        MAP = board.board

        MAP[food_pos] = board.bg
        MAP[snake_head] = board.bg

        if paths == []:
            paths = get_paths(MAP, snake_head, food_pos, key)
        
        direction_key = paths.pop(0)
        
        user_key = get_key(gameSpeed)

        direction_key = user_key if user_key in "+-[]2468q" else direction_key

        key = allowed_action(snake, board, direction_key)

        if key in snake.directions:
            snake.direction = key

        elif key == '+' and  gameSpeed >= 10:
            gameSpeed -= 10 if gameSpeed > 10 else 9
        elif key == '-' :
            gameSpeed += 10
        elif key == ']' : 
            scope += 1
        elif key == '[' and  scope > 2: 
            scope -= 1
        if key == 'q':
            break

def is_valid(pos, board, board_size, OPEN):
    y, x = pos
    h, w = board_size

    return ( 0 <= y < h  and 0 <= x < w ) and \
        board[y, x] in OPEN

def allowed_action(snake, board, key):
    if key in "4268":
        MAP  = board.board
        OPEN = [ board.bg, 20 ]
        snake_head = snake.positions[0]
        board_size = (board.size[1][0], board.size[1][1])
        next_action = snake.next_position(snake_head , key)

        if not is_valid(next_action, MAP, board_size, OPEN):
            allowed_directions = []
            for direction in "4268":
                next_action = snake.next_position(snake_head, direction)

                if is_valid(next_action, MAP, board_size, OPEN):
                    allowed_directions.append(direction)
            #print("allow direct:", allowed_directions)
            if allowed_directions != []:
                return allowed_directions.pop()
    return key

def get_paths(board, src, dest, key):
    keys = []
    try:
        path = ai.path(board, src, dest)
        #print("==========================")
        #print(src, dest, key)
        keys = ai.convert_paths_to_keys(path)
    except Exception as e:
        print(e)

    if keys == []:
        keys = [ key ]

    #print(f"Snake's way: { keys }")
    return keys

render(snake)

gameOver = newMenu("Snake's result", "200x40")
gameOver.resizable(height=False, width=False)
innerTitle = Label(gameOver, text = f"Snake's Score:\t{snake.length}", font = ("Times New Roman", 14))
innerTitle.grid(column=0, row=0, sticky = "w")
gameOver.mainloop()