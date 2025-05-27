<template>
  <div class="form-wrapper">
    <div class="form-box">
      <h1>Add Preferences</h1>
      <form @submit.prevent="submitForm">
        <div v-for="(field, index) in fields" :key="index" class="form-row">
          <select v-model="field.name" :disabled="isFormLocked" required>
            <option value="" disabled>Select a classmate</option>
            <option
              v-for="option in getAvailableOptions(index)"
              :key="option"
              :value="option"
            >
              {{ option }}
            </option>
          </select>
        </div>

        

        <button type="submit" :disabled="isFormLocked">Submit</button>
        <button type="button" @click="goBack" class="back-button">Back</button>

        <p v-if="isFormLocked" style="margin-top: 15px; color: #888;">
          Submissions are closed — the deadline has passed.
        </p>
      </form>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase';

export default {
  name: 'FormView',
  data() {
    return {
      fields: [],
      options: [],
      currentUserId: null,
      classmates: [],
      isFormLocked: false, // <- control form access based on deadline
    };
  },
  async mounted() {
    await this.fetchCurrentUserId();
    await this.fetchClassmateNames();
    await this.fetchMAndSetFieldsAndCheckDate();
  },
  methods: {
    async fetchCurrentUserId() {
      const { data: userData, error: userError } = await supabase.auth.getUser();
      if (userError || !userData?.user) {
        console.error('Failed to get current user:', userError?.message || 'No user found');
        return;
      }
      this.currentUserId = userData.user.id;
    },

    async fetchClassmateNames() {
      const { data, error } = await supabase
        .from('students')
        .select('id, full_name');

      if (error) {
        console.error('Error fetching classmates:', error.message);
        return;
      }

      this.classmates = data.filter(student => student.id !== this.currentUserId);
      this.options = this.classmates.map(s => s.full_name);
    },

    async fetchMAndSetFieldsAndCheckDate() {
      const { data, error } = await supabase
        .from('form')
        .select('m, date')
        .single();

      if (error || !data) {
        console.error('Error fetching m/date from form table:', error?.message || 'No form config found');
        return;
      }

      const m = data.m;
      const deadline = new Date(data.date);
      const now = new Date();

      this.isFormLocked = now > deadline;

      this.fields = Array.from({ length: m }, () => ({ name: '' }));
    },

    getAvailableOptions(currentIndex) {
      const selected = this.fields.map(f => f.name).filter((name, i) => name && i !== currentIndex);
      return this.options.filter(name => !selected.includes(name));
    },

    async submitForm() {
      if (this.isFormLocked) return; // extra safety

      const selectedNames = this.fields.map(f => f.name);

      const preferredIds = selectedNames.map(name => {
        const student = this.classmates.find(s => s.full_name === name);
        return student ? student.id : null;
      }).filter(id => id !== null);

      const { error: deleteError } = await supabase
        .from('preferences')
        .delete()
        .eq('student_id', this.currentUserId);

      if (deleteError) {
        console.error('❌ Failed to delete existing preferences:', deleteError.message);
        return;
      }

      const inserts = preferredIds.map(preferred_id => ({
        student_id: this.currentUserId,
        preferred_id,
      }));

      const { error: insertError } = await supabase
        .from('preferences')
        .insert(inserts);

      if (insertError) {
        console.error('❌ Failed to insert preferences:', insertError.message);
      } else {
        console.log('✅ Preferences updated:', inserts);
        alert('Preferences submitted successfully!');
        this.$router.push({ name: 'HomeStudent' });
      }
    },

    goBack() {
      this.$router.back();
    },
  },
};
</script>

<style scoped>
/* same as before */
.form-wrapper {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to right, #fceabb, #f8b500);
}

.form-box {
  background: white;
  padding: 60px 80px;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 800px;
  text-align: center;
}

h1 {
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

select {
  flex: 1;
  padding: 14px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

button {
  padding: 12px 20px;
  border: none;
  background-color: #42b983;
  color: white;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
}

button:hover {
  background-color: #369f77;
}

.checkbox-row {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
  font-size: 16px;
}

.back-button {
  margin-top: 20px;
  background-color: #999;
}

.back-button:hover {
  background-color: #777;
}
</style>
