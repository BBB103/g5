let socket;
window.onload = () => {
  fetchcocktails();
  
  try {
    if (typeof io !== 'undefined') {
      socket = io();
      setupSocketListeners();
      console.log("Socket.IO 連接成功初始化");
      
    } else {
      console.error("Socket.IO 客戶端庫未加載，請確認是否在 HTML 中引入了 socket.io.js");
    }
  } catch (error) {
    console.error("Socket.IO 初始化失敗:", error);
  }
};

function order(cocktailId) {
  if (socket && socket.connected) {
    socket.emit("order_cocktail", { cocktail_id: cocktailId });
    console.log("訂單已送出:", cocktailId);
  } else {
    console.error("Socket 未連線，無法送出訂單");
    alert("網路連接問題");
  }
}

function setupSocketListeners() {
  socket.on("connect", () => {
    console.log("Socket.IO 已連接到伺服器");
  });
  
  socket.on("connect_error", (error) => {
    console.error("Socket.IO 連接錯誤:", error);
  });
  
  socket.on("order_received", (data) => {
    console.log("收到訂單確認：", data);
  });
  
  socket.on("status_update", (status) => {
    console.log("目前狀態：", status);
    let progress = document.getElementById("progress-value");
    progress.innerText = status.progress;
  });
  
  socket.on("cocktail_ready", (data) => {
    console.log("你的雞尾酒好了！", data);
    alert(`你的 ${data.cocktail_id} 調好了！`);
  });
  
  socket.on("error", (err) => {
    console.error("錯誤訊息：", err.message);
    alert(err.message);
  });
}

