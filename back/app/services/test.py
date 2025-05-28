import unittest
from Newalgo import clustering_algorithm

class TestClusteringAlgorithm(unittest.TestCase):

    def setUp(self):
        # Sample student data and preferences for use in multiple tests
        self.students_data = [
            {"id": "1", "full_name": "Alice", "mean": 13, "alt": False, "present": True},
            {"id": "2", "full_name": "Bob", "mean": 11, "alt": True, "present": True},
            {"id": "3", "full_name": "Charlie", "mean": 9, "alt": False, "present": True},
            {"id": "4", "full_name": "David", "mean": 15, "alt": False, "present": True},
        ]
        self.preferences_data = [
            {"student_id": "1", "preferred_id": "2", "points": 10},
            {"student_id": "2", "preferred_id": "3", "points": 5},
            {"student_id": "3", "preferred_id": "1", "points": 2},
        ]

    def test_successful_grouping(self):
        # Verify successful grouping and correct group count
        result = clustering_algorithm(self.students_data, self.preferences_data, n=2)
        self.assertTrue(result["success"])
        self.assertEqual(result["num_groups"], 2)
        self.assertEqual(result["total_students"], 4)

    def test_not_enough_students(self):
        # Should fail due to insufficient students to form even one group
        students = self.students_data[:1]
        result = clustering_algorithm(students, self.preferences_data, n=2)
        self.assertFalse(result["success"])
        self.assertIn("error", result)


    def test_missing_fields_in_students(self):
        # Students missing required fields should be ignored, causing the algorithm to fail
        faulty_students = [{"full_name": "Test", "mean": 12, "alt": False, "present": True}]
        result = clustering_algorithm(faulty_students, self.preferences_data, n=2)
        self.assertFalse(result["success"])

    def test_students_not_present(self):
        # All students marked as not present → no valid input for grouping
        absent_students = [{"id": "1", "full_name": "Absent", "mean": 12, "alt": False, "present": False}]
        result = clustering_algorithm(absent_students, self.preferences_data, n=2)
        self.assertFalse(result["success"])

    def test_preference_points_calculation(self):
        # Satisfaction score should be in valid range: [0, 100]
        result = clustering_algorithm(self.students_data, self.preferences_data, n=2)
        self.assertGreaterEqual(result["satisfaction_score"], 0)
        self.assertLessEqual(result["satisfaction_score"], 100)

    def test_odd_number_of_students(self):
        # Test handling of uneven group sizes (due to remainder)
        self.students_data.append({"id": "5", "full_name": "Eve", "mean": 10, "alt": True, "present": True})
        result = clustering_algorithm(self.students_data, self.preferences_data, n=2)
        self.assertTrue(result["success"])
        self.assertEqual(result["total_students"], 5)
        self.assertEqual(result["num_groups"], 2)

    def test_group_size_constraint(self):
        # Groups should have either n or n+1 members depending on remainder
        result = clustering_algorithm(self.students_data, self.preferences_data, n=2)
        group_sizes = [len(group["members"]) for group in result["groups"]]
        self.assertTrue(all(s in (2, 3) for s in group_sizes))

    def test_fallback_on_invalid_preference(self):
        # Preferences pointing to invalid student IDs should be ignored without crashing
        faulty_prefs = [
            {"student_id": "1", "preferred_id": "999", "points": 10}
        ]
        result = clustering_algorithm(self.students_data, faulty_prefs, n=2)
        self.assertTrue(result["success"])
        self.assertEqual(result["satisfaction_score"], 0)

if __name__ == '__main__':
    unittest.main()
