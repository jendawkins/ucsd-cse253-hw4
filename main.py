from __future__ import print_function
import torch.autograd as autograd
from torch.autograd import Variable
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import random
import pdb
import numpy as np

from helper import *
from train_model import *
from LSTM import *
from generate_music import *

# input data
with open('input.txt', 'r') as f:
    data = f.read()

vocab = get_idx(data)
# check for GPU
use_gpu = torch.cuda.is_available()

seq_len = 30
batch_size = 10
num_epochs = 5

predict_length = 100
primer = '<start>'
temperature = 1

model = LSTM_Mod2(100, len(vocab), batch_size, seq_len, is_gpu=use_gpu)
train_loss, val_loss = train_model(model, data, vocab, seq_len, batch_size, num_epochs, use_gpu)

plt.figure()
plt.plot(range(len(train_loss)),train_loss,label = 'Training Loss')
plt.plot(range(len(val_loss)),val_loss,label = 'Validation Loss')
plt.xticks(list(np.cumsum(np.repeat(round(len(train_loss)/num_epochs), num_epochs))),tuple([str(x) for x in range(num_epochs)]))
plt.text(20,.15, 'Min Validation Loss = '+ str( min(val_loss)) )
plt.show()
# words = generate(model, vocab, primer, predict_length, temperature, use_gpu)
# print(words)
