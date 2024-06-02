# Imports here
from __future__ import division, print_function

import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.models as models
from PIL import Image, ImageFile
from torch import nn
from torchvision import models, transforms

ImageFile.LOAD_TRUNCATED_IMAGES = True
# Import useful sklearn functions


test_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    #torchvision.transforms.ColorJitter(brightness=2, contrast=2),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.ToTensor(),
    transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))
])


# Define the model class
class Model:
    def __init__(self, num_classes=5):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = models.resnet152(weights=None)
        num_ftrs = self.model.fc.in_features
        
        self.model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes),
            nn.LogSoftmax(dim=1)
        )

        # Freeze certain layers for no learning
        for name, child in self.model.named_children():
            for param in child.parameters():
                param.requires_grad = False

        self.model.to(self.device)

    def load_model(self, path):
        """Load a PyTorch model from a checkpoint file."""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])

    def test_with_single_image(self, file, classes):
        """Test the model with a single image.(image tranformation)"""
        file = Image.open(file).convert('RGB')
        img = test_transforms(file).unsqueeze(0).to(self.device)

        with torch.no_grad():
            self.model.eval() #evalutation model
            out = self.model(img)
            ps = torch.exp(out)
            top_p, top_class = ps.topk(1, dim=1)
            value = top_class.item()
           
        return value,file