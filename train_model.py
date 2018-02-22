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

from generate_music import *
from LSTM import *
from helper import *

def train_model(model, data, vocab_idx, seq_len, batch_size, epochs, use_gpu):
    vocab_size = len(vocab_idx)

    # slice data into trianing and testing (could do this much better)
    slice_ind = int(round(len(data)*.8))
    training_data = data[:slice_ind]
    val_data = data[slice_ind:]

    # turn training and validation data from characters to numbers
    training_nums = [vocab_idx[char] for char in training_data]
    val_nums = [vocab_idx[char] for char in val_data]

    val_inputs = prepare_data(val_nums[:-1], use_gpu)
    val_targets = prepare_data(val_nums[1:], use_gpu)

    np.random.seed(0)

    if use_gpu:
        model.cuda()

    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    # train model
    train_loss_vec = []
    val_loss_vec=[]
    for epoch in range(epochs):
        #get random slice
        a = range(len(training_data) - (seq_len+1))
        # after going through all of a , will have gone through all possible 30
        # character slices
        total = 0
        correct = 0
        iterate = 0
        while len(a) >30:
            model.bs = batch_size
            idxs = random.sample(a,batch_size)
            # get random slice, and the targets that correspond to that slice
            rand_slice = [training_nums[idx : idx + seq_len] for idx in idxs]
            rand_slice = np.array(rand_slice).T
            targets = [training_nums[idx + 1:idx+(seq_len+1)] for idx in idxs]
            targets = np.array(targets).T

            for idx in idxs:
                a.remove(idx)

            # prepare data and targets for model
            rand_slice = prepare_data(rand_slice, use_gpu)
            targets = prepare_data(targets, use_gpu)
            # Pytorch accumulates gradients. We need to clear them out before each instance
            model.zero_grad()

            # Also, we need to clear out the hidden state of the LSTM,
            # detaching it from its history on the last instance.
            model.hidden = model.init_hidden()
            # From TA:
            # another option is to feed sequences sequentially and let hidden state continue
            # could feed whole sequence, and then would kill hidden state

            # Run our forward pass.
            outputs = model(rand_slice)
            # Step 4. Compute the loss, gradients, and update the parameters by
            #  calling optimizer.step()
            loss=0
            for bat in range(batch_size):
                loss += loss_function(outputs[:,bat,:], targets[:,bat,:].squeeze(1))
            loss.backward()
            optimizer.step()

            # correct, total, running_accuracy = get_accuracy(outputs.squeeze(1), targets, correct, total)
            if iterate == 2000 % 1999 :
                print('Loss ' + str(loss.data[0]))
                train_loss_vec.append(loss.data[0])
                # model.bs = 1
                # model.init_hidden()
            # if iterate == 4000 % 3999 :
            #     # model.seq_len = len(val_inputs)
            #     pdb.set_trace()
            #     outputs_val = model(val_inputs)
            #     val_loss = loss_function(outputs_val[:,1,:], val_targets[:,1,:].squeeze(1))
            #     val_loss_vec.append(val_loss)
            #     model.bs = batch_size
            #     print('Validataion Loss ' + str(val_loss))
            iterate += 1
        print('Completed Epoch ' + str(epoch))
        print(generate(model, vocab, primer, predict_length, temperature, use_gpu))
    return train_loss_vec, val_loss_vec