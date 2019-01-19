import copy
import torch
from torch import nn
from torch.distributions import Normal


class Actor(nn.Module):
  def __init__(self):
    super().__init__()
    self.actor = nn.Sequential(nn.Linear(3, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 1))

  def forward(self, state):
    policy = self.actor(state)
    return policy


class Critic(nn.Module):
  def __init__(self, state_action=False):
    super().__init__()
    self.state_action = state_action
    self.critic = nn.Sequential(nn.Linear(3 + (1 if state_action else 0), 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 1))

  def forward(self, state, action=None):
    if self.state_action:
      value = self.critic(torch.cat([state, action], dim=1))
    else:
      value = self.critic(state)
    return value


class ActorCritic(nn.Module):
  def __init__(self):
    super().__init__()
    self.actor = Actor()
    self.critic = Critic()
    self.policy_log_std = nn.Parameter(torch.tensor([[-0.5]]))

  def forward(self, state):
    policy = Normal(self.actor(state), self.policy_log_std.exp())
    value = self.critic(state).squeeze(dim=1)
    return policy, value


def create_target_network(network):
  target_network = copy.deepcopy(network)
  for param in target_network.parameters():
    param.requires_grad = False
  return target_network


def update_target_network(network, target_network, polyak_rate):
  for param, target_param in zip(network.parameters(), target_network.parameters()):
    target_param.data = polyak_rate * target_param.data + (1 - polyak_rate) * param.data
