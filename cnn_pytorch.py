# -*- coding: utf-8 -*-
"""CNN-Pytorch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ttX_aFewK_5XwZh5Le6l899NJdvQyj-C

# CNN using Pytorch

This is a basic CNN template code for anyone to use!
"""

# @title Basic convolutional neural network code in Pytorch #opensource
# @markdown Author: Marc Haraoui

# @markdown Year of update: 2023

import torch

# Check if cuda is available
print(f"Is cuda available? {torch.cuda.is_available()}")

"""## DIY CNN with Pytorch

### CNN Class
"""

import torch.nn as nn
import torch.nn.functional as F

class BasicCNN(nn.Module):
  def __init__(self):
    super(BasicCNN, self).__init__()
    self.conv1 = nn.Conv2d(1, 10, kernel_size=5) # 1 channel (input) to 10 channels (output)
    self.conv2 = nn.Conv2d(10, 20, kernel_size=5) # 10 to 20
    self.fc1 = nn.Linear(320, 50) # Fully connected MLP with 320 inputs and 50 outputs
    self.fc2 = nn.Linear(50, 10) #  MLP: 50 inputs et 10 output classes

  def forward(self, x):
    out = self.conv1(x)
    out = F.max_pool2d(out, 2) # downsampling operation
    out = F.relu(out) # relu activation function
    out = F.relu(F.max_pool2d(self.conv2(out), 2)) # same as three previous lines
    out = out.view(-1, 320)
    out = F.relu(self.fc1(out))
    out = self.fc2(out)
    return F.log_softmax(out, dim=1) # last activation function (probability distribution)

"""### MNIST Dataset"""

import torchvision
import torchvision.transforms as transforms
import torch.optim as optim

# Numpy array to pytorch tensor
transform = transforms.ToTensor()

# Get MNIST dataset for training
trainset = torchvision.datasets.MNIST(root='./data', train=True,
download=True, transform=transform)

# Create the train loader
trainloader = torch.utils.data.DataLoader(trainset, batch_size=32,
shuffle=True, num_workers=2)

# Get MNIST dataset for test
testset = torchvision.datasets.MNIST(root='./data', train=False,
download=True, transform=transform)

#Create the test loader
testloader = torch.utils.data.DataLoader(testset, batch_size=32,
shuffle=False, num_workers=2)

"""### Training our CNN

#### Model init and SGD optimizer

-> You can use another one such as Adam or variations.
"""

cuda = torch.device('cuda')

# Initializing the model on cuda
our_model = BasicCNN().to(cuda)

# SGD optimizer with a e-2 learning rate (you can use a scheduler if necessary)
optimizer = optim.SGD(our_model.parameters(), lr=0.01, momentum=0.9)

"""#### Train and Test functions"""

def train(model, loader, optimizer, epoch, cuda=cuda):
  model.train()
  for batch_idx, (data, target) in enumerate(loader):
    data = data.to(cuda)
    target = target.to(cuda)
    optimizer.zero_grad()

    # Predictions per batch
    output = model(data)

    # Loss
    loss = F.cross_entropy(output, target)
    loss.backward() # back propagation
    optimizer.step()

    # Print result and save checkpoint every 10 batch
    if batch_idx % 10 == 0:
      print('Train epoch {}: [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch, batch_idx * len(data),
            len(loader.dataset),100. * batch_idx / len(loader), loss.item()))

def test(model, loader, cuda=cuda):
  model.eval()
  loss = 0
  correct = 0
  with torch.no_grad(): # no gradient in eval mode
    for data, target in loader:
      data = data.to(cuda)
      target = target.to(cuda)

      # Predictions per batch
      output = model(data)

      # Loss
      loss += F.nll_loss(output, target, reduction='sum').item() # negative log likelihood loss
      prediction = output.max(1, keepdim=True)[1]
      correct += prediction.eq(target.view_as(prediction)).sum().item()
      loss /= len(loader.dataset)

      # Print results
      print('Test: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            loss, correct, len(loader.dataset), 100. * correct / len(loader.dataset)))

"""#### Train and test the model for 3 epochs"""

nb_epochs = 3

for epoch in range(nb_epochs):
    train(our_model, trainloader, optimizer, epoch, cuda)
    test(our_model, testloader, cuda)

"""#### Save checkpoint"""

# If you want to save ckpt, please add a path first
torch.save({
    'epoch': nb_epochs,
    'model_state_dict': our_model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    }, "INSERT_PATH")

"""### Retrain/Fine-tune our CNN

#### Load checkpoint
"""

# To load the checkpoint, use the 'torch.load()' function. Here's an example:
new_model = BasicCNN() # load a new model with the same structure
new_optimizer = optim.SGD(new_model.parameters(), lr=0.01, momentum=0.9)

#retrieve and load checkpoint onto the new model and optimizer
checkpoint = torch.load("INSERT_PATH")
new_model.load_state_dict(checkpoint['model_state_dict'])
new_optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
continue_epoch = checkpoint['epoch']

"""#### Continue training model or fine-tune"""

nb_epochs = 1

for epoch in range(nb_epochs):
    train(new_model, trainloader, new_optimizer, epoch, cuda)
    test(new_model, testloader, cuda)