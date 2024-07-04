# CLASSES OF THE CHARACTERS IN THE GAME
import random

# Set up display variables
win_width = 80
win_height = 60

def find_empty_cell(matrix):
    empty_cells = []
    for r, row in enumerate(matrix):
        for c, col in enumerate(row):
            if col == 0:
                empty_cells.append((c, r))
                
    rand_pos = random.choice(empty_cells)
    return rand_pos

class Snake:
    def __init__(self):
        self.size = 10
        self.body = [(40, 30)]
        self.direction = "RIGHT"

    def grow(self):
        """Adds one segment to the snake's body """
        if self.direction == "UP":
            self.body.insert(0, (self.body[0][0], self.body[0][1]-self.size))
        elif self.direction == "DOWN":
            self.body.insert(0, (self.body[0][0], self.body[0][1]+self.size))
        elif self.direction == "RIGHT":
            self.body.insert(0, (self.body[0][0]+self.size, self.body[0][1]))
        else: # self.direction == "LEFT"
            self.body.insert(0, (self.body[0][0]-self.size, self.body[0][1]))
    
    def shrink(self):
        """Removes the last segment of the snake's body"""
        self.body.pop()
        
class Food:
    def __init__(self):
        self.size = 10
        self.position = (random.randrange(1, win_width/10)*self.size, random.randrange(1, win_height/10)*self.size)
        
    def spawn_new_food(self, matrix):
        """Spawns a new food at a random position on the map"""
        new_food_pos = find_empty_cell(matrix=matrix)
        self.position = (new_food_pos[0]*self.size, new_food_pos[1]*self.size)