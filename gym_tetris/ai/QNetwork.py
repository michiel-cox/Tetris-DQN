from __future__ import division
from pathlib import Path

import os
import random
import numpy as np
import tensorflow as tf

WEIGHT_PATH = os.path.join(os.path.dirname(__file__), 'weights.h5')
IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'model.png')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')


class ExperienceBuffer:
    def __init__(self, buffer_size=20000):
        self.buffer = []
        self.buffer_size = buffer_size

    def add(self, experience):
        if len(self.buffer) + len(experience) >= self.buffer_size:
            self.buffer[0:(len(experience) + len(self.buffer)) - self.buffer_size] = []
        self.buffer.extend(experience)

    def sample(self, size):
        return random.sample(self.buffer, size)


class QNetwork:
    def __init__(self, state_size=9, discount=1, epsilon=1, epsilon_min=0.0001, epsilon_decay=9.9995):
        self.state_size = state_size
        self.model = self._create_model()
        self.discount = discount
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.experiences = ExperienceBuffer()
        self.tensorboard = tf.keras.callbacks.TensorBoard(log_dir=LOG_DIR,
                                                          histogram_freq=1000,
                                                          write_graph=True,
                                                          write_images=True)

    def _create_model(self):
        """Returns a new model."""

        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(64, input_dim=self.state_size, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear'),
        ])

        # For the loss function Mean Square Error is used as the problem
        # we are trying to solve is a regression problem
        # rather than a classification problem.
        model.compile(optimizer='adam',
                      loss='mse',
                      metrics=['mean_squared_error'])

        model.summary()

        tf.keras.utils.plot_model(model, IMAGE_PATH, show_shapes=True)

        return model

    def act(self, possible_states):
        """Returns the best of multiple states unless it has decided to explore which returns a random one."""

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_states)

        max_rating = None
        best_state = None
        ratings = self._predict_ratings([state for action, state in possible_states])

        for i, (action, state) in enumerate(possible_states):
            rating = ratings[i]
            if not max_rating or rating > max_rating:
                max_rating = rating
                best_state = (action, state)

        return best_state

    def _predict_ratings(self, states):
        """Returns the outputs of the Neural Network for multiple states."""
        input_y = np.array(states)
        predictions = self.model.predict(input_y)
        return [predict[0] for predict in predictions]

    def train(self, env, episodes=1):
        """Trains the Neural Network for x episodes and returns the amount of steps, rewards and scores.

        An episode is the same as one game of tetris from start to game over

        A step is the same as a frame in the game.
        Every step it decides on the action to use and saves the result as experience.

        After every episode it trains the model with the 20000 most recent experiences.

        :rtype tuple of (steps, rewards, scoores). steps is an integer, rewards and scores are an integer list
        """
        rewards = []
        scores = []
        steps = 0
        for episode in range(episodes):
            obs = env.reset()
            previous_state = env.game.board.get_info([])
            done = False
            total_reward = 0
            while not done:
                action, state = self.act(obs)
                obs, reward, done, info = env.step(action)
                self.experiences.add((previous_state, reward, state, done))
                previous_state = state
                steps += 1
                total_reward += reward

            rewards.append(total_reward)
            scores.append(env.game.score)

            self.learn()

        return [steps, rewards, scores]

    def load(self):
        """Load the weights."""
        if Path(WEIGHT_PATH).is_file():
            self.model.load_weights(WEIGHT_PATH)

    def save(self):
        """Save the weights."""
        if not os.path.exists(os.path.dirname(WEIGHT_PATH)):
            os.makedirs(os.path.dirname(WEIGHT_PATH))

        self.model.save_weights(WEIGHT_PATH)

    def learn(self, batch_size=512, epochs=1):
        """Let the model learn about its recent experiences to adjust its weights.

        Takes 512 random experiences from the experience buffer of the 20000 most recent steps.
        This ensures that the Neural Network uses recent experiences.

        Afterwards it predicts the future rewards in batch. These ratings are used later for calculating the Q-value.

        Using states and the corresponding Q-values it trains the model.

        After that it lowers the epsilon by multiplying it with the specified decay,
        which means it will explore less and less.
        """
        if len(self.experiences.buffer) < batch_size:
            return

        batch = self.experiences.sample(batch_size)
        train_x = []
        train_y = []

        ratings = self._predict_ratings([x[2] for x in batch])

        for i, (previous_state, reward, next_state, done) in enumerate(batch):
            if not done:
                rating = ratings[i]
                q = reward + self.discount * rating
            else:
                q = reward
            train_x.append(previous_state)
            train_y.append(q)

        self.model.fit(np.array(train_x), np.array(train_y), batch_size=len(train_x), verbose=0,
                       epochs=epochs, callbacks=[self.tensorboard])
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
