from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, value
import logging


def run_grouping_algorithm(students_data, preferences_data, n):
    """
    Run the group formation algorithm using real student data from the database.

    Args:
        students_data: List of student objects with id, full_name, mean, alt, present
        preferences_data: Dict mapping student_id to list of preferred_student_ids
        n: Target group size

    Returns:
        Dict with success status, groups, and satisfaction score
    """
    try:
        # Filter only present students
        students = [s for s in students_data if s.get("present", True)]

        if len(students) < n:
            return {
                "success": False,
                "error": f"Not enough present students ({len(students)}) to form groups of size {n}",
            }

        # Convert student data to the format expected by the algorithm
        student_names = [s["full_name"] for s in students]
        student_info = {s["full_name"]: s for s in students}
        student_id_to_name = {s["id"]: s["full_name"] for s in students}
        student_name_to_id = {s["full_name"]: s["id"] for s in students}

        total_students = len(students)
        num_groups = total_students // n
        remainder = total_students % n

        if num_groups == 0:
            return {
                "success": False,
                "error": "Not enough students to form at least one group",
            }

        # Convert preferences from IDs to names
        # changed    
        preferences = {}
        for student_id, scored_prefs in preferences_data.items():
            if student_id in student_id_to_name:
                student_name = student_id_to_name[student_id]
                preferences[student_name] = {}
                for pref_id, score in scored_prefs.items():
                    if pref_id in student_id_to_name:
                        preferences[student_name][student_id_to_name[pref_id]] = score
        # Assign levels based on mean scores
        for s in students:
            mean = s.get("mean", 0) or 0
            if mean < 10:
                s["level"] = "low"
            elif mean < 14:
                s["level"] = "medium"
            else:
                s["level"] = "high"
            student_info[s["full_name"]]["level"] = s["level"]

        # Create optimization variables
        x = LpVariable.dicts(
            "x",
            ((name, g) for name in student_names for g in range(num_groups)),
            cat=LpBinary,
        )
        # changed
        z = LpVariable.dicts(
            "z",
            (
                (i, j, g)
                for i in student_names
                for j in preferences.get(i, [])
                for g in range(num_groups)
            ),
            cat=LpBinary,
        )

        # Create the optimization problem
        prob = LpProblem("GroupAssignmentWithPreferences", LpMaximize)

        # Objective function: maximize preference satisfaction and level distribution
        preference_weight = 5
        level_weights = {"low": 1, "medium": 1, "high": 1}

        # changed
        objective = lpSum(
            preferences[i][j] * z[i, j, g]
            for i in student_names
            for j in preferences.get(i, {}).keys()
            for g in range(num_groups)
        )

        prob += objective

        # Constraint: Each student assigned to exactly one group
        for i in student_names:
            prob += lpSum(x[i, g] for g in range(num_groups)) == 1

        # Constraint: Group sizes (some groups may have n+1 students if remainder > 0)
        for g in range(num_groups):
            if g < remainder:
                prob += lpSum(x[i, g] for i in student_names) == n + 1
            else:
                prob += lpSum(x[i, g] for i in student_names) == n

        # Constraint: Preference satisfaction logic
        for i in student_names:
            for j in preferences.get(i, []):
                for g in range(num_groups):
                    prob += z[i, j, g] <= x[i, g]
                    prob += z[i, j, g] <= x[j, g]
                    prob += z[i, j, g] >= x[i, g] + x[j, g] - 1

        # Solve the problem
        prob.solve()

        if prob.status != 1:  # Not optimal
            return {
                "success": False,
                "error": "No feasible solution found by the optimization algorithm",
            }

        # Extract results
        groups = []
        for g in range(num_groups):
            group_members = []
            for i in student_names:
                if value(x[i, g]) == 1:
                    student_data = student_info[i]
                    group_members.append(
                        {
                            "id": student_name_to_id[i],
                            "full_name": i,
                            "mean": student_data.get("mean", 0),
                            "alt": student_data.get("alt", False),
                            "level": student_data.get("level", "medium"),
                        }
                    )

            if group_members:
                # Calculate group statistics
                avg_mean = sum(m.get("mean", 0) for m in group_members) / len(
                    group_members
                )
                alt_count = sum(1 for m in group_members if m.get("alt", False))

                groups.append(
                    {
                        "group_number": g + 1,
                        "members": group_members,
                        "average_mean": avg_mean,
                        "alternant_count": alt_count,
                    }
                )

        # Calculate satisfaction score
        # changer
        total_possible = sum(
            sum(preferences.get(i, {}).values()) for i in student_names
        )
        total_matched = 0

        for i in student_names:
            for j, score in preferences.get(i, {}).items():
                for g in range(num_groups):
                    if value(x[i, g]) == 1 and value(x[j, g]) == 1:
                        total_matched += score
                        break

        satisfaction_score = 0
        if total_possible > 0:
            satisfaction_score = round((total_matched / total_possible) * 100, 1)

        return {
            "success": True,
            "groups": groups,
            "satisfaction_score": satisfaction_score,
            "total_students": total_students,
            "num_groups": num_groups,
            "total_matched_preferences": total_matched,
            "total_possible_preferences": total_possible,
        }

    except Exception as e:
        logging.error(f"Algorithm error: {str(e)}")
        return {"success": False, "error": f"Algorithm execution failed: {str(e)}"}
