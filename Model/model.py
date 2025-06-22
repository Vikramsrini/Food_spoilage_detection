import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump
import random

# Configuration
NUM_SAMPLES = 2000  # Increased sample size
FEATURES = ['MQ8A', 'MQ135A', 'MQ9A', 'MQ4A', 'MQ2A', 'MQ3A']

def generate_realistic_samples():
    """Generates samples with realistic overlap and variance"""
    data = []
    for i in range(NUM_SAMPLES):
        # Base spoilage probability (0-1)
        spoilage_prob = random.uniform(0, 1)
        
        # Generate sensor readings with class overlap
        readings = {}
        for sensor in FEATURES:
            if spoilage_prob < 0.3:  # Definitely fresh
                readings[sensor] = random.gauss(150, 30)
            elif spoilage_prob > 0.7:  # Definitely spoiled
                readings[sensor] = random.gauss(700, 80)
            else:  # Transition zone with overlap
                base = 150 + (spoilage_prob - 0.3) * 1375  # 150-700 range
                readings[sensor] = random.gauss(base, 150)
                
            readings[sensor] = max(0, min(1023, readings[sensor]))  # Clamp to sensor range
        
        # Add temporal effects
        days_old = int(10 * spoilage_prob)  # 0-10 days scale
        
        data.append({
            **readings,
            'label': 1 if spoilage_prob > 0.5 else 0,
            'days_old': days_old,
            'spoilage_prob': spoilage_prob  # For analysis
        })
    
    return pd.DataFrame(data)

# Generate and analyze dataset
df = generate_realistic_samples()
print("Class distribution:\n", df['label'].value_counts())
print("\nTransition zone samples (0.3 < spoilage_prob < 0.7):", 
      df[(df['spoilage_prob'] > 0.3) & (df['spoilage_prob'] < 0.7)].shape[0])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURES], df['label'], test_size=0.3, random_state=42
)

# Train model with regularization
model = RandomForestClassifier(
    n_estimators=150,
    max_depth=5,
    min_samples_split=5,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
print(f"\nTrain accuracy: {model.score(X_train, y_train):.2f}")
print(f"Test accuracy: {model.score(X_test, y_test):.2f}")

# Save artifacts
df.to_csv('realistic_spoilage_dataset.csv', index=False)
dump(model, 'realistic_spoilage_model.joblib')
print("\nDataset and model saved!")
