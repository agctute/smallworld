import pygame
import numpy as np
import sys

from arena import Arena

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
STARTING_POP = 30

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
    arena = Arena(SCREEN_WIDTH, SCREEN_HEIGHT, 450, 50, 50, 50, rng=rng)
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

if __name__ == '__main__':
    main()

