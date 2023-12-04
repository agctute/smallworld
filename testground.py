import numpy as np
import math

# foo = np.random.default_rng().normal(size=(int(1), int(1)))
#
# print(foo)
# # a dummy function that takes in two integers and a list of integers
# def dummy_func(a, b, c):
#     return a + b + sum(c)
#
# dummy_func(1, 1, [3, 4, 5])

def intersection_point(u0, v0, u1, v1):
    """Return the intersection point of two line segments and its distance from the starting point of the second segment

    Keyword arguments:
    u0 -- the starting point of the first line segment
    v0 -- the vector from u0 to the end of the first line segment
    u1 -- the starting point of the second line segment
    v1 -- the vector from u1 to the end of the second line segment
    """
    d = (v1[0]*v0[1] - v0[0]*v1[1])
    if d == 0:
        return None

    s = (1/d) * ((u0[0]-u1[0])*v0[1] - (u0[1]-u1[1])*v0[0])
    t = (1/d) * (-(-(u0[0]-u1[0])*v1[1] + (u0[1]-u1[1])*v1[0]))

    # print(s, t)
    if (s >= 0 and s <= 1 and t >= 0 and t <= 1): 
        return (u0[0] + t*v0[0], u0[1] + t*v0[1], math.sqrt((s*v1[0])**2 + (s*v1[1])**2))
    else:
        return None

print(intersection_point((200,200), (200,0), (250,300), (0,0-1000)))
