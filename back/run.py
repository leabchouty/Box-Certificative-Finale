import numpy as np
from sklearn.cluster import SpectralClustering
import pandas as pd

# === Input data ===
students = {
    "Alice": {"average": 14.5, "intern": 0, "preferences": ["Bob", "Charlie"]},
    "Bob": {"average": 13.0, "intern": 1, "preferences": ["Alice"]},
    "Charlie": {"average": 15.2, "intern": 0, "preferences": ["Eve"]},
    "David": {"average": 12.8, "intern": 1, "preferences": []},
    "Eve": {"average": 14.7, "intern": 0, "preferences": ["Charlie"]},
    "Fay": {"average": 13.3, "intern": 1, "preferences": ["Charlie"]},
    "Gus": {"average": 12.9, "intern": 0, "preferences": []},
    "Hugo": {"average": 14.1, "intern": 0, "preferences": ["Eve"]},
    "Ivy": {"average": 13.9, "intern": 1, "preferences": ["Fay"]},
    "Jack": {"average": 14.0, "intern": 0, "preferences": ["Alice", "Eve"]},
    "Kim": {"average": 12.5, "intern": 1, "preferences": ["Bob", "Charlie"]},
    "Leo": {"average": 13.8, "intern": 0, "preferences": ["Hugo"]},
    "Mia": {"average": 15.0, "intern": 0, "preferences": ["Alice"]},
    "Nina": {"average": 12.7, "intern": 1, "preferences": ["Fay"]},
    "Oscar": {"average": 13.5, "intern": 1, "preferences": ["Nina", "Kim"]},
}

# === Weighting parameters ===
alpha = 2  # affinity
beta = 1   # similar average
gamma = 1  # same internship status

names = list(students.keys())
n = len(names)
similarity_matrix = np.zeros((n, n))

# === Build similarity matrix ===
for i in range(n):
    for j in range(n):
        if i == j:
            continue
        a, b = names[i], names[j]
        sim = 0
        if b in students[a]["preferences"]:
            sim += alpha
        if a in students[b]["preferences"]:
            sim += alpha
        if abs(students[a]["average"] - students[b]["average"]) <= 1.5:
            sim += beta
        if students[a]["intern"] == students[b]["intern"]:
            sim += gamma
        similarity_matrix[i][j] = sim

# === Determine the optimal number of groups (divisible by 5, 4, or 3) ===
for group_size in [5, 4, 3]:
    if n % group_size == 0:
        k = n // group_size
        break
else:
    raise ValueError("Cannot divide students into equal groups of size 3, 4, or 5.")

# === Apply Spectral Clustering ===
model = SpectralClustering(n_clusters=k, affinity='precomputed', random_state=42)
labels = model.fit_predict(similarity_matrix)

# === Organize students by group ===
groups = {}
student_scores = {}

for idx, label in enumerate(labels):
    name = names[idx]
    groups.setdefault(label, []).append(name)

for label, members in groups.items():
    for student in members:
        idx_s = names.index(student)
        score = sum(similarity_matrix[idx_s][names.index(m)] for m in members if m != student)
        student_scores[student] = score

# === Display final results ===
df = pd.DataFrame([
    {"Student": name, "Group": labels[i] + 1, "Score": student_scores[name]}
    for i, name in enumerate(names)
])

print(df.sort_values(by="Group"))
