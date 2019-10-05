import gym
import gym_tetris

from statistics import mean, median
from gym_tetris.ai.QNetwork import QNetwork


def main():
    env = gym.make("tetris-v1", action_mode=1)
    network = QNetwork()
    network.load()

    running = True
    total_games = 0
    total_steps = 0
    while running:
        steps, rewards, scores = network.train(env, episodes=25)
        total_games += len(scores)
        total_steps += steps
        network.save()
        print("==================")
        print("* Total Games: ", total_games)
        print("* Total Steps: ", total_steps)
        print("* Epsilon: ", network.epsilon)
        print("*")
        print("* Average: ", sum(rewards) / len(rewards), "/", sum(scores) / len(scores))
        print("* Median: ", median(rewards), "/", median(scores))
        print("* Mean: ", mean(rewards), "/", mean(scores))
        print("* Min: ", min(rewards), "/", min(scores))
        print("* Max: ", max(rewards), "/", max(scores))
        print("==================")

    env.close()


if __name__ == '__main__':
    main()
