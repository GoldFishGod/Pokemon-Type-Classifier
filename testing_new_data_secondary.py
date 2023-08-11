# -*- coding: utf-8 -*-
"""testing new data secondary.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SNKb1WpdI7Z6amsSPA0XMPYnLG4WD3LQ

**Primary Model - CNN**

The model chosen to accurately identify the type of a Pokémon from a given image will be a CNN. The encoder aspect of this model will contain several convolutional layers in which the Pokémon image input will be convolved with several kernels. Each kernel will contain the trainable weights that will be updated using gradient descent. Zero-padding and stride will be fine-tuned such that the model will provide the most accurate predictions. After each convolutional layer, a ReLU activation function will be used to map intermediate features and introduce non-linearity. The model will employ the use of max pooling between layers to downscale the image such that kernels in deeper layers look at the most important features of larger regions. In addition, the model will use dropout layers to randomly mask the outputs of some neurons to improve its ability to make more generalized predictions. For each iteration the weights will be trained through gradient descent using a cross entropy function which are commonly used in multi-label classification problems (ie. categorical cross entropy or binary cross entropy loss function). The classifier aspect will consist of the necessary amount of fully-connected layers and a final softmax layer to classify each Pokémon’s type(s).

# New Section
"""

import numpy as np
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt

from google.colab import drive
drive.mount('/content/drive')

def get_accuracy(model, train_data, val_data, batch_size, train=False):
    if train:
        data = train_data
    else:
        data = val_data

    correct = 0
    total = 0
    for imgs, labels in torch.utils.data.DataLoader(data, batch_size=batch_size):

        #############################################
        #To Enable GPU Usage
        if use_cuda and torch.cuda.is_available():
          imgs = imgs.cuda()
          labels = labels.cuda()
        #############################################


        output = model(imgs)

        #select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        correct += pred.eq(labels.view_as(pred)).sum().item()
        total += imgs.shape[0]
    return correct / total

def get_accuracy(model, train_data, val_data, batch_size, train=False):
    if train:
        data = train_data
    else:
        data = val_data

    correct = 0
    total = 0
    class_correct = [0] * len(data.classes)
    class_total = [0] * len(data.classes)

    for imgs, labels in torch.utils.data.DataLoader(data, batch_size=batch_size):
        #############################################
        # To Enable GPU Usage
        if use_cuda and torch.cuda.is_available():
            imgs = imgs.cuda()
            labels = labels.cuda()
        #############################################

        output = model(imgs)

        # Select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        correct += pred.eq(labels.view_as(pred)).sum().item()
        total += imgs.shape[0]

        # Update class-level counts
        for i in range(len(labels)):
            label = labels[i].item()
            prediction = pred[i].item()
            class_correct[label] += int(prediction == label)
            class_total[label] += 1

    accuracy = correct / total
    class_accuracy = [class_correct[i] / class_total[i] for i in range(len(data.classes))]

     #Print accuracy for each class
    for i, class_name in enumerate(data.classes):
        print(f"Accuracy for type {class_name}: {class_accuracy[i]:.2%}")

    print(f"Total accuracy: {accuracy:.2%}")
   # return accuracy

# Training
def get_model_name(name, batch_size, learning_rate, epoch):
    """ Generate a name for the model consisting of all the hyperparameter values

    Args:
        config: Configuration object containing the hyperparameters
    Returns:
        path: A string with the hyperparameter name and value concatenated
    """
    path = "model_{0}_bs{1}_lr{2}_epoch{3}".format(name,
                                                   batch_size,
                                                   learning_rate,
                                                   epoch)
    return path

iters, losses, train_acc, val_acc = [], [], [], []

def train(net, train_data, val_data, batch_size=64, learning_rate=0.001, num_epochs=30):
    torch.manual_seed(1000)

    # Define the Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=learning_rate, momentum=0.9)

    # load training and validation data
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)

    # Set up some arrays to store the training/test loss/erruracy
    #iters, losses, train_acc, val_acc = [], [], [], []

    start_time = time.time()
    n = 0 # the number of iterations
    for epoch in range(num_epochs):  # loop over the dataset multiple times
        total_train_loss = 0.0
        total_train_err = 0.0
        total_epoch = 0
        for imgs, labels in iter(train_loader):

            #############################################
            #To Enable GPU Usage
            if use_cuda and torch.cuda.is_available():
              imgs = imgs.cuda()
              labels = labels.cuda()
            #############################################

            out = net(imgs)             # forward pass
            loss = criterion(out, labels) # compute the total loss
            loss.backward()               # backward pass (compute parameter updates)
            optimizer.step()              # make the updates for each parameter
            optimizer.zero_grad()         # a clean up step for PyTorch

            # save the current training information

            iters.append(n)                                   # track the number of iterations during training
            losses.append(float(loss)/batch_size)             # compute *average* loss
            n += 1 # increment iters
            train_acc.append(get_accuracy(net, train_data, val_data, batch_size, train=True)) # compute training accuracy
            val_acc.append(get_accuracy(net, train_data, val_data, batch_size, train=False))  # compute validation accuracy

        print(("Epoch {}: Train acc: {} | Val acc: {}").format(
            epoch + 1,
            train_acc[-1],
            val_acc[-1]))

        # Save the current model (checkpoint) to a file
        model_path = get_model_name(net.name, batch_size, learning_rate, epoch)
        torch.save(net.state_dict(), model_path)

        # Specify the source file path
        source_file = '/content/' + model_path
        # Specify the destination path
        destination_path = '/content/drive/MyDrive/APS360/MODEL WEIGHTS/type2_balanced/2conv_kernel2_bs80_lr0.0005/first round'
        # Copy the file
        shutil.copy(source_file, destination_path)

    end_time = time.time()
    total_time = end_time - start_time
    print("Training Completed\nTotal training time: {:.2f} seconds".format(total_time))

    # plotting
    plt.title("Training Curve")
    plt.plot(iters, losses, label="Train")
    plt.xlabel("Iterations")
    plt.ylabel("Loss")
    plt.show()

    plt.title("Training Curve")
    plt.plot(iters, train_acc, label="Train")
    plt.plot(iters, val_acc, label="Validation")
    plt.xlabel("Iterations")
    plt.ylabel("Training Accuracy")
    plt.legend(loc='best')
    plt.show()

    print("Final Training Accuracy: {}".format(train_acc[-1]))
    print("Final Validation Accuracy: {}".format(val_acc[-1]))

"""**ALEXNET**"""

import torchvision.models
from torchvision.datasets import DatasetFolder
from torchvision.transforms import ToTensor, ToPILImage
from torch.utils.data import DataLoader
import torchvision.datasets as datasets
alexnet = torchvision.models.alexnet(pretrained=True)

import os
import random
from torch.utils.data.sampler import SubsetRandomSampler
import shutil

#original

class AlexNet(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet, self).__init__()
        self.name = "AlexNet"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.conv2 = nn.Conv2d(380, 512, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.fc1 = nn.Linear(512*4*4, 1024)
        self.fc2 = nn.Linear(1024, numTypes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 512*4*4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class AlexNet2(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet2, self).__init__()
        self.name = "AlexNet2"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=3, padding=1) # in_channels, out_channels, kernel_size
        self.conv2 = nn.Conv2d(380, 512, kernel_size=3, padding=1) # in_channels, out_channels, kernel_size
        self.fc1 = nn.Linear(512 * 6 * 6, 1024)
        self.fc2 = nn.Linear(1024, numTypes)
        self.dropout = nn.Dropout(0.5)  # Add dropout for regularization

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 512 * 6 * 6)  # Correct the reshaping to match the size of the last convolutional layer
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# dropout

class AlexNet_Primary(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet, self).__init__()
        self.name = "AlexNet"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=4, padding=1) # in_channels, out_channels, kernel_size
        self.conv2 = nn.Conv2d(380, 512, kernel_size=4, padding=1) # in_channels, out_channels, kernel_size
        self.fc1 = nn.Linear(512 * 4 * 4, 1024)
        self.fc2 = nn.Linear(1024, numTypes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 512 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 3 conv layers

class AlexNet(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet, self).__init__()
        self.name = "AlexNet"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.conv2 = nn.Conv2d(380, 512, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.conv3 = nn.Conv2d(512, 256, kernel_size=2) # Add another convolutional layer
        self.fc1 = nn.Linear(25633, 1024) # Adjust the input size for the fully connected layer
        self.fc2 = nn.Linear(1024, numTypes)
        self.dropout = nn.Dropout(0.1)  # Add dropout for regularization

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x)) # Apply the third convolutional layer
        x = x.view(-1, 25633) # Adjust the input size for the fully connected layer
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# 1 conv layer

class AlexNet(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet, self).__init__()
        self.name = "AlexNet"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 512, kernel_size=3) #in_channels, out_chanels, kernel_size
        self.fc1 = nn.Linear(512*4*4, 1024)
        self.fc2 = nn.Linear(1024, numTypes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        #x = F.relu(self.conv2(x))
        x = x.view(-1, 512*4*4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class AlexNet(nn.Module):
    def init(self, typeClassifier):
        super(AlexNet, self).init()
        self.name = "AlexNet"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.conv2 = nn.Conv2d(380, 512, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.conv3 = nn.Conv2d(512, 256, kernel_size=2) # Add another convolutional layer
        self.fc1 = nn.Linear(256*3*3, 1024) # Adjust the input size for the fully connected layer
        self.fc2 = nn.Linear(1024, numTypes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x)) # Apply the third convolutional layer
        x = x.view(-1, 256*3*3) # Adjust the input size for the fully connected layer
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 2 conv kernel 2
class AlexNet(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet, self).__init__()
        self.name = "AlexNet"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.conv2 = nn.Conv2d(380, 512, kernel_size=2) #in_channels, out_chanels, kernel_size
        self.fc1 = nn.Linear(512*4*4, 1024) # Adjust the input size for the fully connected layer
        self.fc2 = nn.Linear(1024, numTypes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 512*4*4) # Adjust the input size for the fully connected layer
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

"""**SPLITTING DATA**"""

import os
import random
from torch.utils.data.sampler import SubsetRandomSampler
import shutil

"""**PRIMARY ACCURACY**"""

class_names = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']

# full data
train_data = datasets.DatasetFolder(root="/content/drive/MyDrive/APS360/AlexNet Type1 Balanced Features/Train", loader=torch.load, extensions=('.tensor'))
val_data = datasets.DatasetFolder(root="/content/drive/MyDrive/APS360/AlexNet Type1 Balanced Features/Val", loader=torch.load, extensions=('.tensor'))
test_data = datasets.DatasetFolder(root="/content/drive/MyDrive/APS360/AlexNet Type1 Balanced Features/Test", loader=torch.load, extensions=('.tensor'))

use_cuda = True
file_path = "/content/drive/MyDrive/APS360/MODEL WEIGHTS/type1_balanced/60% test, 99% train, 61% val/model_AlexNet4_no_drop_bs256_lr0.01_epoch9"
alex = AlexNet('Primary')
net = alex
#model_path = get_model_name(net.name, batch_size=100, learning_rate=0.0075, epoch=9)
state = torch.load(file_path)
net.load_state_dict(state)

if use_cuda and torch.cuda.is_available():
  alex.cuda()
  print('CUDA is available!')
else:
  print('CUDA is not available.')

print("Test accuracy for primary Pokemon types")

#test_dir = '/content/drive/MyDrive/APS360/AlexNet Type1 Balanced Features/Test'
#test_data = datasets.DatasetFolder(root=test_dir, loader=torch.load, extensions=('.tensor'))
get_accuracy(alex, test_data, test_data, batch_size=256, train=True) # after 10 epochs

"""**SECONDARY ACCURACY**"""

class_names = ['None', 'Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']

test_data = datasets.DatasetFolder(root="/content/drive/MyDrive/APS360/DATASETS/legends arceus/Features/Type2", loader=torch.load, extensions=('.tensor'))

use_cuda = True
file_path = "/content/drive/MyDrive/APS360/MODEL WEIGHTS/type2_balanced/bs512_lr0.005/fourth round/model_AlexNet_bs512_lr0.005_epoch146"
alex = AlexNet('Secondary')
net = alex
#model_path = get_model_name(net.name, batch_size=100, learning_rate=0.0075, epoch=9)
state = torch.load(file_path)
net.load_state_dict(state)

if use_cuda and torch.cuda.is_available():
  alex.cuda()
  print('CUDA is available!')
else:
  print('CUDA is not available.')

print("Test accuracy for primary Pokemon types")

#test_dir = '/content/drive/MyDrive/APS360/AlexNet Type1 Balanced Features/Test'
#test_data = datasets.DatasetFolder(root=test_dir, loader=torch.load, extensions=('.tensor'))
get_accuracy(alex, test_data, test_data, batch_size=1, train=True) # after 10 epochs

use_cuda = True
file_path = "/content/drive/MyDrive/APS360/MODEL WEIGHTS/type2_balanced/bs512_lr0.01/fourth round/model_AlexNet_bs512_lr0.01_epoch0"
alex = AlexNet('Secondary')
net = alex
#model_path = get_model_name(net.name, batch_size=100, learning_rate=0.0075, epoch=9)
state = torch.load(file_path)
net.load_state_dict(state)

if use_cuda and torch.cuda.is_available():
  alex.cuda()
  print('CUDA is available!')
else:
  print('CUDA is not available.')

print("Test accuracy for primary Pokemon types")

#test_dir = '/content/drive/MyDrive/APS360/AlexNet Type1 Balanced Features/Test'
#test_data = datasets.DatasetFolder(root=test_dir, loader=torch.load, extensions=('.tensor'))
get_accuracy(alex, test_data, test_data, batch_size=512, train=True) # after 10 epochs

"""**Testing Images**"""

alexnet_model = torchvision.models.alexnet(pretrained=True)

file_path = "/content/drive/MyDrive/APS360/MODEL WEIGHTS/type2_balanced/bs512_lr0.005/fourth round/model_AlexNet_bs512_lr0.005_epoch146"
alex = AlexNet('Secondary')
net = alex
#model_path = get_model_name(net.name, batch_size=100, learning_rate=0.0075, epoch=9)
state = torch.load(file_path)
net.load_state_dict(state)

image_path = '/content/drive/MyDrive/APS360/DATASETS/type2_datasets/train/Fire/duplicate_lampent_b5ad20a1-4d25-4926-82b0-3fcb63caade6.jpg'

image = Image.open(image_path)

# Define the transformation to resize and normalize the image
transform = transforms.Compose([
    transforms.Resize((227, 227)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Apply the transformation to the image
input_tensor = transform(image).unsqueeze(0)  # Add batch dimension (1, 3, 227, 227)

# Set the model to evaluation mode
alexnet_model.eval()

# Disable gradient computation for faster inference
with torch.no_grad():
    # Forward pass through the model to get the features
    features = alexnet_model.features(input_tensor)

output = alex(features)

#select index with maximum prediction score
pred = output.max(1, keepdim=True)[1]
print('Secondary Prediction: ', class_names[pred[0]])

file_path = "/content/drive/MyDrive/APS360/MODEL WEIGHTS/type2_balanced/bs512_lr0.005/fourth round/model_AlexNet_bs512_lr0.005_epoch146"
alex = AlexNet('Secondary')
net = alex
#model_path = get_model_name(net.name, batch_size=100, learning_rate=0.0075, epoch=9)
state = torch.load(file_path)
net.load_state_dict(state)

image_path = '/content/drive/MyDrive/APS360/DATASETS/type2_datasets/train/Fire/duplicate_lampent_b5ad20a1-4d25-4926-82b0-3fcb63caade6.jpg'

image = Image.open(image_path)

# Define the transformation to resize and normalize the image
transform = transforms.Compose([
    transforms.Resize((227, 227)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Apply the transformation to the image
input_tensor = transform(image).unsqueeze(0)  # Add batch dimension (1, 3, 227, 227)

# Set the model to evaluation mode
alexnet_model.eval()

# Disable gradient computation for faster inference
with torch.no_grad():
    # Forward pass through the model to get the features
    features = alexnet_model.features(input_tensor)

output = alex(features)

#select index with maximum prediction score
pred = output.max(1, keepdim=True)[1]
print('Secondary Prediction: ', class_names[pred[0]])