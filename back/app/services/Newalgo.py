from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpBinary, value
import logging


def clustering_algorithm(students_data, preferences_data, n):
    """
    Run the group formation algorithm using real student data from the database.

    Args:
        students_data: List of student objects with id, full_name, mean, alt, present
        preferences_data: List of preference objects with student_id, preferred_id, points
        n: Target group size

    Returns:
        Dict with success status, groups, and satisfaction score
    """
    try:
        logging.info(f"Starting algorithm with {len(students_data)} students and {len(preferences_data)} preferences")
        logging.debug(f"Students data: {students_data}")
        logging.debug(f"Preferences data: {preferences_data}")

        # Validate input data
        if not isinstance(students_data, list):
            raise ValueError("students_data must be a list")
        if not isinstance(preferences_data, list):
            raise ValueError("preferences_data must be a list")
        
        # Filter only present students and ensure they have all required fields
        students = []
        for s in students_data:
            if not isinstance(s, dict):
                logging.error(f"Invalid student data format: {s}")
                continue
            if s.get("present", True):
                if "id" not in s or "full_name" not in s:
                    logging.error(f"Student missing required fields: {s}")
                    continue
                students.append(s)

        if len(students) < n:
            return {
                "success": False,
                "error": f"Not enough present students ({len(students)}) to form groups of size {n}",
            }

        # Convert student data to the format expected by the algorithm
        student_names = []
        student_info = {}
        student_id_to_name = {}
        student_name_to_id = {}
        
        for s in students:
            name = str(s.get("full_name", ""))  # Ensure name is a string
            id_ = str(s.get("id", ""))  # Ensure ID is a string
            if name and id_:
                student_names.append(name)
                student_info[name] = s
                student_id_to_name[id_] = name
                student_name_to_id[name] = id_

        total_students = len(students)
        num_groups = total_students // n
        remainder = total_students % n

        if num_groups == 0:
            return {
                "success": False,
                "error": "Not enough students to form at least one group",
            }

        # Convert preferences from IDs to names with points
        preferences = {}
        for pref in preferences_data:
            if not isinstance(pref, dict):
                logging.error(f"Invalid preference format: {pref}")
                continue
                
            student_id = str(pref.get("student_id", ""))
            preferred_id = str(pref.get("preferred_id", ""))
            points = float(pref.get("points", 0))
            
            if student_id in student_id_to_name and preferred_id in student_id_to_name:
                student_name = student_id_to_name[student_id]
                preferred_name = student_id_to_name[preferred_id]
                
                if student_name not in preferences:
                    preferences[student_name] = {}
                preferences[student_name][preferred_name] = points

        logging.info(f"Processed {len(preferences)} student preferences")
        
        # Assign levels based on mean scores
        for s in students:
            mean = float(s.get("mean", 0) or 0)
            if mean < 10:
                s["level"] = "low"
            elif mean < 14:
                s["level"] = "medium"
            else:
                s["level"] = "high"
            if s["full_name"] in student_info:
                student_info[s["full_name"]]["level"] = s["level"]

        # Create optimization variables
        x = LpVariable.dicts(
            "x",
            ((name, g) for name in student_names for g in range(num_groups)),
            cat=LpBinary,
        )

        # Create z variables only for existing preferences
        z_vars = []
        for i in student_names:
            if i in preferences:
                for j in preferences[i].keys():
                    for g in range(num_groups):
                        z_vars.append((i, j, g))
        
        z = LpVariable.dicts("z", z_vars, cat=LpBinary)

        # Create the optimization problem
        prob = LpProblem("GroupAssignmentWithPreferences", LpMaximize)

        # Objective function: maximize preference satisfaction (weighted by points)
        objective_terms = []
        for i in student_names:
            if i in preferences:
                for j, points in preferences[i].items():
                    for g in range(num_groups):
                        if (i, j, g) in z:
                            objective_terms.append(points * z[i, j, g])
        
        if objective_terms:
            prob += lpSum(objective_terms)
        else:
            logging.warning("No preferences to optimize")

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
        for (i, j, g) in z_vars:
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
                if abs(value(x[i, g]) - 1) < 1e-5:  # Check if value is close to 1
                    student_data = student_info[i]
                    group_members.append(
                        {
                            "id": student_name_to_id[i],
                            "full_name": i,
                            "mean": float(student_data.get("mean", 0) or 0),
                            "alt": bool(student_data.get("alt", False)),
                            "level": str(student_data.get("level", "medium")),
                        }
                    )

            if group_members:
                # Calculate group statistics
                avg_mean = sum(m.get("mean", 0) for m in group_members) / len(group_members)
                alt_count = sum(1 for m in group_members if m.get("alt", False))

                groups.append(
                    {
                        "group_number": g + 1,
                        "members": group_members,
                        "average_mean": float(avg_mean),
                        "alternant_count": int(alt_count),
                    }
                )

        # Calculate satisfaction score based on points
        total_possible = sum(sum(preferences.get(i, {}).values()) for i in student_names)
        total_matched = 0

        for i in student_names:
            if i in preferences:
                for j, points in preferences[i].items():
                    for g in range(num_groups):
                        if abs(value(x[i, g]) - 1) < 1e-5 and abs(value(x[j, g]) - 1) < 1e-5:
                            total_matched += points
                            break

        satisfaction_score = 0
        if total_possible > 0:
            satisfaction_score = round((total_matched / total_possible) * 100, 1)

        logging.info(f"Algorithm completed successfully. Generated {len(groups)} groups with {satisfaction_score}% satisfaction")
        
        return {
            "success": True,
            "groups": groups,
            "satisfaction_score": satisfaction_score,
            "total_students": total_students,
            "num_groups": num_groups,
            "total_matched_preferences": float(total_matched),
            "total_possible_preferences": float(total_possible),
        }

    except Exception as e:
        logging.error(f"Algorithm error: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return {"success": False, "error": f"Algorithm execution failed: {str(e)}"}
