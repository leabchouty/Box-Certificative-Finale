<template>
  <div class="form-wrapper">
    <div class="form-box">
      <h1>Add Preferences</h1>
      <form @submit.prevent="submitForm">
        <div v-for="(field, index) in fields" :key="index" class="form-row">
          <select v-model="field.name" required>
            <option value="" disabled>Select a classmate</option>
            <option v-for="option in options" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
          <button type="button" @click="removeField(index)" v-if="fields.length > 1">-</button>
        </div>
        <button type="button" @click="addField">Add classmate</button>

        <div class="checkbox-row">
          <input type="checkbox" id="intern" v-model="isIntern" />
          <label for="intern">I am an intern</label>
        </div>

        <button type="submit">Submit</button>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormView',
  data() {
    return {
      fields: [{ name: '' }],
      options: ["Alice", "Bob", "Charlie", "David", "Eve", "Fay", "Gus", "Hugo", "Ivy", "Jack", "Kim", "Leo", "Mia", "Nina", "Oscar"],
      isIntern: false,
    };
  },
  methods: {
    addField() {
      this.fields.push({ name: '' });
    },
    removeField(index) {
      if (this.fields.length > 1) {
        this.fields.splice(index, 1);
      }
    },
    submitForm() {
      const selectedNames = this.fields.map(f => f.name);
      const internStatus = this.isIntern;
      console.log("Submitted:", selectedNames, "Intern:", internStatus);
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
</style>
