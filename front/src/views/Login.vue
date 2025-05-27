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
        <button type="submit" :disabled="isLoggingIn">Connexion</button>
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
      isLoggingIn: false,
    };
  },
  methods: {
    async handleLogin() {
      this.loginSuccessMessage = '';
      this.loginErrorMessage = '';
      this.isLoggingIn = true;

      try {
        const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
          email: this.username,
          password: this.password,
        });

        if (authError) throw authError;

        if (authData && authData.user) {
          const userId = authData.user.id;
          this.loginSuccessMessage = 'Login successful! Checking your role...';

          // Check if user is a professor
          const { data: professor, error: professorError } = await supabase
            .from('professors') 
            .select('id')    // Check against the 'id' column
            .eq('id', userId) // Use 'id' here
            .single();

          if (professorError && professorError.code !== 'PGRST116') {
            throw professorError;
          }

          if (professor) {
            this.loginSuccessMessage = 'Professor role confirmed. Redirecting to dashboard...';
            this.$router.push('/homeTeacher');
            this.isLoggingIn = false;
            return;
          }

          // If not a professor, check if user is a student
          const { data: student, error: studentError } = await supabase
            .from('students')   
            .select('id')    // Check against the 'id' column
            .eq('id', userId) // Use 'id' here
            .single();
          
          if (studentError && studentError.code !== 'PGRST116') { 
            throw studentError;
          }

          if (student) {
            this.loginSuccessMessage = 'Student role confirmed. Redirecting to dashboard...';
            this.$router.push('/homeStudent'); // Ensure this route exists
            this.isLoggingIn = false;
            return;
          }

          // If user not found in either table
          this.loginErrorMessage = 'Your role could not be determined. Please contact an administrator.';
          await supabase.auth.signOut(); // Log out user as their role is undefined
          
        } else {
          // Should not happen if authError is not thrown, but as a safeguard
          this.loginErrorMessage = 'Login failed. User data not found.';
        }

      } catch (error) {
        console.error('Error during login process:', error.message);
        this.loginErrorMessage = error.message || 'An unexpected error occurred during login.';
      } finally {
        this.isLoggingIn = false;
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

.login-panel button[type="submit"]:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
