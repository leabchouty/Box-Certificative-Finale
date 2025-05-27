import pandas as pd
from itertools import combinations
import random

# === Données des étudiants ===
students = {
    "Alice": {"average": 14.5, "intern": 0, "preferences": ["Bob", "Charlie"]},
    "Bob": {"average": 13.0, "intern": 1, "preferences": ["Alice"]},
    "Charlie": {"average": 15.2, "intern": 0, "preferences": ["Eve"]},
    "David": {"average": 8.8, "intern": 1, "preferences": []},
    "Eve": {"average": 14.7, "intern": 0, "preferences": ["Charlie"]},
    "Fay": {"average": 11.3, "intern": 1, "preferences": ["Charlie"]},
    "Gus": {"average": 9.9, "intern": 0, "preferences": []},
    "Hugo": {"average": 14.1, "intern": 0, "preferences": ["Eve"]},
    "Ivy": {"average": 10.9, "intern": 1, "preferences": ["Fay"]},
    "Jack": {"average": 10.0, "intern": 0, "preferences": ["Alice", "Eve"]},
    "Kim": {"average": 9.5, "intern": 1, "preferences": ["Bob", "Charlie"]},
    "Leo": {"average": 13.8, "intern": 0, "preferences": ["Hugo"]},
    "Mia": {"average": 15.0, "intern": 0, "preferences": ["Alice"]},
    "Nina": {"average": 12.7, "intern": 1, "preferences": ["Fay"]},
    "Oscar": {"average": 13.5, "intern": 1, "preferences": ["Nina", "Kim"]},
}

names = list(students.keys())
n = len(names)

# === Déterminer la taille des groupes ===
for group_size in [5, 4, 3]:
    if n % group_size == 0:
        break
else:
    raise ValueError("Impossible de diviser les étudiants en groupes égaux.")

# === Attribuer un niveau académique
def get_level(avg):
    if avg < 10:
        return "Low"
    elif avg < 13:
        return "Medium"
    else:
        return "High"

# === Calcul du score (préférence + mixité alternant)
alpha = 2  # préférence

def compute_score(a, b):
    score = 0
    if b in students[a]["preferences"]:
        score += alpha
    if students[a]["intern"] != students[b]["intern"]:
        score += 1  # favorise les binômes mixtes
    return score

# === Générer les paires triées
pairs = []
for a, b in combinations(names, 2):
    total = compute_score(a, b) + compute_score(b, a)
    pairs.append(((a, b), total))
pairs.sort(key=lambda x: -x[1])

# === Création des groupes
assigned = set()
groups = []
levels = {name: get_level(data["average"]) for name, data in students.items()}
interns = [name for name in names if students[name]["intern"] == 1]
random.shuffle(interns)

while len(assigned) < n:
    group = []

    # Ajouter au moins un alternant
    for intern in interns:
        if intern not in assigned:
            group.append(intern)
            assigned.add(intern)
            break

    # Ajouter un étudiant de chaque niveau manquant
    needed_levels = {"Low", "Medium", "High"} - {levels[stu] for stu in group}
    for level in needed_levels:
        for name in names:
            if name not in assigned and levels[name] == level:
                group.append(name)
                assigned.add(name)
                break

    # Compléter le groupe
    for name in names:
        if name not in assigned:
            group.append(name)
            assigned.add(name)
            if len(group) == group_size:
                break

    groups.append(group)

# === Calcul des scores de satisfaction
student_scores = {}
student_groups = {}
max_score = (group_size - 1) * (alpha * 2 + 1)  # 2 préférences mutuelles + 1 mixité

for group in groups:
    for student in group:
        score = sum(compute_score(student, other) + compute_score(other, student)
                    for other in group if other != student)
        percent = round((score / max_score) * 100, 2)
        student_scores[student] = percent
        student_groups[student] = group

# === Affichage final
df = pd.DataFrame([
    {
        "Student": student,
        "Group Members": sorted(student_groups[student]),
        "Level": levels[student],
        "Intern": students[student]["intern"],
        "Average": students[student]["average"],
        "Satisfaction (%)": student_scores[student]
    }
    for student in sorted(names)
])

print(df.to_string(index=False))
