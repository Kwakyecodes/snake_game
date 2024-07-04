"""
Characters: 
1. Snake 
2. Food
3. Explosives

Game:
1. The task is for the snake to find the food and avoid any explosives and the wall.
2. The food starts at a random position on the screen and respawns at another point
after being eating.
3. The snake grows 1 unit longer every time it eats one food.

ML Information:
1. Screen size is 600 by 800.
2. Each training input is a matrix of size 7 by 7; the square matrix around the head of the snake.
3. The idea behind this is that the snake doesn't necessarily need to see the food to find it. If it is
given a sense of where the food might be, even if the food is not in sight, it probably should be able to 
find it (or at least move closer to it).
4. Each label/class is a single number: 0 -> UP, 1 -> RIGHT, 2 -> DOWN, 3 -> LEFT.
5. Value of snake in the matrix is 0.
6. Value of food in the matrix is 10+.
7. Paths in the matrix are [1, 13] depending on their distance from food. The closer the point from
food the bigger the number.
8. Data is only taken on the every 3 iterations
"""

import pygame
import pickle
import numpy as np
from collections import deque

# Include top level modules
import os, sys
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..', '..')))

from characters import (
    # Characters
    Snake, 
    Food, 
    Explosive,
    
    # Display variables
    win_height,
    win_width,
)

def update_matrix(curr_matrix, snakes, food, explosives):
    """Update the position of characters in matrix"""
    
    # Update snakes's body and explostions in matrix
    # Switch x and y because of numpy (height -> row, width -> column)
    for pos in (snakes + explosives):
        x, y = pos[0]//10, pos[1]//10
        curr_matrix[y][x] = 2
    
    # Update food in matrix
    x, y = food[0]//10, food[1]//10
    curr_matrix[y][x] = 1  
    
    return curr_matrix

def labeler(direction):
    # Change direction(string) to discrete value for labeling
    converter = {
        "UP": 0,
        "RIGHT": 1,
        "DOWN": 2,
        "LEFT": 3,
    }
    return converter[direction]

def compute_distance(pos1, pos2):
    """Helper function to calculate the distance between two points"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_decision_matrix(matrix, snake_head, food):
    """Decision matrix generator
    Update: Changing decision matrix to 5 by 5"""
    h, w = len(matrix), len(matrix[0])
    food_pos = (food[1]//10, food[0]//10)
    snake_head_pos = (snake_head[1]//10, snake_head[0]//10)
    open_paths = {}
    res = np.zeros((5, 5))
    
    for i in range(5):
        row = snake_head_pos[0] - 2 + i
        for j in range(5):
            col = snake_head_pos[1] - 2 + j
            # Set walls to -15 in decision matrix
            if (row < 0 or row >= h or col < 0 or col >= w):
                res[i][j] = -10
            # Set head of snake to 0 in decision matrix
            elif (i == 3 and j == 3):
                continue
            # Set snake body and explosives to -10 in decision matrix
            elif matrix[row][col] == 2:
                res[i][j] = -10
            # Set food to 10 in decision matrix
            else:
                if matrix[row][col] == 1:
                    res[i][j] = 10
                dist = compute_distance((row, col), food_pos)
                if dist in open_paths:
                    open_paths[dist].append((i, j))
                else:
                    open_paths[dist] = [(i, j)]
    
    # Sort the points in open path in descending order of their distance from the food
    open_paths = dict(sorted(open_paths.items(), key=lambda item: item[0], reverse=True))
    
    # Create a gradient on the decision matrix to give a sense of direction to food
    for order, key in enumerate(open_paths):
        for points in open_paths[key]:
            res[points[0]][points[1]] += order + 1
        
    return res

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
        if matrix[curr[0]][curr[1]] == 1:
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
            
            # Skip moves where snake crashes into explosives or itself
            if matrix[next_y][next_x] == 2:
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
    SNAKE_SPEED = 30
    explosive_TIMER = 0
    SNAKE_COLOR = (255, 255, 255)
    SNAKE_HEAD_COLOR = (0, 0, 255)
    FOOD_COLOR = (255, 255, 255)
    explosive_COLOR = (255, 0, 0)
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)

    # Set up game clock
    clock = pygame.time.Clock()

    # Initialize Pygame
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))
    font = pygame.font.SysFont(None, 35)

    score = 1
    snake = Snake()
    food = Food()
    explosive = Explosive()

    i = 0  # Iterator
    
    while True:
        # End game when enough data has been collected
        if i == 30000:
            break
        
        # Zero all cells in matrix
        """
        Values in matrix
        0 - empty cell
        1 - food
        2 - dangerous cells (snake's body and explosives)
        """
        matrix = np.zeros((win_height//10, win_width//10))
        
        # Update cells of matrix
        matrix = update_matrix(matrix, snake.body, food.position, explosive.explosives)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        new_snake_direction = make_next_move(
            matrix=matrix, 
            head=snake.body[0],
            food=food.position,
        )

        if new_snake_direction:
            snake.direction = new_snake_direction
        else: # Reset game when no valid moves are found
            snake = Snake()
            food = Food()
            explosive = Explosive()
            continue
        
        # Collect new data points into pickle file after every three iterations
        if i % 3 == 0:
            with open(os.path.abspath(os.path.join(current_dir, 'static', 'train.pkl')), 'ab') as f:
                pickle.dump(get_decision_matrix(matrix, snake.body[0], food.position), f)
            with open(os.path.abspath(os.path.join(current_dir, 'static', 'label.pkl')), 'ab') as f:
                pickle.dump(labeler(direction=new_snake_direction), f)
        
        i += 1  # Increase iterator by 1

        # Move the snake
        snake.grow() 
        
        # Logic for eating food and spawning new one
        if snake.body[0] == food.position:
            score += 1
            food.spawn_new_food(matrix=matrix)
        # If no food eaten, remove last segment of snake
        else: 
            snake.shrink()
            
        # Update cells of matrix (effect change in food's position)
        matrix = update_matrix(matrix, snake.body, food.position, explosive.explosives)
        
        # Logic for spawning explosives
        explosive_TIMER += 1
        if explosive_TIMER % 20 == 0: 
            explosive.spawn_explosive(matrix=matrix)
            
        # Logic for timing out explosives
        if explosive_TIMER % 200 == 0:
            explosive.destroy_explosive(0)
            
        # Drawing snake, good food and explosives
        win.fill(BG_COLOR)
        for segment in snake.body[1:]:
            pygame.draw.rect(win, SNAKE_COLOR, pygame.Rect(segment[0], segment[1], snake.size, snake.size))
        pygame.draw.rect(win, SNAKE_HEAD_COLOR, pygame.Rect(snake.body[0][0], snake.body[0][1], snake.size, snake.size))
        pygame.draw.rect(win, FOOD_COLOR, pygame.Rect(food.position[0], food.position[1], food.size, food.size))
        if explosive.explosives:
            for explo in explosive.explosives:
                pygame.draw.rect(win, explosive_COLOR, pygame.Rect(explo[0], explo[1], explosive.size, explosive.size))
                
        # Display score
        score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
        win.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(SNAKE_SPEED)
    
    # Display final scores
    print(score)
    
    # Space of data
    print("Space of data:", i // 3)
    
    # End game
    pygame.quit()


# Command to run game
if __name__ == "__main__":
    game_loop()