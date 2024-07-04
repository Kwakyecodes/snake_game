import pygame
import numpy as np
import tensorflow as tf
from tensorflow.keras import models, layers
from datetime import datetime

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

steps = 0 # Track the number of steps taken by the snake


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

def make_next_move(model, matrix):
    # Predicted move converter
    converter = {
        0: "UP",
        1: "RIGHT",
        2: "DOWN",
        3: "LEFT"
    }
    
    # Add extra dimension to matrix
    matrix = np.expand_dims(matrix, axis=(0, -1)) # resulting shape will be (1, 7, 7, 1)
    
    # Now you can use your model to make predictions
    predictions = model.predict(matrix)
    
    # The output is a batch of logits for each class, so let's take the first (and only) output
    output = predictions[0]
    
    # Convert logits to probabilities
    probabilities = tf.nn.softmax(output).numpy()

    # Get class with the highest probability as models class
    predicted_class = np.argmax(probabilities)
    return converter[predicted_class]


def update_record(score):
    """Log the stats of the most recent game"""
    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    record = f"\ncnn_5by5,{score},{steps},{steps//score},{current_time}"
    logger_file_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'logger.csv'))
    with open(logger_file_path, 'a') as f:
        f.write(record)
    return None


def game_loop():
    """Main game loop"""

    # Constants
    SNAKE_SPEED = 30
    explosive_TIMER = 0
    SNAKE_COLOR = (255, 255, 255)
    FOOD_COLOR = (255, 255, 255)
    explosive_COLOR = (255, 0, 0)
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    global steps

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
    
    # Recreate the exact same model architecture
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(5, 5, 1)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (1, 1), activation='relu'))  
    model.add(layers.Flatten())  # Flatten the feature map
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(4, activation='softmax'))
    
    # Load the weights
    model.load_weights(os.path.abspath(os.path.join(current_dir, 'static', 'weights.h5')))
    
    while True:
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
                
        # Predict the next move with weights of cnn model
        snake.direction = make_next_move(model=model, matrix=get_decision_matrix(matrix, snake.body[0], food.position))
        
        # Move the snake
        steps += 1
        snake.grow()
            
        # Logic for eating food and spawning new one
        if snake.body[0] == food.position:
            score += 1
            food.spawn_new_food(matrix=matrix)
        # If no food eaten, remove last segment of snake
        else: 
            snake.shrink()
            
        # Check if snake bit itself or has hit wall and end game if it has
        if (snake.body[0] in snake.body[1:] or
            snake.body[0][0] not in range(0, win_width) or
            snake.body[0][1] not in range(0, win_height)):
            update_record(score)
            break
        
        # Logic for running into bombs  
        if snake.body:
            if snake.body[0] in explosive.explosives:
                update_record(score)
                break
        
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
        for segment in snake.body:
            pygame.draw.rect(win, SNAKE_COLOR, pygame.Rect(segment[0], segment[1], snake.size, snake.size))
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
    font = pygame.font.SysFont(None, 60)
    game_over_text_1 = font.render(f"Game Over", True, TEXT_COLOR)
    game_over_text_2 = font.render(f"Final score: {score}", True, TEXT_COLOR)
    win.blit(game_over_text_1, (270, 220))
    win.blit(game_over_text_2, (250, 270))
    pygame.display.update()
    pygame.time.delay(5000) # Display final score for 5 seconds
    
    # End game
    pygame.quit()


# Command to run game
if __name__ == "__main__":
    game_loop()