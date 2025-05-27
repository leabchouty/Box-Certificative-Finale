<template>
  <div class="login-wrapper">
    <div class="login-panel">
      <div class="login-left">
        <h1>Welcome Back</h1>
        <p>Please enter your credentials to access your account.</p>
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
      <div class="login-right">
        <h2>Clustering Camarade App</h2>
        <p>Group optimization and affinity-based student matching. Smart. Simple. Efficient.</p>
      </div>
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
        this.loginSuccessMessage = 'Login successful! Welcome.';
      } catch (error) {
        this.loginErrorMessage = error.message;
      }
    },
  },
};
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(to right, #ece9e6, #ffffff);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-panel {
  display: flex;
  width: 90%;
  max-width: 1200px;
  height: 80vh;
  background: white;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  overflow: hidden;
}

.login-left,
.login-right {
  width: 50%;
  padding: 60px;
}

.login-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-left h1 {
  font-size: 32px;
  margin-bottom: 10px;
  color: #222;
}

.login-left p {
  margin-bottom: 30px;
  color: #555;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

input {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

input:focus {
  border-color: #42b983;
  outline: none;
}

button {
  padding: 14px;
  width: 100%;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
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

.login-right {
  background: #42b983;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.login-right h2 {
  font-size: 28px;
  margin-bottom: 20px;
}

.login-right p {
  font-size: 16px;
  padding: 0 20px;
}
</style>
