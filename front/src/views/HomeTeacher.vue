<template>
  <div class="home-teacher">
    <div class="header">
      <h1>Teacher Dashboard</h1>
      <p>Welcome to the Clustering Camarade App</p>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>
    
    <div class="options-container">
      <div class="option-card" @click="navigateToForm">
        <div class="option-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10,9 9,9 8,9"></polyline>
          </svg>
        </div>
        <h3>Access Form</h3>
        <p>Create and manage student information forms for group formation</p>
      </div>
      
      <div class="option-card" @click="navigateToResults">
        <div class="option-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
          </svg>
        </div>
        <h3>Generate Results</h3>
        <p>Generate optimal student groups based on collected data and preferences</p>
      </div>
    </div>
  </div>
</template>

<script>
import { supabase } from '../supabase';

export default {
  name: 'HomeTeacher',
  methods: {
    navigateToForm() {
      // Navigate to the form configuration page
      this.$router.push('/form-config');
    },
    navigateToResults() {
      // Navigate to the results page
      this.$router.push('/results');
    },
    async logout() {
      try {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
        
        // Redirect to login page after logout
        this.$router.push('/login');
      } catch (error) {
        console.error('Error logging out:', error.message);
      }
    }
  }
};
</script>

<style scoped>
.home-teacher {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 60px;
  position: relative;
}

.header h1 {
  font-size: 3rem;
  margin-bottom: 10px;
  font-weight: 300;
}

.header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.logout-btn {
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.options-container {
  display: flex;
  justify-content: center;
  gap: 40px;
  max-width: 1000px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.option-card {
  background: white;
  border-radius: 20px;
  padding: 40px 30px;
  width: 300px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.option-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.option-icon {
  color: #42b983;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.option-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
  font-weight: 600;
}

.option-card p {
  color: #666;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Responsive design */
@media (max-width: 768px) {
  .header h1 {
    font-size: 2rem;
  }
  
  .options-container {
    flex-direction: column;
    align-items: center;
    gap: 30px;
  }
  
  .option-card {
    width: 90%;
    max-width: 350px;
  }
  
  .logout-btn {
    position: static;
    margin-top: 20px;
  }
}
</style> 