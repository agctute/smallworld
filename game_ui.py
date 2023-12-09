import pygame
from arena import Arena
from agent import Agent

class GameUI:
    """The main graphics/ui controller of the simulator"""
    def __init__(self, arena:Arena, screen_width:int, screen_height:int) -> None:
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cam_x = 0
        self.cam_y = 0
        self.arena = arena
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.font = pygame.font.SysFont('Comic Sans MS', 30)

    def update_stats(self, generation: int =0, highest: int =0, current: int=0) -> None:
        """Update the stats display"""
        gen_stat_display = self.font.render(f"Generation {generation}", False, (0, 0, 0))
        self.screen.blit(gen_stat_display, (0, 0))

        high_stat_display = self.font.render(f"Highest: {highest}", False, (0, 0, 0))
        self.screen.blit(high_stat_display, (0, 40))

        cur_stat_display = self.font.render(f"Current: {current}", False, (0, 0, 0))
        self.screen.blit(cur_stat_display, (0, 80))

    def draw(self, screen):
        """Draw the arena and the goal."""
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, 
                         (0, 0, 0), 
                         (0-self.cam_x, 0-self.cam_y, self.arena.width, self.arena.height), 2)
        pygame.draw.rect(screen,
                         (144, 238, 144),
                         (self.arena.goal_x-self.cam_x, self.arena.goal_y-self.cam_y, self.arena.goal_width, self.arena.goal_height))

    def draw_agents(self, screen, agents: list[Agent]) -> None:
        """Draws all the agents in the arena."""
        for agent in agents:
            x, y = agent.get_position()
            pygame.draw.circle(screen, (255, 0, 0), (x - self.cam_x, y - self.cam_y), 5)
            # draws a short line indicating the agent's direction
            end_pos_x, end_pos_y = agent.end_of_velocity_line()
            pygame.draw.line(screen, (255, 0, 0), (x - self.cam_x, y - self.cam_y), (end_pos_x - self.cam_x, end_pos_y - self.cam_y), 1)

    def erase_old_agents(self, screen):
        screen.fill((0, 0, 0))
        self.draw(screen)

    def move_camera(self, x: int, y: int) -> None:
        """Move the camera by x and y."""
        self.cam_x += x
        self.cam_y += y

    def update(self) -> None:
        pygame.display.flip()

    def check_objects_in_bounds(self) -> None:
        """Return whether given object(s) are within view bounds"""
        



