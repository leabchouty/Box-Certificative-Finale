<template>
  <div class="generate-results-page">
    <h1>Generate Student Groups</h1>
    <p>Set group size (n), manage student participation, and generate groups.</p>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading student data...</p>
    </div>

    <div v-else class="content-wrapper">
      <div class="form-group">
        <label for="groupSizeN">Group Size (n):</label>
        <input type="number" id="groupSizeN" v-model.number="n" min="2" :disabled="isLoading" />
        <small>How many members should be in each group?</small>
      </div>

      <div class="student-list-section">
        <h2>Student Participation</h2>
        <p v-if="!students.length && !isLoading">
          No students found in the database, or an error occurred.
        </p>
        
        <ul v-if="students.length" class="student-list">
          <li v-for="student in students" :key="student.id" class="student-item">
            <span class="student-name">{{ student.full_name || student.id || 'Unnamed Student' }}</span>
            <div class="checkbox-wrapper">
              <input 
                type="checkbox" 
                :id="'student_present_' + student.id" 
                v-model="student.present"
                @change="toggleStudentPresence(student)"
                class="present-checkbox"
              >
              <label :for="'student_present_' + student.id" class="checkbox-label">
                {{ student.present ? 'Included' : 'Excluded' }}
              </label>
            </div>
          </li>
        </ul>
      </div>

      <button @click="handleGenerateGroups" class="generate-btn" :disabled="isLoading || !students.length">
        Generate Groups
      </button>
    </div>

    <router-link to="/homeTeacher" class="back-link" v-if="!isLoading">Back to Dashboard</router-link>
  </div>
</template>

<script>
import { supabase } from '../supabase'; // Ensure this path is correct

export default {
  name: 'GenerateResults',
  data() {
    return {
      n: 4, // Default group size
      students: [],
      isLoading: true,
      // activeFormConfig: null, // No longer needed
    };
  },
  methods: {
    // async loadActiveFormConfig() { ... } // Removed this method

    async loadStudents() {
      this.isLoading = true;
      try {
        const { data, error } = await supabase
          .from('students')
          .select('id, full_name, present'); // Ensure id, full_name, and present are selected

        if (error) throw error;

        this.students = data.map(student => ({
          ...student,
          present: student.present === undefined || student.present === null ? true : student.present
        }));
        console.log('Students loaded:', this.students);
      } catch (error) {
        console.error('Error loading students:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async toggleStudentPresence(student) {
      // student.present is already updated by v-model
      try {
        const { error } = await supabase
          .from('students')
          .update({ present: student.present })
          .eq('id', student.id); 

        if (error) throw error;
        console.log(`Student ${student.id} presence updated to ${student.present}`);
      } catch (error) {
        console.error('Error updating student presence:', error);
        student.present = !student.present; // Revert UI on error
        alert('Failed to update student status. Ensure a boolean column named \'present\' exists in your \'students\' table.');
      }
    },
    handleGenerateGroups() {
      const includedStudents = this.students.filter(student => student.present);
      if (includedStudents.length === 0) {
        alert('No students are included for group generation.');
        return;
      }
      if (includedStudents.length < this.n) {
        alert(`Not enough included students (${includedStudents.length}) to form groups of size ${this.n}.`);
        return;
      }
      console.log(`Generating groups with n = ${this.n} for ${includedStudents.length} students:`, includedStudents);
      alert('Group generation logic to be implemented! This will use the list of included students.');
    }
  },
  async mounted() {
    // await this.loadActiveFormConfig(); // Removed this call
    await this.loadStudents(); // Directly load all students
  }
};
</script>

<style scoped>
.generate-results-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  background-color: #f0f2f5;
  min-height: 100vh;
  box-sizing: border-box;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.content-wrapper {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.generate-results-page h1 {
  color: #333;
  margin-bottom: 10px;
}

.generate-results-page > p {
  color: #666;
  margin-bottom: 30px;
  text-align: center;
  max-width: 600px;
}

.form-group {
  margin-bottom: 25px;
  width: 100%;
  max-width: 400px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #444;
}

.form-group input[type="number"] {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
}

.form-group small {
  display: block;
  margin-top: 6px;
  font-size: 0.85rem;
  color: #777;
}

.student-list-section {
  width: 100%;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 30px;
}

.student-list-section h2 {
  color: #333;
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
}

.student-list-section > p { /* For the message when no students are found */
  text-align: center;
  color: #666;
}

.student-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.student-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.student-item:last-child {
  border-bottom: none;
}

.student-name {
  color: #333;
  font-size: 1rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.present-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.9rem;
  color: #555;
  cursor: pointer;
}

.generate-btn {
  background-color: #42b983;
  color: white;
  padding: 15px 30px;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-bottom: 20px;
}

.generate-btn:hover:not(:disabled) {
  background-color: #369f77;
}

.generate-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.back-link {
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
  margin-top: 10px;
}

.back-link:hover {
  text-decoration: underline;
}
</style> 