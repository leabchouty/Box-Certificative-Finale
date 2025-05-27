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

      <button @click="handleGenerateGroups" class="generate-btn" :disabled="isLoading || isGenerating || !students.length">
        {{ isGenerating ? 'Generating Groups...' : 'Generate Groups' }}
      </button>

      <!-- Results Display -->
      <div v-if="generatedGroups && generatedGroups.length" class="results-section">
        <h2>Generated Groups</h2>
        <p class="satisfaction-score">Preference Satisfaction: {{ satisfactionScore }}%</p>
        
        <div class="groups-grid">
          <div v-for="group in generatedGroups" :key="group.group_number" class="group-card">
            <h3>Group {{ group.group_number }}</h3>
            <ul class="group-members">
              <li v-for="member in group.members" :key="member.id" class="member-item">
                <span class="member-name">{{ member.full_name }}</span>
                <span class="member-details">
                  (Mean: {{ member.mean || 'N/A' }}{{ member.alt ? ', Alt' : '' }})
                </span>
              </li>
            </ul>
            <div class="group-stats">
              <small>Avg: {{ group.average_mean?.toFixed(1) || 'N/A' }} | Alt: {{ group.alternant_count || 0 }}</small>
            </div>
          </div>
        </div>

        <!-- Publish Actions -->
        <div class="results-actions">
          <button 
            @click="saveResults(true)" 
            class="publish-btn"
            :disabled="isSaving"
          >
            {{ isSaving ? 'Publishing...' : 'Publish Results' }}
          </button>
        </div>

        <div v-if="saveMessage" class="save-message" :class="{ error: saveError }">
          {{ saveMessage }}
        </div>
      </div>
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
      isGenerating: false,
      generatedGroups: null,
      satisfactionScore: 0,
      isSaving: false,
      saveMessage: '',
      saveError: false,
      currentUser: null,
    };
  },
  methods: {
    // async loadActiveFormConfig() { ... } // Removed this method

    async loadStudents() {
      this.isLoading = true;
      try {
        const { data, error } = await supabase
          .from('students')
          .select('id, full_name, mean, alt, present'); // Load all required fields for the algorithm

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

    async loadStudentPreferences() {
      try {
        const { data, error } = await supabase
          .from('preferences')
          .select('student_id, preferred_id');

        if (error) throw error;

        // Convert array of preferences to object mapping student_id to array of preferred_ids
        const preferences = {};
        data.forEach(pref => {
          if (!preferences[pref.student_id]) {
            preferences[pref.student_id] = [];
          }
          preferences[pref.student_id].push(pref.preferred_id);
        });

        console.log('Preferences loaded:', preferences);
        return preferences;
      } catch (error) {
        console.error('Error loading preferences:', error);
        return {};
      }
    },
    async runGroupingAlgorithm(includedStudents, preferences) {
      try {
        // Call the backend API to run the real PuLP algorithm
        const response = await fetch('http://localhost:5000/api/generate-groups', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            students: includedStudents,
            preferences: preferences,
            n: this.n
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Backend API error');
        }

        const result = await response.json();
        
        if (result.success) {
          return {
            success: true,
            groups: result.groups,
            satisfactionScore: result.satisfaction_score
          };
        } else {
          return { success: false, error: result.error };
        }
      } catch (error) {
        console.error('Algorithm API error:', error);
      }
    },


    async handleGenerateGroups() {
      const includedStudents = this.students.filter(student => student.present);
      
      if (includedStudents.length === 0) {
        alert('No students are included for group generation.');
        return;
      }
      
      if (includedStudents.length < this.n) {
        alert(`Not enough included students (${includedStudents.length}) to form groups of size ${this.n}.`);
        return;
      }

      this.isGenerating = true;
      this.generatedGroups = null;

      try {
        // Load student preferences
        const preferences = await this.loadStudentPreferences();
        
        // Run the algorithm
        const result = await this.runGroupingAlgorithm(includedStudents, preferences);
        
        if (result.success) {
          this.generatedGroups = result.groups;
          this.satisfactionScore = result.satisfactionScore;
          console.log('Groups generated successfully:', this.generatedGroups);
        } else {
          alert('Failed to generate groups: ' + result.error);
        }
      } catch (error) {
        console.error('Error generating groups:', error);
        alert('An error occurred while generating groups.');
      } finally {
        this.isGenerating = false;
      }
    },

    async saveResults(publish = false) {
      if (!this.generatedGroups || !this.generatedGroups.length) {
        alert('No groups to save');
        return;
      }

      this.isSaving = true;
      this.saveMessage = '';
      this.saveError = false;

      try {
        // Get current user (professor) information
        const { data: { user } } = await supabase.auth.getUser();
        
        if (!user) {
          throw new Error('No authenticated user found');
        }

        // Get the active form configuration
        const { data: formData, error: formError } = await supabase
          .from('form')
          .select('id')
          .eq('isopen', true)
          .order('id', { ascending: false })
          .limit(1)
          .single();

        let formId = null;
        if (!formError && formData) {
          formId = formData.id;
        }

        // Prepare the results data
        const resultsData = {
          form_id: formId,
          professor_id: user.id,
          n_value: this.n,
          generated_group_data: {
            groups: this.generatedGroups,
            satisfaction_score: this.satisfactionScore,
            generation_timestamp: new Date().toISOString(),
            total_students: this.generatedGroups.reduce((sum, group) => sum + group.members.length, 0)
          },
          is_published: publish
        };

        // Save to results table
        const { data: savedResult, error: resultError } = await supabase
          .from('results')
          .insert(resultsData)
          .select()
          .single();

        if (resultError) throw resultError;

        // Create groups and group_members records
        await this.createGroupRecords(savedResult.id, user.id);

        this.saveMessage = 'Results published successfully! Students can now view their groups.';
        this.saveError = false;

        // Redirect to results page after successful publish
        setTimeout(() => {
          this.$router.push('/results');
        }, 2000);

      } catch (error) {
        console.error('Error saving results:', error);
        this.saveMessage = `Error saving results: ${error.message}`;
        this.saveError = true;
      } finally {
        this.isSaving = false;
      }
    },

    async createGroupRecords(resultId, professorId) {
      try {
        // Create group records
        for (const group of this.generatedGroups) {
          // Create group record
          const { data: groupRecord, error: groupError } = await supabase
            .from('groups')
            .insert({
              professor_id: professorId,
              is_published: true
            })
            .select()
            .single();

          if (groupError) throw groupError;

          // Create group_members records
          const memberInserts = group.members.map(member => ({
            group_id: groupRecord.id,
            student_id: member.id
          }));

          const { error: membersError } = await supabase
            .from('group_members')
            .insert(memberInserts);

          if (membersError) throw membersError;
        }
      } catch (error) {
        console.error('Error creating group records:', error);
        throw error;
      }
    },
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

/* Results Section */
.results-section {
  width: 100%;
  margin-top: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.results-section h2 {
  color: #333;
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
}

.satisfaction-score {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  color: #42b983;
  margin-bottom: 20px;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.group-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #fafafa;
}

.group-card h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.1rem;
  text-align: center;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 8px;
}

.group-members {
  list-style: none;
  padding: 0;
  margin: 0 0 10px 0;
}

.member-item {
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.member-item:last-child {
  border-bottom: none;
}

.member-name {
  font-weight: 500;
  color: #333;
}

.member-details {
  font-size: 0.85rem;
  color: #666;
  margin-left: 8px;
}

.group-stats {
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
}

.group-stats small {
  color: #777;
  font-size: 0.8rem;
}

/* Results Actions */
.results-actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.publish-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  background-color: #28a745;
  color: white;
}

.publish-btn:hover:not(:disabled) {
  background-color: #218838;
}

.publish-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.save-message {
  text-align: center;
  margin-top: 15px;
  padding: 10px;
  border-radius: 5px;
  font-weight: 500;
}

.save-message:not(.error) {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.save-message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style> 