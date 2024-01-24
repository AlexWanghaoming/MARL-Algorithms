import torch.nn as nn
import torch.nn.functional as f
from .utils import init, get_clones

class RNN(nn.Module):
    # Because all the agents share the same network, input_shape=obs_shape+n_actions+n_agents
    def __init__(self, input_shape, args):
        super(RNN, self).__init__()
        self.args = args
        gain = nn.init.calculate_gain('relu')
        def init_(m):
            return init(m,  nn.init.orthogonal_, lambda x: nn.init.constant_(x, 0), gain=gain)

        self.fc1 = nn.Sequential(
            init_(nn.Linear(input_shape, args.rnn_hidden_dim)), nn.ReLU(), nn.LayerNorm(args.rnn_hidden_dim))
        self.fc_h = nn.Sequential(init_(
            nn.Linear(args.rnn_hidden_dim, args.rnn_hidden_dim)), nn.ReLU(), nn.LayerNorm(args.rnn_hidden_dim))

        if self.args.use_rnn:
            self.rnn = nn.GRUCell(args.rnn_hidden_dim, args.rnn_hidden_dim)
        else:
            self.mlp = nn.Sequential(init_(nn.Linear(args.rnn_hidden_dim, args.rnn_hidden_dim)),
                                     nn.ReLU(),
                                     nn.LayerNorm(args.rnn_hidden_dim))

        self.fc2 = nn.Linear(args.rnn_hidden_dim, args.n_actions)
        self.feature_norm = nn.LayerNorm(input_shape)


    def forward(self, obs, hidden_state):
        obs = self.feature_norm(obs)
        x = self.fc1(obs)
        if self.args.use_rnn:
            h_in = hidden_state.reshape(-1, self.args.rnn_hidden_dim)
            h = self.rnn(x, h_in)
        else:
            h = self.mlp(x)
        q = self.fc2(h)

        return q, h


# Critic of Central-V
class Critic(nn.Module):
    def __init__(self, input_shape, args):
        super(Critic, self).__init__()
        self.args = args
        self.fc1 = nn.Linear(input_shape, args.critic_dim)
        self.fc2 = nn.Linear(args.critic_dim, args.critic_dim)
        self.fc3 = nn.Linear(args.critic_dim, 1)

    def forward(self, inputs):
        x = f.relu(self.fc1(inputs))
        x = f.relu(self.fc2(x))
        q = self.fc3(x)
        return q
