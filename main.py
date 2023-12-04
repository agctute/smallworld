import pygame
import cmath
import math
import numpy as np
import sys

from brain import Brain

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
STARTING_POP = 30
SURVIVORS = 8
NEWBIES = 2
CHILDREN = 20
MUTATION_RATE = 0.1
BRAIN_ARCHITECTURE = [10, 10, 3]

rng = np.random.default_rng()

def main():
    mode = False # True = automatic, False = manual
    steps = 0
    gen = 1
    highest = 0
    current = 0

    pygame.init()
    my_font = pygame.font.SysFont('Comic Sans MS', 30)
    text_surface = my_font.render(f"Generation {gen}", False, (0, 0, 0))
    highest_text = my_font.render(f"Highest: {highest}", False, (0, 0, 0))
    current_text = my_font.render(f"Current: {current}", False, (0, 0, 0))

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    arena = Arena(SCREEN_WIDTH, SCREEN_HEIGHT, 450, 50, 50, 50)
    pygame.display.set_caption("Pygame Test")
    for _ in range(0, STARTING_POP):
        arena.add_agent()

    pygame.display.flip()
    while True:
        if steps == 200:
            gen += 1
            text_surface = my_font.render(f"Generation {gen}", False, (0, 0, 0))
            steps = 0
            arena.fitness()
            highest = max(len(arena.finished_agents), highest)
            highest_text = my_font.render(f"Highest: {highest}", False, (0, 0, 0))
            arena.select()
            arena.reset(random=True)
            arena.erase_old_agents(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    mode = not mode
                if (not mode and event.key == pygame.K_SPACE):
                    if steps % 100 == 0:
                        arena.change_goal(rng.integers(0, SCREEN_WIDTH-100), rng.integers(0, SCREEN_HEIGHT-100), rng.integers(10, 100), rng.integers(10, 100)) 
                        arena.draw(screen)
                    arena.agents[0].check_distance(arena.agents[0].direction)
                    arena.update_agents()
                    steps += 1

        if mode:
            if steps % 100 == 0:
                arena.change_goal(rng.integers(0, SCREEN_WIDTH-100), rng.integers(0, SCREEN_HEIGHT-100), rng.integers(10, 100), rng.integers(10, 100)) 
                arena.draw(screen)
            arena.update_agents()
            steps += 1

        screen.fill((0, 0, 0))
        arena.draw(screen)
        arena.draw_agents(screen)
        screen.blit(text_surface, (0, 0))
        screen.blit(highest_text, (0, 40))
        current = len(arena.finished_agents)
        current_text = my_font.render(f"Current: {current}", False, (0, 0, 0))
        screen.blit(current_text, (0, 80))
        pygame.display.flip()
        pygame.time.Clock().tick(40)

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
    def __init__(self, width, height, goal_x, goal_y, goal_width, goal_height):
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
            agent.update_position()

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
            parent_1 = rng.choice(self.agents, p=probabilities).copy()
            parent_2 = rng.choice(self.agents, p=probabilities).copy()
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
            x = rng.integers(200, self.width-200)
            y = rng.integers(400, self.height-200)
            direction = rng.integers(0,359)
        else:
            x = self.start_x
            y = self.start_y
            direction = 0

        for agent in self.agents:
            agent.x = x
            agent.y = y
            agent.direction = direction


# Agent composed of single layer nn
# has a position and velocity
# has a set of weights
class Agent:
    """A agent that moves around in the arena.

    Attributes:
        arena: The arena the agent is in.
        x: The x coordinate of the agent.
        y: The y coordinate of the agent.
        speed: The speed of the agent.
        direction: The direction the agent is facing.
        brain: the neural net object that computes what the agent should do
    """
    def __init__(self, arena:Arena, x:float, y:float, speed=10, direction=270, brain=None):
        self.arena = arena
        self.x = x
        self.y = y
        self.speed = speed
        # 0-360 based on degrees
        self.direction = direction
        if brain == None:
            self.brain = Brain(layers=BRAIN_ARCHITECTURE)
        else:
            self.brain = brain

        self.fitness = 0

    # returns three points that represent the agent's vision
    # one is the distance from the agent to the wall or goal in front
    # two is the distance 45 degrees to the right
    # three is the distance 45 degress to the left
    def check_surroundings(self) -> list[float]:
        """Check the surroundings of the agent."""
        res = []
        # front = self.check_distance(self.direction)
        # right = self.check_distance(self.direction + 45)
        # left = self.check_distance(self.direction - 45)
        #
        # res.append(front[1])
        # res.append(right[1])
        # res.append(left[1])
        for i in range(11):
            res.append(self.check_distance(self.direction + i * 10 - 50)[1])

        print(res)
        return res 
    
    def check_distance(self, direction:int):
        """Check the distance between the agent and the wall or goal in the specified direction."""

        # transform direction s.t. it is between 0 and 360
        direction = (direction % 360)
        if direction < 0:
            direction += 360

        goal_distance = self.check_goal_collision(direction)
        if goal_distance:
            return goal_distance, 1;

        # cardinal direction cases
        if direction == 0:
            return self.arena.width - self.x, 0
        if direction == 90:
            return self.y, 0
        if direction == 180:
            return self.x, 0
        if direction == 270:
            return self.arena.height - self.y, 0

        # adjust trig calculations based on quadrant
        quadrant = direction // 90
        adj_a = 0
        adj_b = 0
        if quadrant == 0:
            adj_a = self.arena.width - self.x
            adj_b = self.arena.height - self.y
        elif quadrant == 1:
            adj_a = self.arena.height - self.y
            adj_b = self.x
        elif quadrant == 2:
            adj_a = self.y
            adj_b = self.y
        elif quadrant == 3:
            adj_a = self.y
            adj_b = self.arena.width - self.x

        
        direction = int(direction % 90)
        a = 1 / cmath.cos(math.radians(direction)).real * adj_a
        b = 1 / cmath.cos(math.radians(90 - direction)).real * adj_b
        opp_a = cmath.tan(math.radians(direction)).real * adj_a
        opp_b = cmath.tan(math.radians(90 - direction)).real * adj_b

        # print(f"Status report: adj_a = {adj_a}, adj_b = {adj_b}, opp_a = {opp_a}, opp_b = {opp_b}, a = {a}, b = {b}")
        # print(f"cmath.acos(math.radians(direction)).real = {cmath.cos(math.radians(direction)).real}")
        # print(f"cmath.acos(math.radians(90 - direction)).real = {cmath.cos(math.radians(90 - direction)).real}")
        # print(f"direction = {direction}, quadrant = {quadrant}")
        if adj_b > opp_a:
            return a, 0
        elif adj_a > opp_b:
            return b, 0
        else:
            raise Exception("Something went wrong in check_distance")

    def intersection_point(self, u0, v0, u1, v1):
        """Return the intersection point of two line segments and its distance from the starting point of the second segment

        Keyword arguments:
        u0 -- the starting point of the first line segment
        v0 -- the vector from u0 to the end of the first line segment
        u1 -- the starting point of the second line segment
        v1 -- the vector from u1 to the end of the second line segment
        """

        # print(f"u0 = {u0}, v0 = {v0}, u1 = {u1}, v1 = {v1}")
        d = (v1[0]*v0[1] - v0[0]*v1[1])
        if d == 0:
            return None

        s = (1/d) * ((u0[0]-u1[0])*v0[1] - (u0[1]-u1[1])*v0[0])
        t = (1/d) * (-(-(u0[0]-u1[0])*v1[1] + (u0[1]-u1[1])*v1[0]))

        if (s >= 0 and s <= 1 and t >= 0 and t <= 1): 
            return (u0[0] + t*v0[0], u0[1] + t*v0[1], math.sqrt((s*v1[0])**2 + (s*v1[1])**2))
        else:
            return None

    def convert_to_line(self, direction):
        """ Return the starting coordinates and vector of a line segment from the starting point to the end of the line segment"""
        x1 = 1000 * cmath.cos(math.radians(direction)).real 
        y1 = 1000 * cmath.sin(math.radians(direction)).real
        # print(direction, cmath.cos(math.radians(direction)).real, cmath.sin(math.radians(direction)).real)
        return (x1,y1)

    def check_goal_collision(self,direction):
        """Return distance between agent and goal (if goal is in the given direction)"""
        line = self.convert_to_line(direction)
        x00 = self.arena.goal_x
        y00 = self.arena.goal_y
        x01 = self.arena.goal_width
        y01 = self.arena.goal_height
        box = []
        top = self.intersection_point((x00, y00), (x01, 0), (self.x,self.y),line )
        if top:
            box.append(top[2])
        left = self.intersection_point((x00, y00), (0, y01), (self.x,self.y), line)
        if left:
            box.append(left[2])
        right = self.intersection_point((x00 + self.arena.goal_width, y00), (0, y01), (self.x,self.y), line)
        if right:
            box.append(right[2])
        bottom = self.intersection_point((x00, y00 + self.arena.goal_height), (x01, 0), (self.x,self.y), line)
        if bottom:
            box.append(bottom[2])

        # print(top, left, right, bottom)
        return min(box) if box else None

    def update_position(self):
        decision = self.brain.feedforward(self.check_surroundings()) 
        self.x = self.x + self.speed * math.cos(math.radians(self.direction))
        self.y = self.y + self.speed * math.sin(math.radians(self.direction))
        choice = rng.choice([0, 1, 2], p=decision)
        if choice == 0:
            self.direction = self.direction - 15
        elif choice == 1:
            self.direction = self.direction
        elif choice == 2:
            self.direction = self.direction + 15

        # print(choice)
        print(decision)

    def get_position(self):
        return (self.x, self.y)

    def get_direction(self):
        return self.direction

    # converts the agents position, speed, and direction into a new position
    # representing the end point of a line representing the agent's directions and speed
    def end_of_velocity_line(self):
        return ([sum(x) for x in zip(self.get_position(), polar_to_cartesian(25, self.direction))])

    def copy(self):
        return Agent(self.arena, self.x, self.y, self.speed, self.direction, brain=self.brain.copy())

    def mutate(self):
        self.brain = self.brain.mutate(MUTATION_RATE)

    def crossover(self, other):
        offspring = self.brain.crossover(other.brain)
        new_agent = Agent(self.arena, self.x, self.y, self.speed, self.direction, brain=offspring)
        # print(new_agent.brain)
        return new_agent

def polar_to_cartesian(r, theta):
    """
    Convert polar coordinates (r, theta) to cartesian coordinates (x, y).
    r: magnitude
    theta: angle in degrees
    """

    x = r * cmath.cos(theta * cmath.pi / 180)
    y = r * cmath.sin(theta * cmath.pi / 180)
    return (x.real, y.real)

if __name__ == '__main__':
    main()

