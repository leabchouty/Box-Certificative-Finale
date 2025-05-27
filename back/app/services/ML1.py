import random
import pandas as pd
from itertools import combinations

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

names = list(students.keys())
n = len(names)

# === Determine valid group size ===
for group_size in [5, 4, 3]:
    if n % group_size == 0:
        break
else:
    raise ValueError("Cannot divide students evenly into groups of 3, 4, or 5.")

# === Weights ===
alpha = 2  # preference
beta = 1   # average similarity
gamma = 1  # same intern status

# === Score between two students ===
def compute_score(a, b):
    score = 0
    if b in students[a]["preferences"]:
        score += alpha
    if abs(students[a]["average"] - students[b]["average"]) <= 1.5:
        score += beta
    if students[a]["intern"] == students[b]["intern"]:
        score += gamma
    return score

# === Generate sorted student pairs by total mutual compatibility ===
pairs = []
for a, b in combinations(names, 2):
    s1 = compute_score(a, b)
    s2 = compute_score(b, a)
    total = s1 + s2
    pairs.append(((a, b), total))
pairs.sort(key=lambda x: -x[1])

# === Grouping algorithm ===
assigned = set()
groups = []

while len(assigned) < n:
    group = []
    for (a, b), _ in pairs:
        if a not in assigned and b not in assigned:
            group = [a, b]
            assigned.update([a, b])
            break
    for name in names:
        if name not in assigned and len(group) < group_size:
            score_to_group = sum(compute_score(name, member) + compute_score(member, name) for member in group)
            if score_to_group >= len(group) * 2:
                group.append(name)
                assigned.add(name)
    for name in names:
        if name not in assigned and len(group) < group_size:
            group.append(name)
            assigned.add(name)
    groups.append(group)

# === Compute satisfaction scores ===
student_scores = {}
student_groups = {}
max_possible_score = (group_size - 1) * (alpha * 2 + beta + gamma)  # max per pair

for group in groups:
    for student in group:
        score = sum(compute_score(student, other) + compute_score(other, student) for other in group if other != student)
        percent_score = round((score / max_possible_score) * 100, 2)
        student_scores[student] = percent_score
        student_groups[student] = group

# === Display result ===
df = pd.DataFrame([
    {
        "Student": student,
        "Group Members": sorted([name for name in student_groups[student]]),
        "Satisfaction (%)": student_scores[student]
    }
    for student in sorted(names)
])

print(df.to_string(index=False))
