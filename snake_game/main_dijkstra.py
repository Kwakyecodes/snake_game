import pygame
import math
import numpy as np
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

def calc_cost(A, B):
    """Takes two points A and B and calculates cost of getting from A to B"""
    cost = abs(A[1] - B[1]) + abs(A[0] - B[0])
    return cost

def make_next_move(matrix, head, length_of_snake, food, curr_direction):
    """Select next move of snake"""
    
    h, w = len(matrix), len(matrix[0])
    directions = [ 
        {"name": "LEFT", "value": (0, -1), "opposite": "RIGHT"},
        {"name": "UP", "value": (-1, 0), "opposite": "DOWN"},
        {"name": "RIGHT", "value": (0, 1), "opposite": "LEFT"},
        {"name": "DOWN", "value": (1, 0), "opposite": "UP"}, 
        # Opposite key value pair of directions ensures that
        # Assistant does not move into its body
    ]
    head = (head[1]//10, head[0]//10) # Scale position of head and reverse for numpy
    food = (food[1]//10, food[0]//10) # Scale position of food and reverse for numpy
    n = 1 # number of items in heap
    heap = [
        {"path": [head], "direction": curr_direction}
    ]
    move = None
    while heap:
        # Sort heap in descending order based on proximity to food
        heap.sort(key=lambda x: calc_cost(x["path"][-1], food), reverse=True)
    
        path_obj = heap.pop()
        n -= 1 # Reduce size of heap since the last item has been popped
        curr = path_obj["path"][-1]
        curr_direction = path_obj["direction"]
        
        # Stop searching and make move when food is found OR
        # When snake is overthinking (heap length becomes too big)
        if matrix[curr[0]][curr[1]] == 1 or (n > 0 and math.log10(n)) >= 3.5:
            move = path_obj["path"][1] # Set move to next step from head   
            break
        
        # Find next possible moves
        for d in directions:
            
            # Prevent snake from going the opposite direction
            if d["opposite"] == curr_direction:
                continue
            
            y, x = d["value"]
            next_y, next_x = curr[0] + y, curr[1] + x
            nextt = (next_y, next_x)
            
            # Check if path has already been visited. This is important because each time this
            # function is called, every path from head to the food is determine; visiting an already
            # visited path means snake crashes into itself. Ideally, the matrix could be changed to
            # reflect this change in the snake's (temporary) position but that's too much work and I'm lazy boi :o
            if nextt in path_obj["path"]:
                continue
            
            # Skip moves where snake crashes into wall
            if (next_y not in range(0, h)) or (next_x not in range(0, w)):
                continue
            
            # Skip moves where snake crashes into explosives or itself
            if matrix[next_y][next_x] == 2:
                continue
            
            new_heap_obj = {
                "path": path_obj["path"] + [nextt],
                "direction": d["name"]
                } 
            heap.append(new_heap_obj)
            n += 1 # Increase size of head each time an item is added
           
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
        matrix = update_matrix(matrix, snake.body, food.position, explosive.explosives)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        new_snake_direction = make_next_move(
            matrix=matrix, 
            head=snake.body[0], 
            length_of_snake=len(snake.body),
            food=food.position, 
            curr_direction=snake.direction
        )
        if new_snake_direction:
            snake.direction = new_snake_direction
        else: # End game because no valid move was found
            break

        # Move the snake
        snake.grow() 
        
        # Check if snake bit itself or has hit wall and end game if it has
        if (snake.body[0] in snake.body[1:] or
            snake.body[0][0] not in range(0, win_width) or
            snake.body[0][1] not in range(0, win_height)):
            break
            
        # Logic for eating food and spawning new one
        if snake.body[0] == food.position:
            score += 1
            food.spawn_new_food(matrix=matrix)
            
        # If no food eaten, remove last segment of snake
        else: 
            snake.shrink()
            
        # Update cells of matrix (effect change in food's position)
        matrix = update_matrix(matrix, snake.body, food.position, explosive.explosives)
            
        # Logic for running into bombs  
        if snake.body:
            if snake.body[0] in explosive.explosives:
                for i, explo in enumerate(explosive.explosives):
                    if explo == snake.body[0]:
                        score -= 1
                        explosive.destroy_explosive(i)
                        snake.shrink()
            
        # Check if snake is dead and end game if so
        if len(snake.body) == 0:
            break
        
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
    