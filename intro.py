from grid_settings import the_settings
import random
import time

###SET CONSTANTS
CELL_SIZE = 100 #so that cells are bigger than the alien

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (95, 95, 95)
GREEN = (0,255,0)
RED = (255,0,0)


GRID_WIDTH = the_settings["grid_width"]
GRID_HEIGHT = the_settings["grid_height"]
WIDTH = (GRID_WIDTH+2)*CELL_SIZE + 300
HEIGHT = (GRID_HEIGHT+2)*CELL_SIZE

BLOCKED_SQUARES = the_settings["blocked_locations"]
REWARD_LOCATIONS = the_settings["reward_locations"]

START_LOC = the_settings["start_location"]
START_X = (START_LOC[0]+1)*CELL_SIZE+50
START_Y = (START_LOC[1]+1)*CELL_SIZE+50


ALPHA = the_settings["alpha"]
GAMMA = the_settings["gamma"]
EPSILON = the_settings["epsilon"]

AUTO_ENABLED = the_settings["auto"]
ITERATIONS = the_settings["iterations"]
TIME_TO_SLEEP = the_settings["sleep_between_moves"]
PRINT_LOGS = the_settings["print_logs"]
if the_settings["default_direction"]=="L": 
    DEFAULT_MOVE = 0
elif the_settings["default_direction"]=="R":
    DEFAULT_MOVE = 1
elif the_settings["default_direction"]=="U":
    DEFAULT_MOVE = 2
elif the_settings["default_direction"]=="D":
    DEFAULT_MOVE = 3

MOVE_OPTIONS = [0, 1, 2, 3]

#create a class of squares to hold info about each grid object
class Square:
  def __init__(self, left_coor, top_coor):
    self.top_coor = top_coor #top left of where it is
    self.left_coor = left_coor #left coor of where it is
    self.rect = Rect((left_coor ,top_coor),(CELL_SIZE,CELL_SIZE)) #the rect of this square
    self.reward = 0 #the reward gained by entering this square
    self.blocked = False #if the square cannot be entered
    self.value = 0 #the td value associated with this
    self.terminating_state = False #if it starts a new game



#initalize a bunch of squares based on the size of the grid
the_squares = {}

for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):
       the_squares[(x,y)] = Square((x+1)*CELL_SIZE, (y+1)*CELL_SIZE) 


for blocked_square in BLOCKED_SQUARES:
   the_squares[blocked_square].blocked = True

for location, the_reward in REWARD_LOCATIONS.items():
   the_squares[location].reward = the_reward
   the_squares[location].terminating_state = True

#make a dictionary that holds all the next moves for each square
#key is the square id value is the list of next ids where the order is left, right, up, down
next_moves = {}
for the_id, square in the_squares.items():
    this_square_center = square.rect.center
    new_left = (max(CELL_SIZE*1.5, this_square_center[0]-CELL_SIZE), this_square_center[1])
    new_right = (min(CELL_SIZE*(GRID_WIDTH+1)-CELL_SIZE*0.5, this_square_center[0]+CELL_SIZE), this_square_center[1])
    new_up = (this_square_center[0], max(CELL_SIZE*1.5, this_square_center[1]-CELL_SIZE))
    new_down = (this_square_center[0], min(CELL_SIZE*(GRID_HEIGHT+1)-CELL_SIZE*0.5, this_square_center[1]+CELL_SIZE))
    
    options = [new_left, new_right, new_up, new_down]
    next_squares = []

    for option in options:
        for the_option_id, the_option_square in the_squares.items():
            if the_option_square.rect.collidepoint(option):
                if the_option_square.blocked:
                    next_squares.append(the_id)
                    break
                else:
                    next_squares.append(the_option_id)
                    break
                
    next_moves[the_id] = next_squares

#initialize the alien to move
alien = Actor('alien')
alien.center =  (START_X, START_Y)


#use this so that the actions slow down and people can see whats going on
actions_valid = True
iteration = 0
game_mode = "playing"

def draw():
    screen.clear()
    screen.fill(WHITE)

    #draw the basic grid
    for the_id, square in the_squares.items():
        if square.blocked:
            screen.draw.filled_rect(square.rect, GRAY)
        if (square.reward != None) and (square.reward > 0):
            screen.draw.filled_rect(square.rect, GREEN)
        if (square.reward != None) and (square.reward < 0):
            screen.draw.filled_rect(square.rect, RED)
        else:
            screen.draw.rect(square.rect, BLACK)
        
        #label each square
        screen.draw.text(f"Square ({the_id[0]},{the_id[1]})", (square.left_coor, square.top_coor), color="orange")

        #write the values for each square on the side
        the_current_val = f"Square ({the_id[0]},{the_id[1]}): {square.value:2f}"
        screen.draw.text(the_current_val, ((GRID_WIDTH+2)*CELL_SIZE, (GRID_WIDTH*the_id[1] + the_id[0])*25 + CELL_SIZE), color="orange")
    
    #draw the alien
    alien.draw()



def update():
    global actions_valid, game_mode, iteration
    if game_mode == "waiting":
        pass
    elif game_mode == "playing":
        cur_square = get_current_square()
        if AUTO_ENABLED:
            the_direction = get_new_direction(cur_square)
            is_terminated = move2(cur_square, the_direction)
            time.sleep(TIME_TO_SLEEP)
            if is_terminated:
                iteration += 1
                if iteration > ITERATIONS:
                    game_mode = "finished_all_iterations"
                else:
                    game_mode = "finished_iteration"
                    
        else:
            if keyboard.left and actions_valid:
                is_terminated = move2(cur_square, 0)
                if is_terminated:
                    game_mode = "finished_iteration"
            elif keyboard.right and actions_valid:
                is_terminated = move2(cur_square, 1)
                if is_terminated:
                    game_mode = "finished_iteration"
            elif keyboard.up and actions_valid:
                is_terminated = move2(cur_square, 2)
                if is_terminated:
                    game_mode = "finished_iteration"
            elif keyboard.down and actions_valid:
                is_terminated = move2(cur_square, 3)
                if is_terminated:
                    game_mode = "finished_iteration"

    elif game_mode == "finished_iteration":
        reset_board()
        game_mode = "playing"
        time.sleep(0.5)
    elif game_mode == "finished_all_iterations":
        for i in range(GRID_HEIGHT):
            row = ""
            for j in range(GRID_WIDTH):
                value = the_squares[(j,i)].value
                if value > 0:
                    row += f" {the_squares[(j,i)].value:2f} " 
                else:
                    row += f" {the_squares[(j,i)].value:2f} " 
            print(row)
        game_mode = "waiting"


        


def move2(current_square_id, direction):
    global actions_valid
    #get the next square based on the direction
    next_square_id = next_moves[current_square_id][direction]

    #print logs if needed
    if PRINT_LOGS:
        directions_to_words = {
            0:"L", 1:"R", 2:"U", 3:"D"
        }
        print(f"From square {current_square_id} took action {directions_to_words[direction]} and ended up in square {next_square_id}")

    #get both the current and new squares in square not id form
    current_square = the_squares[current_square_id]
    next_square = the_squares[next_square_id]

    #update the alien position
    alien.center = next_square.rect.center

    #update the old squares estimated value 
    current_square.value = ((1-ALPHA) * current_square.value) + (ALPHA * (next_square.reward + (GAMMA * next_square.value)))    
    
    #if the new square was a terminating state reset the game
    if next_square.terminating_state:
        return True
                
    #otherwise pause actions for a second 
    actions_valid = False
    clock.schedule(reset_actions, 0.5)

    return False

def reset_board():
    alien.center =  (START_X, START_Y)


def reset_actions():
    global actions_valid
    actions_valid = True

def get_new_direction(cur_square):
    if random.random() > EPSILON:
        the_move_direction = random.choice(MOVE_OPTIONS)
    else:
        the_moves = next_moves[cur_square]
        
        most_value = the_squares[the_moves[0]].value
        the_move_direction = 0
        all_same = True

        for i, move in enumerate(the_moves):
            the_val = the_squares[move].value
            if the_val != most_value:
                all_same = False
            if the_val > most_value:
                most_value = the_val
                the_move_direction = i
        
        if all_same:
            the_move_direction = DEFAULT_MOVE

    return the_move_direction

def get_current_square():
    for id, square in the_squares.items():
        if square.rect.collidepoint(alien.center):
            return id