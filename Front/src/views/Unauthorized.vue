<template>
  <div class="unauthorized-wrapper">
    <div class="unauthorized-box">
      <h1>🚫 Unauthorized</h1>
      <p class="unauthorized-text">You are not allowed to access this page.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UnauthorizedView'
};
</script>

<style scoped>
.unauthorized-wrapper {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(to right, #fdecea, #f9d6d5); 
  display: flex;
  justify-content: center;
  align-items: center;
}

.unauthorized-box {
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
  color: #b00020;
  margin-bottom: 20px;
}

.unauthorized-text {
  font-size: 18px;
  color: #555;
}
</style>
