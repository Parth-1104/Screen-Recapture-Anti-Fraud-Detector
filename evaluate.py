import os
from predict import predict

def run_evaluation():
    categories = {'real': 0, 'screen': 1}
    correct = 0
    total = 0
    
    for folder, label in categories.items():
        if not os.path.exists(folder):
            continue
        for file in os.listdir(folder):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(folder, file)
                score = predict(path)
                pred_label = 1 if score >= 0.5 else 0
                if pred_label == label:
                    correct += 1
                total += 1
                
    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"Validated Benchmark: {correct}/{total} correct -> Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    run_evaluation()