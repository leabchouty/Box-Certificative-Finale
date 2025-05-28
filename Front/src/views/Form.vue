<template>
  <div class="form-wrapper">
    <div class="form-box" v-if="isOpen && !isFormLocked">
      <h1>Assign Points</h1>
      <form @submit.prevent="submitForm">
        <div
          v-for="(field, index) in fields"
          :key="index"
          class="form-row"
        >
          <select
            v-model="field.name"
            :disabled="isFormLocked"
            required
            @input="handleFieldInput(index)"
          >
            <option value="" disabled>Select a classmate</option>
            <option
              v-for="option in getAvailableOptions(index)"
              :key="option"
              :value="option"
            >
              {{ option }}
            </option>
          </select>

          <input
            type="number"
            v-model.number="field.points"
            :disabled="isFormLocked"
            min="0"
            :max="getMaxPoints(index)"
            placeholder="Points"
            @input="handleFieldInput(index)"
          />
        </div>

        <p class="total-warning" v-if="totalPoints > 100">
          ⚠️ Total exceeds 100 points ({{ totalPoints }})!
        </p>

        <p class="total-display">
          Total: {{ totalPoints }} / 100
        </p>

        <button
          type="submit"
          :disabled="isFormLocked || totalPoints !== 100"
        >
          Submit
        </button>
        <button type="button" @click="goBack" class="back-button">Back</button>
      </form>
    </div>

    <!-- Message quand formulaire fermé -->
    <div class="form-box" v-else>
      <p style="color: #888; font-size: 18px; text-align: center;">
        Submissions are closed — either the deadline has passed or the form is not open.
      </p>
      <button type="button" @click="goBack" class="back-button">Back</button>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase';

export default {
  name: 'FormView',
  data() {
    return {
      fields: [{ name: '', points: 0 }],
      options: [],
      currentUserId: null,
      classmates: [],
      isFormLocked: false,
      isOpen: true,
    };
  },
  async mounted() {
    await this.fetchCurrentUserId();
    await this.fetchClassmateNames();
    await this.checkDeadline();
  },
  computed: {
    totalPoints() {
      return this.fields.reduce((sum, field) => sum + (field.points || 0), 0);
    },
  },
  methods: {
    async fetchCurrentUserId() {
      const { data: userData, error } = await supabase.auth.getUser();
      if (error || !userData?.user) {
        console.error('User not found:', error?.message || 'Not logged in');
        return;
      }
      this.currentUserId = userData.user.id;
    },

    async fetchClassmateNames() {
      const { data, error } = await supabase.from('students').select('id, full_name');
      if (error) {
        console.error('Error fetching classmates:', error.message);
        return;
      }
      this.classmates = data.filter(s => s.id !== this.currentUserId);
      this.options = this.classmates.map(s => s.full_name);
    },

    async checkDeadline() {
      const { data, error } = await supabase.from('form').select('date, isopen').single();

      if (error || !data) {
        console.error('Error fetching form config:', error?.message || 'No config found');
        this.isFormLocked = true;
        this.isOpen = false;
        return;
      }

      const deadline = new Date(data.date);
      const now = new Date();

      this.isFormLocked = now > deadline;
      this.isOpen = data.isopen && !this.isFormLocked;
    },

    getAvailableOptions(currentIndex) {
      const selected = this.fields
        .map((f, i) => f.name)
        .filter((name, i) => name && i !== currentIndex);
      return this.options.filter(name => !selected.includes(name));
    },

    getMaxPoints(index) {
      const totalExcludingCurrent = this.fields.reduce((sum, f, i) => {
        return i !== index ? sum + (f.points || 0) : sum;
      }, 0);
      return Math.max(0, 100 - totalExcludingCurrent);
    },

    handleFieldInput(index) {
      const field = this.fields[index];

      if (typeof field.points !== 'number' || isNaN(field.points)) {
        field.points = 0;
        return;
      }

      const max = this.getMaxPoints(index);
      if (field.points > max) {
        field.points = max;
      }

      if (this.totalPoints === 100) {
        this.fields = this.fields.filter(f => f.name && f.points > 0);
        return;
      }

      const isValid = field.name && field.points > 0;
      const isLast = index === this.fields.length - 1;

      if (isValid && isLast && this.totalPoints < 100) {
        this.fields.push({ name: '', points: 0 });
      }
    },

    async submitForm() {
      if (this.isFormLocked || this.totalPoints !== 100) return;

      const submissions = this.fields
        .filter(f => f.name && f.points > 0)
        .map(f => {
          const student = this.classmates.find(s => s.full_name === f.name);
          return {
            student_id: this.currentUserId,
            preferred_id: student?.id,
            points: f.points,
          };
        });

      await supabase
        .from('preferences')
        .delete()
        .eq('student_id', this.currentUserId);

      const { error: insertError } = await supabase.from('preferences').insert(submissions);
      if (insertError) {
        console.error('Error inserting preferences:', insertError.message);
      } else {
        alert('Points submitted successfully!');
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

select,
input[type='number'] {
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
  margin-top: 10px;
}

button:hover {
  background-color: #369f77;
}

.back-button {
  background-color: #999;
  margin-left: 10px;
}

.back-button:hover {
  background-color: #777;
}

.total-warning {
  color: red;
  font-weight: bold;
  margin-bottom: 10px;
}

.total-display {
  margin-top: 10px;
  font-weight: bold;
}
</style>
