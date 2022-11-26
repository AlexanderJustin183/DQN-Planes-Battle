#!usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "AlexanderJustin"
# My blog: https://www.blog.csdn.net/AlexanderJustin183/article
__version__ = "3.0.1"

__doc__ = """
QTrainer for Snake AI.
Date: 2022-11-22
"""

import os

import numpy as np
import torch
from torch import nn, optim


# Torch(PyTorch): https://www.pytorch.org
# ``pip install torch torchvision torchaudio``


class Linear_QNet(nn.Module):
    """docstring for Linear_QNet"""
    
    def __init__(self, input_size, hidden_size, output_size=3, use_cuda=False):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
        if use_cuda:
            self.net = self.net.cuda()
        self.cuda = use_cuda
    
    def forward(self, x):
        v = self.net(x)
        if self.cuda:
            v = v.cuda()
        return v
    
    def save(self, file_name="model.pth"):
        try:
            model_folder_path = "./model"
            if not os.path.exists(model_folder_path):
                os.makedirs(model_folder_path)
            file_name = os.path.join(model_folder_path, file_name)
            torch.save(self.state_dict(), file_name)
            print("Save model successfully!")
        except BaseException as ex:
            print("[ERROR CODE 0]Failed to save model. Reason:", ex)


class QTrainer():
    """docstring for QTrainer"""
    
    def __init__(self, model, lr, gamma, use_cuda=False):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.cuda = use_cuda
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        if self.cuda:
            self.criterion = self.criterion.cuda()
    
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(np.array(state), dtype=torch.float)
        next_state = torch.tensor(np.array(next_state), dtype=torch.float)
        action = torch.tensor(np.array(action), dtype=torch.long)
        reward = torch.tensor(np.array(reward), dtype=torch.float)
        if self.cuda:
            state = state.cuda()
            next_state = next_state.cuda()
            action = action.cuda()
            reward = reward.cuda()
        
        # (n, x)
        
        if len(state.shape) == 1:
            # (1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            if self.cuda:
                state = state.cuda()
                next_state = next_state.cuda()
                action = action.cuda()
                reward = reward.cuda()
            done = (done,)
        
        # 1: predicted Q values with current state
        predict = self.model(state)
        
        target = predict.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                model = self.model(next_state[idx])
                if self.cuda:
                    model = model.cuda()
                Q_new = reward[idx] + self.gamma * torch.max(model)
            
            target[idx][torch.argmax(action[idx]).item()] = Q_new
        
        # 2: Q_ne = r + y * max(next_predicted Q value) -> only do this if not done
        # predict.clone()
        # prods[torch.argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, predict)
        if self.cuda:
            loss = loss.cuda()
        loss.backward()
        
        self.optimizer.step()  # if comment out this line, the trainer will never step

#
# app.io.funcIO(async.Batch().func_base(myWrapper))
