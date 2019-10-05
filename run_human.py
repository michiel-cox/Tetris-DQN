import gym
import pygame
import gym_tetris


def main():
    env = gym.make('tetris-v1')
    env.reset()

    running = True
    while running:
        action = 0

        env.render()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    action = 1
                elif event.key == pygame.K_RIGHT:
                    action = 2
                elif event.key == pygame.K_z:
                    action = 3
                elif event.key == pygame.K_x:
                    action = 4
                elif event.key == pygame.K_DOWN:
                    action = 5
                elif event.key == pygame.K_UP:
                    action = 6
                elif event.key == pygame.K_SPACE:
                    action = 7
                elif event.key == pygame.K_r:
                    env.reset()

        env.step(action)

    env.close()


if __name__ == '__main__':
    main()
