# Snake Game Project

This project contains multiple implementations of the classic Snake game, along with some advanced features like an automated player using the BFS algorithm and a machine learning training setup with different configurations.

## Table of Contents

- [Introduction](#introduction)
- [User-Controlled Snake Game](#user-controlled-snake-game)
- [Automated Snake Game Using BFS](#automated-snake-game-using-bfs)
- [Machine Learning Training Setup](#machine-learning-training-setup)
- [Observations and Findings](#observations-and-findings)
- [Installation and Usage](#installation-and-usage)

## Introduction

The Snake Game Project is an exploration into various approaches to automate and enhance the classic snake game. The project includes:
1. A user-controlled version of the game.
2. An automated version using the Breadth-First Search (BFS) algorithm.
3. Machine learning models trained to play the game using Convolutional Neural Networks (CNNs).

## User-Controlled Snake Game

In this version, the player controls the snake using the arrow keys. The objective is to navigate the snake to eat food while avoiding the walls and explosives that spawn randomly on the screen. Each time the snake eats food, it grows longer. The game ends if the snake runs into the wall, its own body, or an explosive.

## Automated Snake Game Using BFS

This version automates the snake's movement using the BFS algorithm. The algorithm finds the shortest path to the food while avoiding obstacles. The game setup and rules are the same as the user-controlled version, but the snake's movements are determined by the BFS pathfinding algorithm.

## Machine Learning Training Setup

### CNN Small

In this simplified version, the snake only needs to find the food, without growing and there are no explosives. The input to the model is a 6x8 matrix representing the game screen, where:
- The snake is represented by 11.
- The food is represented by 6.
- Empty cells are 0.

### CNN

This version uses a 7x7 matrix around the snake's head to train the model. The idea is that the snake doesn't need to see the entire screen but should have a sense of direction towards the food. The input matrix includes:
- The snake's head, which is represented by 0.
- The snake's body and the walls, which are represented by negative values.
- Food with a higher positive value.
- Paths graded based on proximity to the food.

### CNN 2x

Similar to the CNN version, but with double the amount of training data to improve the model's performance.

### CNN 5by5

This version reduces the input matrix to 5x5 around the snake's head. The smaller matrix focuses on a more localized view, potentially sacrificing some context for better immediate decision-making.

## Observations and Findings

The following data was collected during the experiments:

| Model       | Score | Steps | Steps per Score | Timestamp              |
|-------------|-------|-------|-----------------|------------------------|
| bfs         | 122   | 5706  | 46              | 21-06-2024 23:13:06    |
| human       | 6     | 383   | 63              | 21-06-2024 23:16:04    |
| human       | 16    | 1097  | 68              | 21-06-2024 23:27:37    |
| bfs         | 150   | 7858  | 52              | 21-06-2024 23:32:32    |
| cnn_small   | 249   | 1237  | 4               | 25-06-2024 14:54:19    |
| cnn         | 26    | 1315  | 50              | 27-06-2024 04:07:06    |
| cnn         | 28    | 1414  | 50              | 27-06-2024 04:08:34    |
| cnn_2x      | 41    | 2057  | 50              | 27-06-2024 09:52:37    |
| cnn_5by5    | 65    | 3463  | 53              | 04-07-2024 05:16:46    |

- **BFS Algorithm**: Performed well in navigating the snake to the food while avoiding obstacles.
- **Human-Controlled**: Varied performance, but generally less efficient than the automated approaches.
- **CNN Small**: Achieved high scores in the simplified environment (without growth or explosives).
- **CNN**: Using a 7x7 matrix provided a decent performance but struggled with larger context.
- **CNN 2x**: Doubling the training data improved performance slightly.
- **CNN 5by5**: Performed much better than CNN and CNN 2x, but struggled more with larger context.

## Installation and Usage

1. **Clone the Repository**:
    ```sh
    git clone <repository-url>
    cd snake_game
    ```

2. **Set Up the Virtual Environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the Required Packages**:
    ```sh
    pip install pygame numpy tensorflow
    ```

4. **Run the User-Controlled Snake Game**:
    ```sh
    python3 -m human_player.main
    ```

5. **Run the Automated Snake Game Using BFS**:
    ```sh
    python3 -m bfs_player.main
    ```

6. **Run the CNN Training Setup**:
    ```sh
    python3 -m cnn_players.big_snake.main
    ```

Feel free to explore the different scripts and experiment with the configurations to see how the snake performs under various settings.