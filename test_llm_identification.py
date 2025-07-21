import os
import argparse
from PIL import Image
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from gameplay.humanoid import Humanoid

def run_llm_identification_evaluation(llm_agent, num_images=20, num_batches=1, save_matrix=None):
    data_parser = llm_agent.data_parser
    class_names = ['HEALTHY', 'INJURED', 'CORPSE', 'ZOMBIE']
    all_true_total = []
    all_pred_total = []

    for batch in range(num_batches):
        print(f"\n=== Batch {batch+1}/{num_batches} ===")
        data_parser.reset()  # Make all images available again
        available = len(data_parser.unvisited)
        if available == 0:
            print("No unvisited images available for evaluation.")
            continue
        n = min(num_images, available)
        for i in range(n):
            humanoid = data_parser.get_random()
            prediction = llm_agent.get_model_suggestion(humanoid, identify=True)
            gt = str(humanoid.state).strip().upper()
            pred = str(prediction).strip().upper()
            #print(f"GT: {gt}, Pred: {pred}")
            all_true_total.append(gt)
            all_pred_total.append(pred)

    # Only show aggregate results
    print("\n=== Aggregate Results Across All Batches ===")
    cm_total = confusion_matrix(all_true_total, all_pred_total, labels=class_names)
    print("\nAggregate Confusion Matrix (rows=Actual, cols=Predicted):")
    print("Labels:", class_names)
    print(cm_total)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_total, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('LLM Humanoid Identification Confusion Matrix (Aggregate)')
    if save_matrix:
        plt.savefig(f"{os.path.splitext(save_matrix)[0]}_aggregate.png")
    plt.show()
    print("\nAggregate Classification Report:")
    print(classification_report(all_true_total, all_pred_total, labels=class_names, zero_division='warn'))

if __name__ == "__main__":
    from endpoints.llm_interface import LLMInterface
    from endpoints.data_parser import DataParser
    from gameplay.scorekeeper import ScoreKeeper
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="llava", help="LLM model name")
    parser.add_argument("-n", "--num_images", type=int, default=20, help="Number of images to evaluate per batch")
    parser.add_argument("-b", "--num_batches", type=int, default=1, help="Number of batches to run")
    parser.add_argument("--save_matrix", type=str, default=None, help="Path to save confusion matrix image(s)")
    args = parser.parse_args()
    data_parser = DataParser("data")
    scorekeeper = ScoreKeeper(720, 10)
    llm_agent = LLMInterface(data_parser, scorekeeper, img_data_root="data", model_name=args.model)
    run_llm_identification_evaluation(llm_agent, args.num_images, args.num_batches, args.save_matrix) 