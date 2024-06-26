import torch
import torch.optim as optim
from PPOModel import PPOModel

class PPOAgent:
    def __init__(self, input_dim, output_dim, lr=0.001, gamma=0.99, epsilon=0.2):
        self.model = PPOModel(input_dim, output_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        state = torch.tensor(state, dtype=torch.float)
        with torch.no_grad():
            action_probs = self.model(state)
        action = torch.argmax(action_probs).item()
        return action

    def update(self, states, actions, rewards):
        states = torch.tensor(states, dtype=torch.float)
        actions = torch.tensor(actions, dtype=torch.long)
        rewards = torch.tensor(rewards, dtype=torch.float)

        for _ in range(10):
            action_probs = self.model(states)
            dist = torch.distributions.Categorical(logits=action_probs)
            action_log_probs = dist.log_prob(actions)

            advantages = rewards - rewards.mean()
            ratios = torch.exp(action_log_probs - action_log_probs.detach())
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1 - self.epsilon, 1 + self.epsilon) * advantages

            loss = -torch.min(surr1, surr2).mean()
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
