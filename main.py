import pygame
import numpy as np
import sys

from arena import Arena
from game_ui import GameUI

SCREEN_WIDTH = 700 
SCREEN_HEIGHT = 700 
STARTING_POP = 30

rng = np.random.default_rng()

def main():
    ui = GameUI(Arena(1000, 1000, 450, 50, 50, 50, rng=rng), SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = ui.screen
    arena = ui.arena
    mode = False # True = automatic, False = manual
    steps = 0
    gen = 1
    highest = 0
    current = 0

    pygame.display.set_caption("Pygame Test")
    for _ in range(0, STARTING_POP):
        arena.add_agent()

    while True:
        if steps == 200:
            gen += 1
            ui.update_stats(generation=gen, highest=highest, current=current)
            # text_surface = my_font.render(f"Generation {gen}", False, (0, 0, 0))
            steps = 0
            arena.fitness()
            highest = max(len(arena.finished_agents), highest)
            ui.update_stats(generation=gen, highest=highest, current=current)
            # highest_text = my_font.render(f"Highest: {highest}", False, (0, 0, 0))
            arena.select()
            arena.reset(random=True)
            ui.erase_old_agents(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    mode = not mode
                if (not mode and event.key == pygame.K_SPACE):
                    if steps % 100 == 0:
                        arena.change_goal(rng.integers(0, screen.get_width()-100), rng.integers(0, screen.get_height()-100), rng.integers(10, 100), rng.integers(10, 100)) 
                        ui.draw(screen)
                    arena.agents[0].check_distance(arena.agents[0].direction)
                    arena.update_agents()
                    steps += 1

                # moving top down camera
                if event.key == pygame.K_LEFT:
                    ui.move_camera(-20, 0)
                if event.key == pygame.K_RIGHT:
                    ui.move_camera(20, 0)
                if event.key == pygame.K_UP:
                    ui.move_camera(0, -20)
                if event.key == pygame.K_DOWN:
                    ui.move_camera(0, 20)


        if mode:
            if steps % 100 == 0:
                arena.change_goal(rng.integers(0, SCREEN_WIDTH-100), rng.integers(0, SCREEN_HEIGHT-100), rng.integers(10, 100), rng.integers(10, 100)) 
                ui.draw(screen)
            arena.update_agents()
            steps += 1

        screen.fill((0, 0, 0))
        ui.draw(screen)
        ui.draw_agents(screen, arena.agents)
        current = len(arena.finished_agents)
        ui.update_stats(generation=gen, highest=highest, current=current)
        pygame.display.flip()
        pygame.time.Clock().tick(40)

if __name__ == '__main__':
    main()

