<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { useAuthStore } from "@/stores/auth";

onLaunch(async () => {
  console.log("App Launch");
  
  // 初始化认证 Store
  const authStore = useAuthStore();
  
  // 检查是否已有 token
  const existingToken = authStore.getToken();
  
  if (existingToken) {
    console.log("Token exists, skip silent login");
  } else {
    console.log("No token found, starting silent login...");
    
    // 执行静默登录
    const loginSuccess = await authStore.silentLogin();
    
    if (loginSuccess) {
      console.log("Silent login successful");
      uni.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 1500
      });
    } else {
      console.warn("Silent login failed, user can still use app with limited features");
      // 静默登录失败不阻塞用户使用，只是部分功能可能受限
    }
  }
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
});
</script>

<style>
/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
