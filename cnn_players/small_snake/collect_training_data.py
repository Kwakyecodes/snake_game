"""
Characters: 
1. Snake 
2. Food

Game:
1. The task is for the snake to find the food.
2. The food starts at a random position on the screen and respawns at another point
after being eating.
3. The snake doesn't grow. It just continues eating the food until the game is ended.

ML Information:
1. Screen size is 60 by 80.
2. Each training input is a matrix of size 6 by 8.
3. Each label/class is a single number: 0 -> UP, 1 -> RIGHT, 2 -> DOWN, 3 -> LEFT.
4. Value of snake in the matrix is 11.
5. Value of food in the matrix is 6.
6. Paths in the matrix are 0.
"""

import pygame
import pickle
import numpy as np
from collections import deque
from characters import (
    # Characters
    Snake, 
    Food, 
    
    # Display variables
    win_height,
    win_width,
)

# Get absolute path of current directory
import os
current_dir = os.path.dirname(__file__)

def labeler(direction):
    # Change direction(string) to discrete value for labeling
    converter = {
        "UP": 0,
        "RIGHT": 1,
        "DOWN": 2,
        "LEFT": 3,
    }
    return converter[direction]

def update_matrix(matrix, snake, food):
    """Update the position of characters in matrix"""
    
    # Update snake on matrix
    matrix[snake[1]//10][snake[0]//10] = 11
    
    # Update food in matrix
    matrix[food[1]//10][food[0]//10] = 6 
    
    return matrix


def make_next_move(matrix, head, food):
    """Select next move of snake"""
    
    h, w = len(matrix), len(matrix[0])
    visited = [[False for _ in range(w)] for _ in range(h)]
    directions = [ 
        {"name": "LEFT", "value": (0, -1)},
        {"name": "UP", "value": (-1, 0)},
        {"name": "RIGHT", "value": (0, 1)},
        {"name": "DOWN", "value": (1, 0)}, 
    ]
    head = (head[1]//10, head[0]//10) # Scale position of head and reverse for numpy
    food = (food[1]//10, food[0]//10) # Scale position of food and reverse for numpy
    visited[head[0]][head[1]] = True # Mark the position of head as visited
    queue = deque([[head]]) # Initialise queue unique paths with position of snake's head
    
    move = None
    while queue:
        path = queue.popleft()
        curr = path[-1]
        
        # Stop searching and make move when food is found OR
        if matrix[curr[0]][curr[1]] == 6:
            move = path[1] # Set move to next step from head   
            break
        
        # Find next possible moves
        for d in directions:
            
            y, x = d["value"]
            next_y, next_x = curr[0] + y, curr[1] + x
            next_coord = (next_y, next_x)
            
            # Skip moves where snake crashes into wall
            if (next_y < 0 or next_y >= h or next_x < 0 or next_x >= w):
                continue
            
            # Skip nodes that have already been visited
            if visited[next_y][next_x]:
                continue
        
            queue.append(path + [next_coord])
            visited[next_y][next_x] = True 
           
    if move:        
        # Select direction 
        move_pos = (move[0] - head[0], move[1] - head[1])
        for d in directions:
            if d["value"] == move_pos:
                move = d["name"] # Change move to direction name
                break   
    return move
   
def game_loop():
    """Main game loop"""

    # Constants
    SNAKE_SPEED = 24
    SNAKE_COLOR = (255, 255, 255)
    FOOD_COLOR = (0, 0, 255)
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)

    # Set up game clock
    clock = pygame.time.Clock()

    # Initialize Pygame
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))

    score = 1
    snake = Snake() # Spawns snake at level 1
    food = Food() # Initiates with no food at random position; could be position of snake but what are the chances :) 
    
    m = 0  # Space of the training set
    
    while True:
        # End game when enough data has been collected
        if m == 10000:
            break
            
        # Zero all cells in matrix
        matrix = np.zeros((win_height//10, win_width//10))
        
        # Update cells of matrix
        matrix = update_matrix(matrix, snake.body[0], food.position)
        
        # Collect new data point into pickle file
        with open(os.path.abspath(os.path.join(current_dir, 'static', 'train.pkl')), 'ab') as f:
            pickle.dump(matrix, f)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        # Reset direction of snake
        snake.direction = make_next_move(
            matrix=matrix, 
            head=snake.body[0], 
            food=food.position, 
        )

        # Collect new label into pickle file
        with open(os.path.abspath(os.path.join(current_dir, 'static', 'label.pkl')), 'ab') as f:
            pickle.dump(labeler(direction=snake.direction), f)
        
        m += 1  # increase m by 1 after every new data collected

        # Move the snake
        snake.grow() 
                    
        # Logic for eating food and spawning new one
        if snake.body[0] == food.position:
            score += 1
            food.spawn_new_food(matrix=matrix)
            
        # Remove last segment whether food is eaten or not. 
        # To prevent snake from growing
        snake.shrink()
            
        # Update cells of matrix (effect change in food's position)
        matrix = update_matrix(matrix, snake.body[0], food.position)
        
        win.fill(BG_COLOR)
        pygame.draw.rect(win, SNAKE_COLOR, pygame.Rect(snake.body[0][0], snake.body[0][1], snake.size, snake.size))
        pygame.draw.rect(win, FOOD_COLOR, pygame.Rect(food.position[0], food.position[1], food.size, food.size))
                
        pygame.display.update()
        clock.tick(SNAKE_SPEED)
                
    # Display final scores
    print(score)
        
    # End game
    pygame.quit()


# Command to run game
if __name__ == "__main__":
    game_loop()