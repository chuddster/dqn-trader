from collections import deque
import random
import numpy as np
import math

class DQNAgent(object):
    """ A simple Deep Q agent """

    def __init__(self, mode, model, action_size, memory_size, update_target_freq, batch_size, gamma, epsilon, epsilon_min, epsilon_start, epsilon_decay):
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma  # discount rate
        self.epsilon = epsilon  # exploration rate
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.update_target_freq = update_target_freq
        self.batch_size = batch_size
        self.step = 0
        self.model = model 
        self.model_sub = model 
        self.mode = mode

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if self.mode == "train" and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(np.array([state]))
        return np.argmax(act_values[0])  # returns action

    def update_target_model(self):
        self.model_sub.set_weights(self.model.get_weights())

    def replay(self):
        """ vectorized implementation; 30x speed up compared with for loop """
        minibatch = np.array(random.sample(self.memory, self.batch_size))

        states = np.concatenate(minibatch[:, 0]).reshape(
            self.batch_size, -1)
        actions = np.array([tup[1] for tup in minibatch])
        rewards = np.array([tup[2] for tup in minibatch])
        next_states = np.concatenate(minibatch[:, 3]).reshape(
            self.batch_size, -1)
        done = np.array([tup[4] for tup in minibatch])

        double_dqn = self.model_sub.predict(next_states)[range(
            self.batch_size), np.argmax(self.model.predict(next_states), axis=1)]

        # Q(s', a)
        target = rewards + self.gamma * double_dqn 
        # end state target is reward itself (no lookahead)
        target[done] = rewards[done]

        # Q(s, a)
        target_f = self.model.predict(states)
        # make the agent to approximately map the current state to future discounted reward
        target_f[range(self.batch_size), actions] = target

        if(self.step % self.update_target_freq == 0):
            self.update_target_model()

        self.model.fit(states, target_f, batch_size = self.batch_size, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min and self.step > self.epsilon_start:
                self.epsilon -= self.epsilon_decay
        self.step += 1

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
