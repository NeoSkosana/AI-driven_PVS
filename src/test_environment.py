import numpy as np
import pandas as pd
import torch
from sklearn import datasets
from transformers import pipeline

def test_installations():
    print("Testing NumPy...")
    arr = np.array([1, 2, 3, 4, 5])
    print("NumPy array:", arr)
    
    print("\nTesting Pandas...")
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    print("Pandas DataFrame:\n", df)
    
    print("\nTesting PyTorch...")
    tensor = torch.tensor([1., 2., 3.])
    print("PyTorch tensor:", tensor)
    
    print("\nTesting Scikit-learn...")
    iris = datasets.load_iris()
    print("Loaded Iris dataset shape:", iris.data.shape)
    
    print("\nTesting Transformers...")
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    result = classifier("Hello, this is a test!")
    print("Transformer test result:", result)

if __name__ == "__main__":
    print("Starting environment test...\n")
    test_installations()
