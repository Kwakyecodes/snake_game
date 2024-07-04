import pygame
import numpy as np
from datetime import datetime

# Include top level modules
import os, sys
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from characters import (
    # Characters
    Snake, 
    Food, 
    Explosive,
    
    # Display variables
    win_height,
    win_width
)

steps = 0 # Track the number of steps taken by the snake

def update_matrix(curr_matrix, snakes, food, explosives):
    """Update the position of characters in matrix"""
    
    # Update snakes's body and explostions in matrix
    # Switch x and y because of numpy
    for pos in (snakes + explosives):
        x, y = pos[0]//10, pos[1]//10
        curr_matrix[y][x] = 2
    
    # Update food in matrix
    x, y = food[0]//10, food[1]//10
    curr_matrix[y][x] = 1  
    
    return curr_matrix

def update_record(score):
    """Log the stats of the most recent game"""
    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    record = f"\nhuman,{score},{steps},{steps//score},{current_time}"
    logger_file_path = os.path.abspath(os.path.join(current_dir, '..', 'logger.csv'))
    with open(logger_file_path, 'a') as f:
        f.write(record)
    return None

   
def game_loop():
    """Main game loop"""

    # Constants
    SNAKE_SPEED = 12
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

    running = True
    while running:
        # Create new matrix
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != "DOWN":
                    snake.direction = 'UP'
                elif event.key == pygame.K_DOWN and snake.direction != "UP":
                    snake.direction = 'DOWN'
                elif event.key == pygame.K_LEFT and snake.direction != "RIGHT":
                    snake.direction = 'LEFT'
                elif event.key == pygame.K_RIGHT and snake.direction != "LEFT":
                    snake.direction = 'RIGHT'
        
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
        
        # Logic for spawning and timing out explosives
        explosive_TIMER += 1
        if explosive_TIMER % 20 == 0: 
            explosive.spawn_explosive(matrix=matrix)
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