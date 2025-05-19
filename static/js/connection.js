function order(cocktail_id) {
    if (window.socket && window.socket.connected) {
        window.socket.emit("order_cocktail", { cocktail_id: cocktail_id });
    } else {
        alert("連線尚未建立，請稍候再試。");
    }
}
