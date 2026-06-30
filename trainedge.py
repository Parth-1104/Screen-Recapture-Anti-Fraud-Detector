import os
import torch
import cv2
import numpy as np
import pickle
from torchvision import models, transforms
from sklearn.linear_model import LogisticRegression
from PIL import Image


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
weights = models.MobileNet_V3_Small_Weights.DEFAULT
model = models.mobilenet_v3_small(weights=weights).to(device)
model.eval()


model.classifier = torch.nn.Identity()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_features(img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        tensor = transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            feat = model(tensor).squeeze().cpu().numpy()
        return feat
    except Exception:
        return None

def main():
    X, y = [], []
    print("Extracting deep edge features from dataset...")
    
    for folder, label in [('real', 0), ('screen', 1)]:
        if not os.path.exists(folder): continue
        for f in os.listdir(folder):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(folder, f)
                feat = extract_features(path)
                if feat is not None:
                    X.append(feat)
                    y.append(label)
                    
    X, y = np.array(X), np.array(y)
    

    clf = LogisticRegression(C=1.0, max_iter=1000)
    clf.fit(X, y)
    
    train_acc = clf.score(X, y) * 100
    print(f"\n=============================================")
    print(f"🎉 SUCCESS: Model trained with Accuracy: {train_acc:.2f}%")
    print("=============================================")
    
    # Save the lightweight model weights
    with open("model_weights.pkl", "wb") as f:
        pickle.dump(clf, f)
    print("Saved classification boundary to 'model_weights.pkl'.")

if __name__ == "__main__":
    main()