import pygame
import numpy as np
import tensorflow as tf
from datetime import datetime
from tensorflow.keras import models, layers

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

steps = 0 # Track the number of steps taken by the snake

def update_matrix(matrix, snake, food):
    """Update the position of characters in matrix"""
    
    # Update snake on matrix
    matrix[snake[1]//10][snake[0]//10] = 11
    
    # Update food in matrix
    matrix[food[1]//10][food[0]//10] = 6 
    
    return matrix

def update_record(score):
    """Log the stats of the most recent game"""
    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    record = f"\ncnn_small,{score},{steps},{steps//score},{current_time}"
    logger_file_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'logger.csv'))
    with open(logger_file_path, 'a') as f:
        f.write(record)
    return None

def make_next_move(model, matrix):
    # Predicted move converter
    converter = {
        0: "UP",
        1: "RIGHT",
        2: "DOWN",
        3: "LEFT"
    }
    
    # Add extra dimension to matrix
    matrix = np.expand_dims(matrix, axis=(0, -1)) # resulting shape will be (1, 6, 8, 1)
    
    # Now you can use your model to make predictions
    predictions = model.predict(matrix)
    
    # The output is a batch of logits for each class, so let's take the first (and only) output
    output = predictions[0]
    
    # Convert logits to probabilities
    probabilities = tf.nn.softmax(output).numpy()

    # Get class with the highest probability as models class
    predicted_class = np.argmax(probabilities)
    return converter[predicted_class]
   
def game_loop():
    """Main game loop"""

    # Constants
    SNAKE_SPEED = 20
    SNAKE_COLOR = (255, 255, 255)
    FOOD_COLOR = (0, 0, 255)
    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    global steps

    # Set up game clock
    clock = pygame.time.Clock()

    # Initialize Pygame
    pygame.init()
    win = pygame.display.set_mode((win_width, win_height))

    score = 1
    snake = Snake()
    food = Food()
    
    # Recreate the exact same model architecture
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(6, 8, 1)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (2, 2), activation='relu'))  
    model.add(layers.Flatten())  # Flatten the feature map
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(4, activation='softmax'))

    # Load the weights
    model.load_weights(os.path.abspath(os.path.join(current_dir, 'static', 'weights.h5')))
    
    while True:
        # Create new matrix
        """
        Values in matrix
        0 - empty cell
        1 - food
        2 - dangerous cells (snake's body and explosives)
        """
        matrix = np.zeros((win_height//10, win_width//10))
        
        # Update cells of matrix
        matrix = update_matrix(matrix, snake.body[0], food.position)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        # Predict the next move with weights of cnn model
        snake.direction = make_next_move(model=model, matrix=matrix)

        # Move the snake
        steps += 1
        snake.grow() 
            
        # Logic for eating food and spawning new one
        if snake.body[0] == food.position:
            score += 1
            food.spawn_new_food(matrix=matrix)
            
        # Check if the snake has hit a wall
        if (snake.body[0][0] not in range(0, win_width) or
            snake.body[0][1] not in range(0, win_height)):
            update_record(score)
            break
            
        # Remove last segment whether food is eaten or not. 
        # to prevent the snake from growing
        snake.shrink()
            
        # Update cells of matrix (effect change in food's position)
        matrix = update_matrix(matrix, snake.body[0], food.position)
            
        # Drawing snake and food
        win.fill(BG_COLOR)
        pygame.draw.rect(win, SNAKE_COLOR, pygame.Rect(snake.body[0][0], snake.body[0][1], snake.size, snake.size))
        pygame.draw.rect(win, FOOD_COLOR, pygame.Rect(food.position[0], food.position[1], food.size, food.size))

        pygame.display.update()
        clock.tick(SNAKE_SPEED)
    
    # Display final scores
    print(f"SCORE: {score}")
    pygame.display.update()
    pygame.time.delay(5000) # Display final score for 5 seconds
    
    # End game
    pygame.quit()


# Command to run game
if __name__ == "__main__":
    game_loop()