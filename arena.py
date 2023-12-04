import pygame
import math
import numpy as np

from agent import Agent

# hyperparameters controlling some evolutionary alg stuff
SURVIVORS = 8
NEWBIES = 2
CHILDREN = 20

class Arena:
    """Arena class that contains all the agents and the goal

    Attributes:
        width: width of the arena
        height: height of the arena
        goal_x: x coordinate of the goal (relative to window)
        goal_y: y coordinate of the goal (relative to window)
        goal_width: width of the goal
        goal_height: height of the goal
        agents: list of agents in the arena
        finished_agents: list of agents that have reached the goal
    """
    def __init__(self, width, height, goal_x, goal_y, goal_width, goal_height, rng):
        self.width = width
        self.height = height
        self.goal_x = goal_x
        self.goal_y = goal_y
        self.goal_width = goal_width
        self.goal_height = goal_height
        self.agents = []
        self.finished_agents = []
        self.start_x = 475
        self.start_y = 475
        self.rng = rng # global random numpy generator

    # draws arena and goal
    def draw(self, screen):
        """Draws the arena and the goal."""
        pygame.draw.rect(screen, 
                         (255, 255, 255), 
                         (0, 0, self.width, self.height))
        pygame.draw.rect(screen,
                         (144, 238, 144),
                         (self.goal_x, self.goal_y, self.goal_width, self.goal_height))

    def change_goal(self, goal_x, goal_y, goal_width, goal_height):
        """Changes the goal."""
        self.goal_x = goal_x
        self.goal_y = goal_y
        self.goal_width = goal_width
        self.goal_height = goal_height

    def erase_old_agents(self, screen):
        screen.fill((0, 0, 0))
        self.draw(screen)

    def add_agent(self, agent=None):
        """Adds an agent to the arena."""
        if agent == None:
            agent = Agent(self, self.start_x, self.start_y)
        # print(f"Adding agent with brain: {agent.brain}")
        self.agents.append(agent)


    def draw_agents(self, screen):
        """Draws all the agents in the arena."""
        for agent in self.agents:
            pygame.draw.circle(screen, (255, 0, 0), (agent.get_position()), 5)
            # draws a short line indicating the agent's direction
            pygame.draw.line(screen, (255, 0, 0), (agent.get_position()), agent.end_of_velocity_line(), 1)

    def update_agents(self):
        """Updates the position of all the agents in the arena."""
        for agent in self.agents:
            self.check_goal()
            self.check_death()
            agent.update_position(rng=self.rng)

    def check_death(self):
        """Checks if any agents have died."""
        for agent in self.agents:
            if agent.x < 0 or agent.x > self.width or agent.y < 0 or agent.y > self.height:
                self.agents.remove(agent) 
    
    def check_goal(self):
        """Check if an agent has reached the goal and remove from the arena if so."""

        for agent in self.agents:
            if agent.x > self.goal_x and agent.x < self.goal_x + self.goal_width:
                if agent.y > self.goal_y and agent.y < self.goal_y + self.goal_height:
                    self.agents.remove(agent)
                    self.finished_agents.append(agent)

    def distance_to_goal(self, agent):
        """Calculates the distance between an agent and the goal."""
        return math.sqrt((agent.x - self.goal_x) ** 2 + (agent.y - self.goal_y) ** 2)

    def fitness(self):
        """Calculates the fitness of each agent."""
        for agent in self.agents:
            agent.fitness = 1 / (1 + self.distance_to_goal(agent) ** 2)
        for agent in self.finished_agents:
            agent.fitness = 1

    def mutate(self):
        for agent in self.agents:
            agent.mutate()
        for agent in self.finished_agents:
            agent.mutate()

    def select(self, survivor_count=SURVIVORS, new_boys=NEWBIES, children=CHILDREN):
        """Performs the selection process for the agent."""
        # get top 10
        if len(self.finished_agents) >= survivor_count:
            self.agents = self.finished_agents[:survivor_count]
        else:
            i = len(self.finished_agents)
            self.agents.sort(key=lambda x: x.fitness, reverse=True)
            self.agents = self.agents[:survivor_count-i]
            for agent in self.finished_agents:
                self.agents.append(agent)

        self.finished_agents = []
        probabilities = np.asarray([a.fitness for a in self.agents])
        # print(probabilities)
        probabilities = probabilities / probabilities.sum()
        # print(probabilities)
        # generate new agents through mutation
        children_list = []
        for _ in range(children):
            parent_1 = self.rng.choice(self.agents, p=probabilities).copy()
            parent_2 = self.rng.choice(self.agents, p=probabilities).copy()
            new_agent = parent_1.crossover(parent_2)
            # print(f"parent1's brain: {parent_1.brain}, parent2's brain: {parent_2.brain}, new agent's brain: {new_agent.brain}")
            new_agent.mutate()
            children_list.append(new_agent)
            # print("does it come here")

        for i in range(new_boys + survivor_count - len(self.agents)):
            self.add_agent()

        for agent in children_list:
            self.add_agent(agent)


    def reset(self, random=False):
        """Resets the arena."""
        if random:
            x = self.rng.integers(200, self.width-200)
            y = self.rng.integers(400, self.height-200)
            direction = self.rng.integers(0,359)
        else:
            x = self.start_x
            y = self.start_y
            direction = 0

        for agent in self.agents:
            agent.x = x
            agent.y = y
            agent.direction = direction


