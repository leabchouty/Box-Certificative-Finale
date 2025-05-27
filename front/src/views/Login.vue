<template>
  <div class="login">
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <div>
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" />
      </div>
      <button type="submit">Login</button>
    </form>
    <div v-if="loginSuccessMessage" class="success-message">
      {{ loginSuccessMessage }}
    </div>
    <div v-if="loginErrorMessage" class="error-message">
      {{ loginErrorMessage }}
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase'; // Import supabase client

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loginSuccessMessage: '', // Added for success message
      loginErrorMessage: '',   // Added for error message
    };
  },
  methods: {
    async handleLogin() { // Make the method async
      this.loginSuccessMessage = ''; // Reset messages
      this.loginErrorMessage = '';   // Reset messages
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: this.username, // Username is email
          password: this.password,
        });
        if (error) throw error;
        console.log('User logged in:', data.user);
        this.loginSuccessMessage = 'Login successful! Welcome.'; // Set success message
        // We can redirect the user or update the UI here
        // For example, this.$router.push('/dashboard');
      } catch (error) {
        console.error('Error logging in:', error.message);
        this.loginErrorMessage = error.message; // Set error message
      }
    },
  },
};
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  text-align: center;
}
.login h1 {
  margin-bottom: 20px;
}
.login div {
  margin-bottom: 15px;
  text-align: left;
}
.login label {
  display: block;
  margin-bottom: 5px;
}
.login input {
  width: calc(100% - 22px);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
}
.login button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}
.login button:hover {
  background-color: #369f77;
}
.success-message { /* Added style for success message */
  margin-top: 20px;
  padding: 10px;
  color: green;
  border: 1px solid green;
  border-radius: 3px;
}
.error-message { /* Added style for error message */
  margin-top: 20px;
  padding: 10px;
  color: red;
  border: 1px solid red;
  border-radius: 3px;
}
</style> 