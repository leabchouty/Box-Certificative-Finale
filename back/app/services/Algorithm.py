from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, value

students = [
    {"name": "Alice", "mean": 15.2, "alt": False},
    {"name": "Bob", "mean": 11.5, "alt": True},
    {"name": "Charlie", "mean": 8.9, "alt": False},
    {"name": "Diana", "mean": 13.0, "alt": True},
    {"name": "Eli", "mean": 16.5, "alt": False},
    {"name": "Fanny", "mean": 9.8, "alt": True},
    {"name": "Gaspard", "mean": 14.1, "alt": False},
    {"name": "Hugo", "mean": 10.5, "alt": True},
    {"name": "Isabelle", "mean": 12.3, "alt": False},
    {"name": "Jade", "mean": 17.8, "alt": True},
    {"name": "Kamel", "mean": 9.4, "alt": False},
    {"name": "Laura", "mean": 13.7, "alt": True},
    {"name": "Marc", "mean": 11.2, "alt": False},
]

# Approximate group size
n = 3

# Preferences
preferences = {
    "Alice": ["Bob", "Jade", "Diana", "Fanny", "Isabelle"],
    "Bob": ["Diana", "Fanny", "Isabelle", "Alice", "Gaspard"],
    "Charlie": ["Hugo", "Fanny", "Kamel", "Isabelle", "Gaspard"],
    "Diana": ["Laura", "Fanny", "Jade", "Alice", "Gaspard"],
    "Eli": ["Jade", "Alice", "Gaspard", "Isabelle", "Diana"],
    "Fanny": ["Charlie", "Gaspard", "Diana", "Hugo", "Jade"],
    "Gaspard": ["Laura", "Hugo", "Alice", "Eli", "Isabelle"],
    "Hugo": ["Kamel", "Isabelle", "Fanny", "Bob", "Jade"],
    "Isabelle": ["Bob", "Kamel", "Jade", "Diana", "Fanny"],
    "Jade": ["Eli", "Alice", "Hugo", "Diana", "Charlie"],
    "Kamel": ["Hugo", "Charlie", "Diana", "Fanny", "Isabelle"],
    "Laura": ["Gaspard", "Diana", "Fanny", "Isabelle", "Eli"],
    "Marc": ["Jade", "Fanny", "Bob", "Diana", "Charlie"],
}

student_names = [s["name"] for s in students]
student_info = {s["name"]: s for s in students}
total_students = len(students)

# Calculate number of groups
num_groups = total_students // n
remainder = total_students % n

if num_groups == 0:
    raise ValueError("Pas assez d'étudiants pour former au moins un groupe.")

# Assign level
for s in students:
    if s["mean"] < 10:
        s["level"] = "low"
    elif s["mean"] < 14:
        s["level"] = "medium"
    else:
        s["level"] = "high"

# Variables
x = LpVariable.dicts("x", ((i, g) for i in student_names for g in range(num_groups)), cat=LpBinary)
z = LpVariable.dicts(
    "z",
    ((i, j, g) for i in student_names for j in preferences.get(i, []) for g in range(num_groups)),
    cat=LpBinary,
)

# Problem
prob = LpProblem("GroupAssignmentWithPreferences", LpMaximize)

# Objective
prob += (
    5 * lpSum(z[i, j, g] for i in student_names for j in preferences.get(i, []) for g in range(num_groups))
    + lpSum(x[i, g] for i in student_names for g in range(num_groups) if student_info[i]["level"] == "low")
    + lpSum(x[i, g] for i in student_names for g in range(num_groups) if student_info[i]["level"] == "medium")
    + lpSum(x[i, g] for i in student_names for g in range(num_groups) if student_info[i]["level"] == "high")
)

# Each student assigned to exactly one group
for i in student_names:
    prob += lpSum(x[i, g] for g in range(num_groups)) == 1

# Group size: some groups with n+1 students
for g in range(num_groups):
    if g < remainder:
        prob += lpSum(x[i, g] for i in student_names) == n + 1
    else:
        prob += lpSum(x[i, g] for i in student_names) == n

# Preference satisfaction
for i in student_names:
    for j in preferences.get(i, []):
        for g in range(num_groups):
            prob += z[i, j, g] <= x[i, g]
            prob += z[i, j, g] <= x[j, g]
            prob += z[i, j, g] >= x[i, g] + x[j, g] - 1

# Solve
prob.solve()

# Evaluation
total_possible = sum(len(preferences.get(i, [])) for i in student_names)
total_matched = 0

for i in student_names:
    for j in preferences.get(i, []):
        for g in range(num_groups):
            if value(x[i, g]) == 1 and value(x[j, g]) == 1:
                total_matched += 1
                break

# Output
if prob.status == 1:
    print(f"\n✅ Répartition en {num_groups} groupes (taille approx. {n}) réussie :\n")
    for g in range(num_groups):
        print(f"🧩 Groupe {g+1}:")
        for i in student_names:
            if value(x[i, g]) == 1:
                s = student_info[i]
                print(f" - {i} (mean={s['mean']}, level={s['level']}, alternant={s['alt']})")
        print()
    if total_possible > 0:
        score_pct = (total_matched / total_possible) * 100
        print(f"📊 Score de satisfaction : {total_matched}/{total_possible} préférences respectées ({score_pct:.1f}%)")
    else:
        print("📊 Score de satisfaction : aucune préférence exprimée.")
else:
    print("\n❌ Aucune solution réalisable trouvée.")
