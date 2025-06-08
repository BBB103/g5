async function fetchcocktails(){
    const response = await fetch("/cocktails");
    const data = await response.json();
    renderCocktailLists(data);
}
function renderCocktailLists(cocktails){
    const container = document.getElementById("cocktail-list");
    container.innerHTML = "";
    for (const id in cocktails) {
        const cocktail = cocktails[id];

        const card = document.createElement("div")
        card.className = "cocktail-card";

        const img = document.createElement("img");
        img.src = `/static/images/${cocktail.image || "default.jpg"}`;
        card.appendChild(img);

        const name = document.createElement("h2");
        name.textContent = cocktail.name;
        card.appendChild(name);

        const desc = document.createElement("p");
        desc.textContent = cocktail.descrption;
        card.appendChild(desc);
        
        const btn = document.createElement("button");
        btn.textContent = "就你了";
        btn.onclick = () => order(cocktail.id || id);
        card.appendChild(btn);

        container.appendChild(card);

    }
}

function order(cocktail_id){
    if (window.socket && window.socket.connected) {
        window.socket.emit("order_cocktail", { cocktail_id: cocktail_id });
    } 
    else {
        alert("not connected!!");
    }
}
