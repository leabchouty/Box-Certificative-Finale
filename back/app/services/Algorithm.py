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
]


# Number of groups (user-defined or provided)
n = 4

# Preferences collected from student form (max m per student)
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
}


student_names = [s["name"] for s in students]
student_info = {s["name"]: s for s in students}
total_students = len(students)

# Check feasibility
if total_students % n != 0:
    raise ValueError("Total students must be divisible by the number of groups.")

group_size = total_students // n

# Assign level
for s in students:
    if s["mean"] < 10:
        s["level"] = "low"
    elif s["mean"] < 14:
        s["level"] = "medium"
    else:
        s["level"] = "high"

# Define LP variables
x = LpVariable.dicts(
    "x", ((i, g) for i in student_names for g in range(n)), cat=LpBinary
)
z = LpVariable.dicts(
    "z",
    (
        (i, j, g)
        for i in student_names
        for j in preferences.get(i, [])
        for g in range(n)
    ),
    cat=LpBinary,
)

# Build problem
prob = LpProblem("GroupAssignmentWithPreferences", LpMaximize)

# Objective: maximize satisfied preferences and balanced levels
prob += (
    5
    * lpSum(
        z[i, j, g]
        for i in student_names
        for j in preferences.get(i, [])
        for g in range(n)
    )
    + 1
    * lpSum(
        x[i, g]
        for i in student_names
        for g in range(n)
        if student_info[i]["level"] == "low"
    )
    + 1
    * lpSum(
        x[i, g]
        for i in student_names
        for g in range(n)
        if student_info[i]["level"] == "medium"
    )
    + 1
    * lpSum(
        x[i, g]
        for i in student_names
        for g in range(n)
        if student_info[i]["level"] == "high"
    )
)

# Constraints
# One group per student
for i in student_names:
    prob += lpSum(x[i, g] for g in range(n)) == 1


##
# Fixed group size
for g in range(n):
    prob += lpSum(x[i, g] for i in student_names) == group_size

# Define z[i,j,g] = 1 if i and j are in the same group
for i in student_names:
    for j in preferences.get(i, []):
        for g in range(n):
            prob += z[i, j, g] <= x[i, g]
            prob += z[i, j, g] <= x[j, g]
            prob += z[i, j, g] >= x[i, g] + x[j, g] - 1

# After solving
prob.solve()

# Score basé sur le nombre total de personnes préférées effectivement présentes
total_possible = 0
total_matched = 0

for i in student_names:
    prefs = preferences.get(i, [])
    total_possible += len(prefs)
    for j in prefs:
        for g in range(n):
            if value(x[i, g]) == 1 and value(x[j, g]) == 1:
                total_matched += 1
                break  # Ne compte qu'une fois


# Affichage résultat
if prob.status == 1:
    print(
        f"\n✅ Successful distribution into {n} groups of {group_size} students each:\n"
    )
    for g in range(n):
        print(f"🧩 Group {g+1}:")
        for i in student_names:
            if value(x[i, g]) == 1:
                s = student_info[i]
                print(
                    f" - {i} (mean={s['mean']}, level={s['level']}, alternant={s['alt']})"
                )
        print()

    # Affichage
    if total_possible > 0:
        score_pct = (total_matched / total_possible) * 100
        print(
            f"📊 Satisfaction score: {total_matched}/{total_possible} preferences respected ({score_pct:.1f}%)"
        )
    else:
        print("📊 Satisfaction score: No preferences expressed.")

else:
    print("\n❌ No feasible solution found.")
