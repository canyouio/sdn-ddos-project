<template>
  <div class="sidebar">
    <h2>SDN Monitor</h2>
    <nav>
      <ul>
        <li><router-link to="/">仪表盘</router-link></li>
        <li><router-link to="/lists">黑白名单</router-link></li>
      </ul>
    </nav>
  </div>
  <div class="main-content">
    <router-view/>
  </div>
</template>
