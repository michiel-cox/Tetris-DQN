import random
import time
import gym
import gym_tetris


def main():
    env = gym.make('tetris-v1', action_mode=1)
    env.reset()

    start_time = time.time()
    log_every = 5
    counter_fps = 0
    counter_games = 0
    log_until_quit = 5
    while log_until_quit > 0:
        x = random.randrange(10)
        rotation = random.randrange(4)
        obs, reward, done, info = env.step((x, rotation))
        counter_fps += 1

        if done:
            counter_games += 1
            env.reset()

        if (time.time() - start_time) > log_every:
            print("Frames per second: ", counter_fps / (time.time() - start_time))
            print("Games per second: ", counter_games / (time.time() - start_time))
            start_time = time.time()
            counter_games = 0
            counter_fps = 0
            log_until_quit -= 1


if __name__ == '__main__':
    main()
