import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import cross_val_score

# 1. Read data
df = pd.read_csv('test data/cr.csv')

le_crop = LabelEncoder()
df['label'] = le_crop.fit_transform(df['label'])

# 3. Define features and target
X = df.drop(columns=['label'])
y = df['label']

# 4. Train/test split (stratify helps if classes are unbalanced)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 5. Scale numeric features (KNN depends on distance)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 6. Train KNN
knn = KNeighborsClassifier(n_neighbors=3, weights='distance', metric='minkowski')
knn.fit(X_train_scaled, y_train)

# 7. Evaluate
y_pred = knn.predict(X_test_scaled)

def top_crops(sample):
    sample_scaled = scaler.transform(sample)
    probs = knn.predict_proba(sample_scaled)[0]
    top_n = 4
    top_indices = np.argsort(probs)[::-1][:top_n]
    top_crops = le_crop.inverse_transform(top_indices)
    top_probs = probs[top_indices]

    final_top = {}

    for crop, prob in zip(top_crops, top_probs):
        if prob > 0:
            final_top[crop] = prob

    return final_top