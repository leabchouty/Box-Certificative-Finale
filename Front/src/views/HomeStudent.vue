<template>
  <div class="home-wrapper">
    <button @click="logout" class="logout-btn">Logout</button>
    <div class="home-box">
      <h1>Bienvenue</h1>
      <p class="welcome-text">Veuillez choisir une action :</p>
      <div class="menu-buttons">
        <router-link to="/form" class="menu-button">Form</router-link>
        <router-link to="/results" class="menu-button">View My Group</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase'; // Assure-toi que ce chemin est correct
import { useRouter } from 'vue-router';

export default {
  name: 'HomeView',
  setup() {
    const router = useRouter();

    const logout = async () => {
      try {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
        router.push('/');
      } catch (error) {
        console.error('Error logging out:', error.message);
      }
    };

    return {
      logout
    };
  }
};
</script>

<style scoped>
.home-wrapper {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(to right, #e3f2fd, #e0f7fa);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative; /* pour positionner le bouton logout */
}

.home-box {
  background: white;
  padding: 60px 80px;
  width: 100%;
  max-width: 800px;
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  text-align: center;
}

h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 20px;
}

.welcome-text {
  font-size: 18px;
  color: #555;
  margin-bottom: 40px;
}

.menu-buttons {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.menu-button {
  padding: 16px 32px;
  font-size: 16px;
  font-weight: bold;
  background-color: #42b983;
  color: white;
  text-decoration: none;
  border-radius: 10px;
  transition: background-color 0.3s ease;
}

.menu-button:hover {
  background-color: #369f77;
}

.logout-btn {
  position: absolute;
  top: 20px;
  right: 20px;

  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  border: 1px solid #dc3545;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  z-index: 10;
}

.logout-btn:hover {
  background: #dc3545;
  color: white;
  transform: translateY(-2px);
}
</style>
