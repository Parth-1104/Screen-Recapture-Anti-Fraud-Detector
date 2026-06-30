import os
import sys
import warnings
import pickle
import numpy as np


warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import torch
from torchvision import models, transforms
from PIL import Image

def predict(image_path):
    try:
        if not os.path.exists("model_weights.pkl"):
            return 0.5
            
        # Load classification model
        with open("model_weights.pkl", "rb") as f:
            clf = pickle.load(f)
            
        # Setup Feature Extractor
        device = 'cpu'
        weights = models.MobileNet_V3_Small_Weights.DEFAULT
        model = models.mobilenet_v3_small(weights=weights)
        model.classifier = torch.nn.Identity()
        model.eval()
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        # Process input image
        img = Image.open(image_path).convert('RGB')
        tensor = transform(img).unsqueeze(0)
        
        with torch.no_grad():
            feat = model(tensor).squeeze().numpy().reshape(1, -1)
            

        prob = clf.predict_proba(feat)[0][1]
        return round(float(prob), 2)
        
    except Exception:
        return 0.5

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(0.5)
        sys.exit(1)
    print(predict(sys.argv[1]))