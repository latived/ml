import gym
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


class RLAgent(object):
    
    def __init__(self, m, n, ini=False, W=None, b=None):
        self._graph = tf.Graph()
        with self._graph.as_default():
            self._X = tf.placeholder(tf.float32, shape=(1, m))
            if ini == False:
                self.W = tf.Variable(tf.random_normal([m, n]), trainable=False)
                self.bias = tf.Variable(tf.random_normal([1, n]), trainable=False)
            else:
                self.W = W
                self.bias = b
            out = tf.nn.sigmoid(tf.matmul(self._X, self.W) + self.bias)
            self._result = tf.multinomial(out, 1)
            init = tf.global_variables_initializer()
            self._sess = tf.Session()
            self._sess.run(init)

    def predict(self, X):
        action = self._sess.run(self._result, feed_dict={ self._X: X })
        return action

    def get_weights(self):
        W, b = self._sess.run([self.W, self.bias])
        return W, b


def play_one_episode(env, agent, show=False):
    obs = env.reset()
    img_pre = preprocess_image(obs)
    done = False
    t = 0
    while not done and t < 10000:
        if show:
            env.render()  # Ths can be commented to speed up
        t += 1
        action = agent.predict(img_pre)
        #print(t, action)
        obs, reward, done, info = env.step(action)
        img_pre = preprocess_image(obs)
        if done:
            break
    return t


def play_multiple_episodes(env, T, ini=False, W=None, b=None, show=False):
    episode_lengths = np.empty(T)
    obs = env.reset()
    img_pre = preprocess_image(obs)
    if not ini:
        agent = RLAgent(img_pre.shape[1], env.action_space.n)
    else:
        agent = RLAgent(img_pre.shape[1], env.action_space.n, ini, W, b)
    for i in range(T):
        episode_lengths[i] = play_one_episode(env, agent, show)
    avg_length = episode_lengths.mean()
    print("avg length: ", avg_length)
    if not ini:
        W, b = agent.get_weights()
    return avg_length, W, b


def random_search(env):
    episode_lengths = []
    best = 0
    for t in range(10):
        print("Agent {} reporting".format(t))
        avg_length, wts, bias = play_multiple_episodes(env, 10)
        episode_lengths.append(avg_length)
        if avg_length > best:
            best_wt = wts
            best_bias = bias
            best = avg_length
    return episode_lengths, best_wt, best_bias


def preprocess_image(img):
    img = img.mean(axis=2)  # to grayscale
    img[img == 150] = 0  # inc contrast
    img = (img - 128)/128 - 1  # norm to -1 to 1
    m, n = img.shape
    return img.reshape(1, m * n)


def load_weights_and_bias(weights, bias):
    W = np.load(weights)
    b = np.load(bias)
    return W, b


if __name__ ==  '__main__':
    train = False
    W, b = None, None
    env_name = 'MsPacman-v0'
    env = gym.make(env_name)
    if train:
        episode_lengths, W, b = random_search(env)
        plt.plot(episode_lengths)
        plt.show()
    else:
        W, b = load_weights_and_bias('pacman_nn_weights.npy', 'pacman_nn_bias.npy')
    print('Final run with the Best Agent')
    play_multiple_episodes(env, 10, ini=True, W=W, b=b, show=True)

