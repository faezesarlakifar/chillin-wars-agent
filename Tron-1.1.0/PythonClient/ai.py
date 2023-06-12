import random
import numpy as np
import copy

# chillin imports
from chillin_client import RealtimeAI

# project imports
from ks.models import ECell, EDirection, Position
from ks.commands import ChangeDirection, ActivateWallBreaker

# Constants
POPULATION_SIZE = 10
MAX_GENERATIONS = 80
MAX_DEPTH = 4
MUTATION_RATE = 0.1

class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)
        self.world = world

    def initialize(self):
        print('initialize')

    def decide(self):
        print('decide')
        self.client1()

    def client1(self):
        state = self.world  # Initial state
        my_team = self.my_side
        
        if(self.world.agents[my_team].direction == EDirection.Up):
            if self.world.agents[my_team].position.y + 1 >= len(state.board):
                self.change_direction()
            elif (not (state.board[self.world.agents[my_team].position.y+1][self.world.agents[my_team].position.x] == ECell.Empty)):
                self.change_direction()
        elif(self.world.agents[my_team].direction == EDirection.Down):
            if self.world.agents[my_team].position.y - 1 <= 0:
                self.change_direction()
            elif (not (state.board[self.world.agents[my_team].position.y-1][self.world.agents[my_team].position.x] == ECell.Empty)):
                self.change_direction()
        elif(self.world.agents[my_team].direction == EDirection.Right):
            if self.world.agents[my_team].position.x + 1 >= len(state.board[0]):
                self.change_direction()
            elif (not (state.board[self.world.agents[my_team].position.y][self.world.agents[my_team].position.x+1] == ECell.Empty)):
                self.change_direction()
        elif(self.world.agents[my_team].direction == EDirection.Left):
            if self.world.agents[my_team].position.x - 1 <= 0:
                self.change_direction()
            elif (not (state.board[self.world.agents[my_team].position.y][self.world.agents[my_team].position.x-1] == ECell.Empty)):
                self.change_direction()
                
    def change_direction(self):
        my_team = self.my_side
        state = self.world 
        best_direction = self.genetic_minimax(state, MAX_GENERATIONS, POPULATION_SIZE)
        if self.world.agents[my_team].wall_breaker_cooldown == 0:
            self.send_command(ActivateWallBreaker())
        print(best_direction)
        self.send_command(ChangeDirection(best_direction))
        

    def genetic_minimax(self, state, max_generations, population_size):
        population = self.initialize_population(population_size)
        max_ = float('-inf')
        best_action = population[0][0]
        for _ in range(max_generations):
            fitness_scores = []
            for individual in population:
                fitness_score = self.evaluate_individual(state, individual)
                fitness_scores.append(fitness_score)
                if fitness_score > max_:
                    max_ = fitness_score
                    best_action = individual[0]

            population = self.select_parents(population, fitness_scores, population_size)
            population = self.crossover(population, population_size)
            population = self.mutate(population)
    
        return best_action

    def initialize_population(self, population_size):
      population = []
      directions = list(EDirection)
      for _ in range(population_size):
          individual = [random.choice(directions)]
          for _ in range(MAX_DEPTH - 1):
              previous_direction = individual[-1]
              valid_directions = [direction for direction in directions if not self.is_opposite(previous_direction, direction)]
              individual.append(random.choice(valid_directions))
          population.append(individual)
      return population

    def mutate(self, population):
        for i in range(len(population)):
            for j in range(MAX_DEPTH):
                if random.random() < MUTATION_RATE:
                    previous_direction = population[i][j-1]
                    valid_directions = [direction for direction in list(EDirection) if not self.is_opposite(previous_direction, direction)]
                    population[i][j] = random.choice(valid_directions)
        return population

    def is_opposite(self, direction1, direction2):
        if (direction1 == EDirection.Up and direction2 == EDirection.Down) or \
                (direction1 == EDirection.Down and direction2 == EDirection.Up) or \
                (direction1 == EDirection.Left and direction2 == EDirection.Right) or \
                (direction1 == EDirection.Right and direction2 == EDirection.Left):
            return True
        return False

    def evaluate_individual(self, state, individual):
        total_score = 0
        current_state = copy.deepcopy(state)
        for direction in individual:
            next_state, flag = self.get_next_state(current_state, direction)
            total_score += self.evaluate_state(next_state, flag)
            current_state = next_state
        return total_score

    def select_parents(self, population, fitness_scores, population_size):
        sorted_population = [ind for _, ind in sorted(enumerate(population), key=lambda x: fitness_scores[x[0]])]
        selected_population = sorted_population[:population_size]
        return selected_population

    def crossover(self, population, population_size):
        new_population = []
        for _ in range(population_size):
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            crossover_point = random.randint(1, MAX_DEPTH - 1)
            child = parent1[:crossover_point] + parent2[crossover_point:]
            new_population.append(child)
        return new_population

    def _get_our_agent_position(self, state):
        return state.agents[self.my_side].position

    def _get_their_agent_position(self, state):
        return state.agents[self.other_side].position

    def evaluate_state(self, state, flag__):
        
        if(flag__):
            return float('-inf')
      
        max_cycles = self.world.constants.max_cycles
        wall_score_coefficient = self.world.constants.wall_score_coefficient
        my_wall_crash_score = self.world.constants.my_wall_crash_score
        enemy_wall_crash_score = self.world.constants.enemy_wall_crash_score

        my_agent = state.agents[self.my_side]
        
        # Check if the direction can not be done
        if my_agent.position.x <= 0:
            return float('-inf') 
         
        if my_agent.position.y <= 0:
            return float('-inf')     
        
        if my_agent.position.x >= len(state.board[0]):
            return float('-inf')
        
        if my_agent.position.y >= len(state.board):
            return float('-inf')
        
        if state.board[my_agent.position.y][my_agent.position.x] == ECell.AreaWall :
            my_agent.health = 0
            return float('-inf')
        
        opponent_agent = state.agents[self.other_side]

        my_score = state.scores[self.my_side]
        opponent_score = state.scores[self.other_side]
        
        current_cycle = self.current_cycle
        
        score_diff = my_score - opponent_score

        my_wall_penalty = 0
        enemy_wall_penalty = 0
        wall_coefficient_reward = 0

        # Compute the penalties for hitting walls
        if(self.my_side == 'Yellow'):
          if state.board[my_agent.position.y][my_agent.position.x] == ECell.YellowWall :
              my_wall_penalty = my_wall_crash_score
              if(my_agent.wall_breaker_rem_time < 1):
                my_agent.health -= 1
          elif state.board[my_agent.position.y][my_agent.position.x] == ECell.BlueWall :
              enemy_wall_penalty = enemy_wall_crash_score
              if(my_agent.wall_breaker_rem_time < 1):
                my_agent.health -= 1
        else:
          if state.board[my_agent.position.y][my_agent.position.x] == ECell.YellowWall :
              enemy_wall_penalty = enemy_wall_crash_score
              if(my_agent.wall_breaker_rem_time < 1):
                my_agent.health -= 1
          elif state.board[my_agent.position.y][my_agent.position.x] == ECell.BlueWall :
              my_wall_penalty = my_wall_crash_score
              if(my_agent.wall_breaker_rem_time < 1):
                my_agent.health -= 1

        if state.board[my_agent.position.y][my_agent.position.x] == ECell.Empty :
        # if my_agent.position in empty_neighbors:
            wall_coefficient_reward = wall_score_coefficient*10
        # Compute the score for the state
        state_score = score_diff + my_wall_penalty + enemy_wall_penalty + wall_coefficient_reward + my_agent.health

        # Check if the game is over
        if current_cycle >= max_cycles or my_agent.health <= 0 or opponent_agent.health <= 0 or ((my_agent.position.x == opponent_agent.position.x) and (my_agent.position.y == opponent_agent.position.y)) :
            # Return a higher value for a better state and a lower value for a worse state
            if my_score > opponent_score:
                return float('inf')
            elif my_score < opponent_score:
                return float('-inf')
            else:
                return 0

        # Evaluate the quality of the state based on the score difference

        return state_score

    def get_next_state(self, state, direction):
        
        next_state = copy.deepcopy(state)
        current_agent = copy.deepcopy(state.agents[self.my_side])
        
        #apply direction to the state and make virtual next state
        
        # update state board ----> applied on evaluate_state function
        
        flag_ = False
        # update state agents
        if (current_agent.direction == EDirection.Up):
            if(direction == EDirection.Down):
                flag_ = True
        elif (current_agent.direction == EDirection.Down):
            if(direction == EDirection.Up):
                flag_ = True
        if (current_agent.direction == EDirection.Right):
            if(direction == EDirection.Left):
                flag_ = True
        elif (current_agent.direction == EDirection.Left):
            if(direction == EDirection.Right):
                flag_ = True
                
        if(direction == EDirection.Up):
            current_agent.position.y -= 1
            current_agent.direction = EDirection.Up
        elif(direction == EDirection.Down):  
            current_agent.position.y += 1
            current_agent.direction = EDirection.Down
        elif(direction == EDirection.Right): 
            current_agent.position.x += 1
            current_agent.direction = EDirection.Right
        elif(direction == EDirection.Left):
            current_agent.position.x -= 1
            current_agent.direction = EDirection.Left
            
        next_state.agents[self.my_side] = current_agent
        
        # update state scores ----> applied on evaluate_state function
        
        return next_state, flag_
