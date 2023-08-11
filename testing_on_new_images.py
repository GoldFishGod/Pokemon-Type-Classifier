# -*- coding: utf-8 -*-
"""Testing on new images

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bY_LKduBgzcUcw4EZdlGZ2q9O5_6A8L5
"""

#import required libraries
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import tensorflow as tf
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from PIL import Image

import time
import torchvision.models
alexnet = torchvision.models.alexnet(pretrained=True)
! pip install wget

from google.colab import drive
drive.mount('/content/gdrive')

class AlexNet2(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet2, self).__init__()
        self.name = "AlexNet2"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(380, 512, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(512 * 6 * 6, 1024)
        self.fc2 = nn.Linear(1024, numTypes)
        self.dropout = nn.Dropout(0.5)  # Add dropout for regularization

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 512 * 6 * 6)  # Correct the reshaping to match the size
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class AlexNet4(nn.Module):
    def __init__(self, typeClassifier):
        super(AlexNet4, self).__init__()
        self.name = "AlexNet4"
        if typeClassifier == 'Primary':
            numTypes = 18
        elif typeClassifier == 'Secondary':
            numTypes = 19

        self.conv1 = nn.Conv2d(256, 380, kernel_size=4, padding=1)
        self.conv2 = nn.Conv2d(380, 512, kernel_size=4, padding=1)
        self.fc1 = nn.Linear(512 * 4 * 4, 1024)
        self.fc2 = nn.Linear(1024, numTypes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(-1, 512 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

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

model = AlexNet4('Primary')

use_cuda = True

if use_cuda and torch.cuda.is_available():
  model.cuda()
  print('CUDA is available!  Training on GPU ...')
else:
  print('CUDA is not available.  Training on CPU ...')


model_path = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/MODEL WEIGHTS/type1_balanced/61% test, 99% train, 63% val/model_AlexNet4_bs256_lr0.001_epoch3'  # Update with your model's path
model.load_state_dict(torch.load(model_path))

model2 = AlexNet('Secondary')

use_cuda = True

if use_cuda and torch.cuda.is_available():
  model2.cuda()
  print('CUDA is available!  Training on GPU ...')
else:
  print('CUDA is not available.  Training on CPU ...')


model2_path = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/MODEL WEIGHTS/type2_balanced/bs512_lr0.005/fourth round/model_AlexNet_bs512_lr0.005_epoch146'  # Update with your model's path
model2.load_state_dict(torch.load(model2_path))

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()  # Convert image to tensor without normalization
])

img_path = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/gen9 sorted/type2_pokemon/None/sprigatito.jpg'

image = Image.open(img_path)
tensor_input = preprocess(image)
print(type(tensor_input))

import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image
from io import BytesIO

image_url = 'https://img.pokemondb.net/sprites/home/normal/2x/kyogre.jpg'

# Download the image from the URL
response = requests.get(image_url)
response.raise_for_status()  # Check for any download errors

# Open the image using PIL.Image.open()
image = Image.open(BytesIO(response.content))
tensor_input = preprocess(image)
print(type(tensor_input))

# Resize the image to 224x224 pixels
image_resized = image.resize((224, 224), Image.ANTIALIAS)

# Convert PIL image to a NumPy array
image_np = np.array(image_resized)

# Plot the resized image
plt.imshow(image_np)
plt.axis('off')  # Hide the axis
plt.show()

feature_extraction = alexnet.features(tensor_input)
features_tensor = torch.from_numpy(feature_extraction.detach().numpy())
features_tensor = features_tensor.to('cuda')

#features_tensor = torch.load('/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/legends arceus/Attempt2/Type1_Features/Flying/Copy of 16.tensor')
features_tensor = features_tensor.to('cuda')
output = model(features_tensor)

pred = tf.nn.softmax(output.detach().cpu().numpy())
max_index = tf.argmax(pred, axis=1)
#print(pred[0])
#print(max_index.numpy().item())
classes = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting',
             'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice',
             'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water', 'None']
type1 = classes[max_index.numpy().item()]
print("Type 1: ",type1)


classes = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting',
             'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Water', 'None',
             'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']

output2 = model2(features_tensor)
pred2 = tf.nn.softmax(output2.detach().cpu().numpy())

max_index2 = tf.argmax(pred2, axis=1)
#print(pred2[0])
#print(max_index2.numpy().item())
type2 =classes[max_index2.numpy().item()]
print("Type 2: ", type2)

import torch
import matplotlib.pyplot as plt

# Create an instance of your AlexNet model
model = AlexNet4(typeClassifier='Primary')

# Load pre-trained weights if available
# (Assuming you have trained the model or loaded pre-trained weights before plotting)
# model.load_state_dict(torch.load('path_to_your_pretrained_weights.pth'))

# Get the weights of the first convolutional layer (self.conv1)
weights_conv1 = model.conv1.weight.data

# Normalize the weights for visualization (optional but can improve visualization)
weights_conv1 = (weights_conv1 - weights_conv1.min()) / (weights_conv1.max() - weights_conv1.min())

# Plot the first 9 kernels in a 3x3 grid
fig, axes = plt.subplots(3, 3, figsize=(8, 8))

for i, ax in enumerate(axes.flat):
    ax.imshow(weights_conv1[i, 0].cpu(), cmap='gray')
    ax.axis('off')

plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.show()

"""Testing on Legends Arceus Sprites"""

def get_accuracy(model, data, batch_size, train=False):
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

path_test = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/legends arceus/Attempt2/Type1_Features'
path_test = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/gen9 sorted/Features/Type 1'
dataset_test = torchvision.datasets.DatasetFolder(path_test, loader=torch.load, extensions=('.tensor'))

get_accuracy(model, dataset_test, 1)

path_test2 = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/legends arceus/Attempt2/Type2_Features'
#path_test2 = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/AlexNet Type2 Balanced Features/Test'
dataset_test2 = torchvision.datasets.DatasetFolder(path_test2, loader=torch.load, extensions=('.tensor'))

def get_accuracy(model, data, batch_size, train=False):
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

get_accuracy(model2, dataset_test2, 1)

# img = ... a PyTorch tensor with shape [N,3,224,224] containing hand images ...
root_dir = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/legends arceus/Type 2'

transform = transforms.Compose([
    #transforms.Resize((435, 435)),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

train_set_new = torchvision.datasets.ImageFolder(root_dir, transform=transform)

data_loader = torch.utils.data.DataLoader(train_set_new, batch_size=1, shuffle=True)

def get_features(data_loader, dir):
  n = 0
  classes = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting',
             'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice',
             'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water', 'None']
  dataiter = iter(data_loader)

  for imgs, labels in data_loader:
    features = alexnet.features(imgs)
    features_tensor = torch.from_numpy(features.detach().numpy())

    folder_name = dir + '/' + str(classes[labels])
    if not os.path.isdir(folder_name):
      os.mkdir(folder_name)
    torch.save(features_tensor.squeeze(0), folder_name + '/' + str(n) + '.tensor')
    n = n+1
    if n%10 == 0:
      print("Total is: ", n)

train_dir = '/content/gdrive/MyDrive/Third Year/Summer 2023/APS360/DATASETS/legends arceus/Features/Type2_Adjusted_Labels2'

print("getting features from train set...")
get_features(data_loader, train_dir)