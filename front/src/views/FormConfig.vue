<template>
  <div class="form-config-page">
    <div class="config-container">
      <h1>Configure Student Form</h1>
      <p class="subtitle">Set the parameters and status for the student preference form.</p>

      <!-- Loading state -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading form configuration...</p>
      </div>

      <!-- Form configuration -->
      <form v-else @submit.prevent="handleSaveChanges" class="config-form">
        <div class="form-group publish-toggle-group">
          <label for="isPublishedCheckbox">Form Status:</label>
          <div class="toggle-container">
            <div class="checkbox-wrapper">
              <input 
                type="checkbox" 
                id="isPublishedCheckbox" 
                v-model="formConfig.isPublished" 
                class="standard-checkbox"
                :disabled="isSaving"
                @change="handlePublishToggle"
              >
              <label for="isPublishedCheckbox" class="checkbox-label">
                {{ formConfig.isPublished ? 'Published' : 'Unpublished' }}
              </label>
            </div>
            <div class="status-indicator" :class="{ active: formConfig.isPublished }">
              {{ getFormStatus() }}
            </div>
          </div>
          <small>Manually open or close the form for student submissions.</small>
        </div>

        <div class="form-group">
          <label for="closureDateTime">Auto-Closure Date & Time:</label>
          <input 
            type="datetime-local" 
            id="closureDateTime" 
            v-model="formConfig.closureDateTime" 
            :min="minDateTime"
            :disabled="isSaving"
          >
          <small>
            {{ formConfig.closureDateTime ? 
              `Form will automatically close on ${formatDateTime(formConfig.closureDateTime)}` : 
              'No automatic closure time set' 
            }}
          </small>
        </div>

        <!-- Form statistics if config exists -->
        <div v-if="existingConfig" class="form-stats">
          <h3>Current Form Statistics</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">Student Responses:</span>
              <span class="stat-value">{{ studentResponseCount || 0 }}</span>
            </div>
          </div>
        </div>

        <div class="button-group">
          <button 
            type="submit" 
            class="save-btn"
            :disabled="isSaving || !hasChanges"
          >
            {{ isSaving ? 'Saving...' : (existingConfig ? 'Update Settings' : 'Create Form') }}
          </button>
          
          <button 
            v-if="existingConfig && formConfig.isPublished"
            type="button" 
            class="close-btn"
            @click="confirmCloseForm"
            :disabled="isSaving"
          >
            Close Form Now
          </button>
        </div>
      </form>

      <!-- Status messages -->
      <div v-if="statusMessage" :class="['status-message', { success: isSuccess, error: !isSuccess }]">
        {{ statusMessage }}
      </div>
      
      <router-link to="/homeTeacher" class="back-link">Back to Dashboard</router-link>
    </div>

    <!-- Confirmation dialog -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click="cancelDialog">
      <div class="dialog" @click.stop>
        <h3>Confirm Action</h3>
        <p>{{ confirmMessage }}</p>
        <div class="dialog-buttons">
          <button @click="cancelDialog" class="cancel-btn">Cancel</button>
          <button @click="confirmAction" class="confirm-btn">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase';

export default {
  name: 'FormConfig',
  data() {
    return {
      formConfig: {
        closureDateTime: '',
        isPublished: false,
      },
      originalConfig: null,
      existingConfig: null,
      minDateTime: '',
      statusMessage: '',
      isSuccess: false,
      isLoading: true,
      isSaving: false,
      studentResponseCount: 0,
      showConfirmDialog: false,
      confirmMessage: '',
      confirmCallback: null,
    };
  },
  computed: {
    hasChanges() {
      if (!this.originalConfig) return true; // New config
      
      return (
        this.formConfig.closureDateTime !== this.originalConfig.closureDateTime ||
        this.formConfig.isPublished !== this.originalConfig.isPublished
      );
    }
  },
  methods: {
    async loadExistingConfig() {
      try {
        // Get the most recent form configuration
        const { data: configs, error: configError } = await supabase
          .from('form')
          .select('*')
          .order('id', { ascending: false })
          .limit(1);

        if (configError) throw configError;

        if (configs && configs.length > 0) {
          this.existingConfig = configs[0];
          this.formConfig = {
            closureDateTime: this.existingConfig.date ? 
              new Date(this.existingConfig.date).toISOString().slice(0, 16) : '',
            isPublished: this.existingConfig.isopen,
          };
          
          // Store original config for change detection
          this.originalConfig = { 
            closureDateTime: this.formConfig.closureDateTime,
            isPublished: this.formConfig.isPublished
          };
          
          // Load student response count if form exists
          await this.loadStudentResponseCount();
        } else {
          // No existing config, keep defaults
          this.originalConfig = null;
        }
      } catch (error) {
        console.error('Error loading form configuration:', error);
        this.showError('Failed to load existing form configuration.');
      }
    },

    async loadStudentResponseCount() {
      if (!this.existingConfig) {
        console.log('loadStudentResponseCount: No existingConfig, cannot load count.');
        return;
      }
      
      console.log('loadStudentResponseCount: existingConfig:', JSON.parse(JSON.stringify(this.existingConfig)));
      console.log('loadStudentResponseCount: Querying with form_config_id:', this.existingConfig.id);

      try {
        // Count students who have submitted the form (form_submitted = true)
        const { count, error } = await supabase
          .from('students')
          .select('id', { count: 'exact' })
          .eq('form_submitted', true);

        console.log('loadStudentResponseCount: Supabase response - count:', count, 'error:', error);

        if (error) throw error;
        this.studentResponseCount = count || 0;
      } catch (error) {
        console.error('Error loading response count:', error);
        // Don't show error for this, it's not critical
      }
    },

    async handleSaveChanges() {
      if (!this.hasChanges && this.existingConfig) {
        this.showError('No changes detected.');
        return;
      }

      // Validate closure date if provided
      if (this.formConfig.closureDateTime && new Date(this.formConfig.closureDateTime) <= new Date()) {
        this.showError('Closure date and time must be in the future.');
        return;
      }

      // Show confirmation if there are student responses and we're making significant changes
      if (this.studentResponseCount > 0 && this.hasSignificantChanges()) {
        this.confirmMessage = `This form has ${this.studentResponseCount} student responses. Making changes may affect the results. Are you sure you want to continue?`;
        this.confirmCallback = this.saveConfiguration;
        this.showConfirmDialog = true;
        return;
      }

      await this.saveConfiguration();
    },

    async saveConfiguration() {
      this.isSaving = true;
      this.statusMessage = '';

      try {
        const configData = {
          date: this.formConfig.closureDateTime || null,
          isopen: this.formConfig.isPublished,
        };

        let result;
        if (this.existingConfig) {
          // Update existing configuration
          result = await supabase
            .from('form')
            .update(configData)
            .eq('id', this.existingConfig.id)
            .select()
            .single();
        } else {
          // Create new configuration
          result = await supabase
            .from('form')
            .insert([configData])
            .select()
            .single();
        }

        if (result.error) throw result.error;

        this.existingConfig = result.data;
        this.originalConfig = { ...this.formConfig };
        
        this.showSuccess(this.existingConfig ? 'Form settings updated successfully!' : 'Form created successfully!');
        
        // Reload response count
        await this.loadStudentResponseCount();
        
      } catch (error) {
        console.error('Error saving form configuration:', error);
        this.showError(`Error: ${error.message}`);
      } finally {
        this.isSaving = false;
      }
    },

    handlePublishToggle() {
      if (this.formConfig.isPublished && this.studentResponseCount > 0) {
        // No confirmation needed for publishing, but maybe log it
        console.log('Form published with existing responses');
      }
    },

    confirmCloseForm() {
      this.confirmMessage = `Are you sure you want to close the form immediately? Students will no longer be able to submit responses.`;
      this.confirmCallback = this.closeFormNow;
      this.showConfirmDialog = true;
    },

    async closeFormNow() {
      this.formConfig.isPublished = false;
      await this.saveConfiguration();
    },

    hasSignificantChanges() {
      if (!this.originalConfig) return false;
      return false; // No significant changes since m was removed
    },

    getFormStatus() {
      if (!this.formConfig.isPublished) return 'Form is closed';
      
      if (this.formConfig.closureDateTime) {
        const closeDate = new Date(this.formConfig.closureDateTime);
        const now = new Date();
        
        if (closeDate <= now) {
          return 'Form closed (deadline passed)';
        } else {
          const timeLeft = this.getTimeRemaining(closeDate);
          return `Form open (closes in ${timeLeft})`;
        }
      }
      
      return 'Form is open';
    },

    getTimeRemaining(endDate) {
      const now = new Date();
      const diff = endDate - now;
      
      if (diff <= 0) return '0 minutes';
      
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      
      if (days > 0) return `${days} day${days > 1 ? 's' : ''}, ${hours} hour${hours > 1 ? 's' : ''}`;
      if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''}, ${minutes} minute${minutes > 1 ? 's' : ''}`;
      return `${minutes} minute${minutes > 1 ? 's' : ''}`;
    },

    formatDateTime(dateString) {
      if (!dateString) return 'Not set';
      return new Date(dateString).toLocaleString();
    },

    setMinDateTime() {
      const now = new Date();
      now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
      this.minDateTime = now.toISOString().slice(0, 16);
    },

    showSuccess(message) {
      this.statusMessage = message;
      this.isSuccess = true;
      setTimeout(() => {
        this.statusMessage = '';
      }, 5000);
    },

    showError(message) {
      this.statusMessage = message;
      this.isSuccess = false;
    },

    confirmAction() {
      if (this.confirmCallback) {
        this.confirmCallback();
        this.confirmCallback = null;
      }
      this.showConfirmDialog = false;
    },

    cancelDialog() {
      this.showConfirmDialog = false;
      this.confirmCallback = null;
    }
  },

  async mounted() {
    this.setMinDateTime();
    await this.loadExistingConfig();
    this.isLoading = false;
  }
};
</script>

<style scoped>
.form-config-page {
  min-height: 100vh;
  background-color: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.config-container {
  background: white;
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
}

/* Loading state */
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

/* Form styles */
.config-container h1 {
  text-align: center;
  font-size: 2rem;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 1rem;
}

.config-form .form-group {
  margin-bottom: 25px;
}

.config-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #444;
  font-size: 0.95rem;
}

.config-form input[type="datetime-local"] {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.2s ease-in-out;
}

.config-form input:focus {
  border-color: #42b983;
  outline: none;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

.config-form input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.config-form small {
  display: block;
  margin-top: 6px;
  font-size: 0.85rem;
  color: #777;
}

/* Styles for Checkbox instead of Toggle */
.publish-toggle-group label[for="isPublishedCheckbox"] {
  margin-bottom: 8px;
}

.toggle-container {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.standard-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.standard-checkbox:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.checkbox-label {
  font-weight: normal;
  color: #333;
  font-size: 1rem;
  cursor: pointer;
}

/* Status Indicator remains the same */
.status-indicator {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.status-indicator.active {
  background-color: #d4edda;
  color: #155724;
  border-color: #c3e6cb;
}

/* Form statistics */
.form-stats {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 25px 0;
}

.form-stats h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-weight: 500;
  color: #666;
}

.stat-value {
  font-weight: 600;
  color: #333;
}

/* Buttons */
.button-group {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

.save-btn, .close-btn {
  flex: 1;
  padding: 15px;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.save-btn {
  background-color: #42b983;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background-color: #369f77;
}

.save-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.close-btn {
  background-color: #dc3545;
  color: white;
}

.close-btn:hover:not(:disabled) {
  background-color: #c82333;
}

/* Status messages */
.status-message {
  margin-top: 20px;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.status-message.success {
  background-color: #e6fffa;
  color: #38a169;
  border: 1px solid #a7f3d0;
}

.status-message.error {
  background-color: #fff5f5;
  color: #e53e3e;
  border: 1px solid #feb2b2;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  padding: 30px;
  border-radius: 12px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.dialog h3 {
  margin-bottom: 15px;
  color: #333;
}

.dialog p {
  margin-bottom: 25px;
  color: #666;
  line-height: 1.5;
}

.dialog-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background-color: #5a6268;
}

.confirm-btn {
  background-color: #dc3545;
  color: white;
}

.confirm-btn:hover {
  background-color: #c82333;
}

.back-link {
  display: block;
  text-align: center;
  margin-top: 30px;
  color: #42b983;
  text-decoration: none;
  font-weight: 500;
}

.back-link:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .config-container {
    padding: 30px 25px;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .toggle-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style> 