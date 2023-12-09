import cmath
import math

from brain import Brain

BRAIN_ARCHITECTURE = [10, 10, 3]
MUTATION_RATE = 0.1

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
    def __init__(self, arena, x:float, y:float, speed=10, direction=270, brain=None):
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

    def update_position(self, rng):
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
        return self.x, self.y

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

