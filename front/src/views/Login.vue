<template>
  <div class="login-wrapper">
    <div class="login-box">
      <h1>Se connecter à l'application</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Email</label>
          <input type="text" id="username" v-model="username" placeholder="Entrez votre email" />
        </div>
        <div class="form-group">
          <label for="password">Mot de passe</label>
          <input type="password" id="password" v-model="password" placeholder="Entrez votre mot de passe" />
        </div>
        <button type="submit">Connexion</button>
        <p v-if="loginSuccessMessage" class="success-message">{{ loginSuccessMessage }}</p>
        <p v-if="loginErrorMessage" class="error-message">{{ loginErrorMessage }}</p>
      </form>
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
        this.loginSuccessMessage = 'Connexion réussie. Redirection...';
        setTimeout(() => this.$router.push('/HomeStudent'), 1000);
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
  background: linear-gradient(to right, #e3f2fd, #e0f7fa);
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-box {
  background: white;
  padding: 60px 80px;
  width: 100%;
  max-width: 800px;
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  text-align: center;
}

h1 {
  margin-bottom: 40px;
  font-size: 28px;
  color: #333;
}

.form-group {
  margin-bottom: 25px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 15px;
}

input {
  width: 100%;
  padding: 16px;
  font-size: 16px;
  border-radius: 10px;
  border: 1px solid #ccc;
}

input:focus {
  border-color: #42b983;
  outline: none;
}

button {
  margin-top: 10px;
  width: 100%;
  padding: 16px;
  font-size: 17px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
}

button:hover {
  background-color: #369f77;
}

.success-message {
  margin-top: 20px;
  color: green;
}

.error-message {
  margin-top: 20px;
  color: red;
}
</style>
