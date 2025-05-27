<template>
  <div class="home-wrapper">
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
export default {
  name: 'HomeView',
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
</style>
