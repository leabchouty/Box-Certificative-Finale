<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Sign In</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Email</label>
          <input type="text" id="username" v-model="username" placeholder="Enter your email" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" placeholder="Enter your password" />
        </div>
        <button type="submit">Login</button>
      </form>
      <p v-if="loginSuccessMessage" class="success-message">{{ loginSuccessMessage }}</p>
      <p v-if="loginErrorMessage" class="error-message">{{ loginErrorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase';

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loginSuccessMessage: '',
      loginErrorMessage: '',
    };
  },
  methods: {
    async handleLogin() {
      this.loginSuccessMessage = '';
      this.loginErrorMessage = '';
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: this.username,
          password: this.password,
        });
        if (error) throw error;
        console.log('User logged in:', data.user);
        this.loginSuccessMessage = 'Login successful! Welcome.';
        // this.$router.push('/dashboard');
      } catch (error) {
        console.error('Error logging in:', error.message);
        this.loginErrorMessage = error.message;
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.login-box {
  background-color: #ffffffdd;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  text-align: center;
  animation: fadeIn 0.6s ease-in-out;
}

.login-box h1 {
  margin-bottom: 25px;
  font-size: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #444;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  transition: border 0.3s;
}

input:focus {
  border-color: #42b983;
  outline: none;
}

button {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #369f77;
}

.success-message {
  color: green;
  margin-top: 15px;
}

.error-message {
  color: red;
  margin-top: 15px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
