<template>
  <div class="results-page">
    <h1>Published Group Results</h1>
    
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading results...</p>
    </div>

    <div v-else-if="!publishedResults.length" class="no-results">
      <p>No published results available yet.</p>
      <router-link :to="userRole === 'teacher' ? '/homeTeacher' : '/homeStudent'" class="back-link">
        Back to Dashboard
      </router-link>
    </div>

    <div v-else class="results-container">
      <!-- Teacher View: Can see all results and manage them -->
      <div v-if="userRole === 'teacher'" class="teacher-results">
        <div class="results-selector">
          <label for="result-select">Select Result Set:</label>
          <select id="result-select" v-model="selectedResultId" @change="loadSelectedResult">
            <option v-for="result in publishedResults" :key="result.id" :value="result.id">
              {{ formatResultTitle(result) }}
            </option>
          </select>
        </div>

                 <div v-if="selectedResult" class="teacher-actions">
           <button @click="unpublishResult" class="unpublish-btn" :disabled="isUpdating">
             {{ isUpdating ? 'Unpublishing...' : 'Unpublish' }}
           </button>
         </div>
      </div>

      <!-- Results Display (for both teachers and students) -->
      <div v-if="selectedResult" class="result-display">
        <div class="result-header">
          <h2>{{ userRole === 'teacher' ? 'Generated Groups' : 'Your Group Assignment' }}</h2>
          <div class="result-info">
            <p><strong>Group Size:</strong> {{ selectedResult.n_value }} members</p>
            <p><strong>Preference Satisfaction:</strong> {{ selectedResult.generated_group_data.satisfaction_score }}%</p>
            <p><strong>Generated:</strong> {{ formatDate(selectedResult.created_at) }}</p>
            <p v-if="selectedResult.professor_name"><strong>Professor:</strong> {{ selectedResult.professor_name }}</p>
          </div>
        </div>

        <!-- Student View: Show only their group -->
        <div v-if="userRole === 'student'" class="student-group-view">
          <div v-if="studentGroup" class="student-group-card">
            <h3>{{ studentGroup.name }}</h3>
            <div class="group-members">
              <h4>Your Group Members:</h4>
              <ul>
                <li v-for="member in studentGroup.members" :key="member.id" 
                    :class="{ 'current-student': member.id === currentUser?.id }">
                  <span class="member-name">{{ member.full_name }}</span>
                  <span v-if="member.id === currentUser?.id" class="you-indicator">(You)</span>
                  <span class="member-details">
                    {{ member.alt ? ' - Alternant' : '' }}
                  </span>
                </li>
              </ul>
            </div>
          </div>
          <div v-else class="no-group">
            <p>You have not been assigned to a group in the current results.</p>
          </div>
        </div>

        <!-- Teacher View: Show all groups -->
        <div v-else class="teacher-groups-view">
          <div class="groups-grid">
            <div v-for="group in selectedResult.generated_group_data.groups" :key="group.group_number" class="group-card">
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
        </div>
      </div>

      <router-link :to="userRole === 'teacher' ? '/homeTeacher' : '/homeStudent'" class="back-link">
        Back to Dashboard
      </router-link>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase';

export default {
  name: 'ResultsView',
  data() {
    return {
      publishedResults: [],
      selectedResult: null,
      selectedResultId: null,
      studentGroup: null,
      currentUser: null,
      userRole: null,
      isLoading: true,
      isUpdating: false,
    };
  },
  methods: {
    async loadPublishedResults() {
      this.isLoading = true;
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          this.$router.push('/login');
          return;
        }

        this.currentUser = user;

        // Determine user role
        const { data: teacherData } = await supabase
          .from('professors')
          .select('id')
          .eq('id', user.id)
          .single();

        this.userRole = teacherData ? 'teacher' : 'student';

        // Load published results with professor information
        const { data, error } = await supabase
          .from('results')
          .select(`
            *,
            professors!results_professor_id_fkey(full_name)
          `)
          .eq('is_published', true)
          .order('created_at', { ascending: false });

        if (error) throw error;

        // Add professor name to results
        this.publishedResults = data.map(result => ({
          ...result,
          professor_name: result.professors?.full_name || 'Unknown'
        }));

        // Auto-select the first result if available
        if (this.publishedResults.length > 0) {
          this.selectedResultId = this.publishedResults[0].id;
          await this.loadSelectedResult();
        }

      } catch (error) {
        console.error('Error loading published results:', error);
      } finally {
        this.isLoading = false;
      }
    },

    async loadSelectedResult() {
      if (!this.selectedResultId) return;

      const result = this.publishedResults.find(r => r.id === this.selectedResultId);
      this.selectedResult = result;

      if (this.userRole === 'student' && result) {
        // Find the student's group
        this.studentGroup = null;
        const groups = result.generated_group_data.groups;
        
        for (const group of groups) {
          if (group.members.some(member => member.id === this.currentUser.id)) {
            this.studentGroup = {
              name: `Group ${group.group_number}`,
              members: group.members
            };
            break;
          }
        }
      }
    },

    formatResultTitle(result) {
      const date = new Date(result.created_at).toLocaleDateString();
      const time = new Date(result.created_at).toLocaleTimeString();
      return `${date} ${time} - ${result.professor_name} (n=${result.n_value})`;
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleString();
    },



    async unpublishResult() {
      if (!this.selectedResult || this.userRole !== 'teacher') return;

      if (!confirm('Are you sure you want to unpublish these results? Students will no longer be able to see them.')) {
        return;
      }

      this.isUpdating = true;
      try {
        const { error } = await supabase
          .from('results')
          .update({ is_published: false })
          .eq('id', this.selectedResult.id);

        if (error) throw error;

        // Remove from published results list
        this.publishedResults = this.publishedResults.filter(r => r.id !== this.selectedResult.id);
        this.selectedResult = null;
        this.selectedResultId = null;

        // Auto-select next result if available
        if (this.publishedResults.length > 0) {
          this.selectedResultId = this.publishedResults[0].id;
          await this.loadSelectedResult();
        }

        alert('Results unpublished successfully.');

      } catch (error) {
        console.error('Error unpublishing results:', error);
        alert('Error unpublishing results.');
      } finally {
        this.isUpdating = false;
      }
    }
  },

  async mounted() {
    await this.loadPublishedResults();
  }
};
</script>

<style scoped>
.results-page {
  padding: 40px;
  background-color: #f4f7f6;
  min-height: 100vh;
  box-sizing: border-box;
}

.results-page h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
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

.no-results {
  text-align: center;
  padding: 60px 20px;
}

.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.results-selector {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.results-selector label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #333;
}

.results-selector select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 1rem;
}

.teacher-actions {
  display: flex;
  margin-bottom: 20px;
  justify-content: center;
}

.unpublish-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
  background-color: #dc3545;
  color: white;
}

.unpublish-btn:hover:not(:disabled) {
  background-color: #c82333;
}

.unpublish-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.result-display {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.result-header {
  margin-bottom: 30px;
  text-align: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

.result-header h2 {
  margin: 0 0 15px 0;
  color: #333;
}

.result-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  text-align: left;
}

.result-info p {
  margin: 5px 0;
  color: #666;
}

/* Student Group View */
.student-group-card {
  background-color: #f8f9fa;
  border: 2px solid #42b983;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.student-group-card h3 {
  color: #42b983;
  margin-top: 0;
}

.student-group-card .group-members ul {
  list-style: none;
  padding: 0;
}

.student-group-card .group-members li {
  padding: 8px 0;
  border-bottom: 1px solid #dee2e6;
}

.student-group-card .group-members li:last-child {
  border-bottom: none;
}

.current-student {
  background-color: #d4edda;
  padding: 8px;
  border-radius: 5px;
  font-weight: 600;
}

.you-indicator {
  color: #28a745;
  font-weight: bold;
}

.no-group {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* Teacher Groups View */
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

.back-link {
  display: inline-block;
  margin-top: 30px;
  padding: 12px 25px;
  background-color: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.back-link:hover {
  background-color: #369f77;
}
</style> 