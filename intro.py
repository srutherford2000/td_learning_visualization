CELL_SIZE = 100

class Square:
  def __init__(self, top_left_coor):
    self.top_left_coor = top_left_coor
    self.rect = Rect(top_left_coor,(CELL_SIZE,CELL_SIZE))
    self.reward = -0.01
    self.blocked = False
    self.value = 0
    self.terminating_state = False


alien = Actor('alien')


WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (95, 95, 95)
GREEN = (0,255,0)
RED = (255,0,0)

the_squares = {}

grid_width = 4 #int(float(input("enter the width of the grid: ")))
grid_height = 3 #int(float(input("enter the heigh of the grid: ")))

for x in range(grid_width):
    for y in range(grid_height):
       the_squares[(x,y)] = Square(((x+1)*CELL_SIZE ,(y+1)*CELL_SIZE)) 

blocked_squares = "(1,1)"
#input(
#"""enter squares that are blocked in list form
#    ex: in the 3x2 grid below if the x's were blocked
#    [x|  |  ]
#    [ |  | x]
#    you would type: (0,0), (2,1)
#""")

blocked_squares = blocked_squares.split(", ")
for blocked_square in blocked_squares:
   blocked_square = blocked_square[1:-1]
   x,y = blocked_square.split(",")
   the_squares[(int(float(x)),int(float(y)))].blocked = True

reward_squares = "(3,0):10, (3,1):-5"
#input(
#"""enter squares that have rewards/penalties in list form
#    ex: in the 3x2 grid below if the numbers are reward/penalty values
#    [100|  |   ]
#    [   |  |-87]
#    you would type: (0,0):100, (2,1):-87
#""")
reward_squares = reward_squares.split(", ")
for reward_square in reward_squares:
   location, the_reward = reward_square.split(":")
   location = location[1:-1]
   x,y = location.split(",")
   the_squares[(int(float(x)),int(float(y)))].reward = int(float(the_reward))
   the_squares[(int(float(x)),int(float(y)))].terminating_state = True

start_loc = (0,2)
start_x = (start_loc[0]+1)*CELL_SIZE+50
start_y = (start_loc[1]+1)*CELL_SIZE+50

alien.center =  (start_x, start_y)

WIDTH = (grid_width+2)*CELL_SIZE + 300
HEIGHT = (grid_height+2)*CELL_SIZE

actions_valid = True


alpha = 0.1
gamma = 1



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
        screen.draw.text(f"Square ({the_id[0]},{the_id[1]})", square.top_left_coor, color="orange")

        #write the values for each square on the side
        the_current_val = f"Square ({the_id[0]},{the_id[1]}): {square.value}"
        screen.draw.text(the_current_val, ((grid_width+2)*CELL_SIZE, (grid_width*the_id[1] + the_id[0])*25 + CELL_SIZE), color="orange")
    
    #draw the alien
    alien.draw()



def update():
    global actions_valid
    if keyboard.left and actions_valid:
        move(-CELL_SIZE, 0)
    elif keyboard.right and actions_valid:
        move(CELL_SIZE, 0)
    elif keyboard.up and actions_valid:
        move(0, -CELL_SIZE)
    elif keyboard.down and actions_valid:
        move(0, CELL_SIZE)



def move(x_change, y_change):
    global actions_valid
    #get the old information about the alien x/y and the square it was in
    old_x = alien.x
    old_y = alien.y

    old_square_id = None
    for id, square in the_squares.items():
        if alien.colliderect(square.rect):
            old_square_id = id
            break

    #move the position in accordance with the new movment
    alien.x += x_change
    alien.x = max(CELL_SIZE*1.5, alien.x)
    alien.x = min(CELL_SIZE*(grid_width+1)-CELL_SIZE*0.5, alien.x)
    
    alien.y += y_change
    alien.y = max(CELL_SIZE*1.5, alien.y)
    alien.y = min(CELL_SIZE*(grid_height+1)-CELL_SIZE*0.5, alien.y)

    
    #do the calculations based on the new square we ended up in and the old square
    for square in the_squares.values():
        if alien.colliderect(square.rect):
            if square.blocked:
                alien.x = old_x
                alien.y = old_y
                
                the_squares[old_square_id].value = ((1-alpha) * the_squares[old_square_id].value) + (alpha*(the_squares[old_square_id].reward + gamma*the_squares[old_square_id].value))
                break
            else:
                the_squares[old_square_id].value = ((1-alpha) * the_squares[old_square_id].value) + (alpha*(square.reward +  gamma*square.value))
                
            
            if square.terminating_state:
                print("THIS IS THE END OF THE GAME")
                clock.schedule(reset_board, 0.5)
                break
            
    actions_valid = False
    clock.schedule(reset_actions, 0.5)


def reset_board():
    alien.center =  (start_x, start_y)


def reset_actions():
    global actions_valid
    actions_valid = True