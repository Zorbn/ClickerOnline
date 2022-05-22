const MAX_MONEY = 1000000000

let total = 0;
let totalPrestiges = "?"
let messageBox = document.getElementById("messageBox");
let totalSpan = document.getElementById("total");
let prestigeSpan = document.getElementById("prestige");

let updatePrestige = () => {
    if (total >= MAX_MONEY) {
        prestigeSpan.innerHTML = `<button class="footer-right prestige - button" type="button" onclick="requestPrestige()">🪙 P R E S T I G E 🪙</button>`;
    } else {
        prestigeSpan.innerHTML = `<span class="footer-right">Reach $1 Billion to prestige! (${totalPrestiges})</span>`;
    }
};

let messages = [];

let sendMessage = (text) => {
    messages.push(`&nbsp;&nbsp;&nbsp;${text}<br>`)

    if (messages.length > 4) {
        messages.shift()
    }

    messageBox.innerHTML = "";
    for (const message of messages) {
        messageBox.innerHTML += message;
    }
};

for (let i = 0; i < 3; i++) {
    sendMessage("~");
}

sendMessage(`Welcome!`);

let socket = io();

socket.on("connect", () => {
    requestTotalMoney();
    socket.emit("request_total_producers");
    socket.emit("request_producer_stats");
    socket.emit("request_total_prestiges");
});

socket.on("receive_money", (amount) => {
    total += amount;
    totalSpan.textContent = total;
    sendMessage(`You got $${amount}!`);
    updatePrestige();
});

socket.on("receive_spent_money", (amount) => {
    total -= amount;
    totalSpan.textContent = total;
    sendMessage(`You spent $${amount}!`);
    updatePrestige();
});

socket.on("receive_total_money", (amount) => {
    total = amount;
    totalSpan.textContent = total;
    updatePrestige();
});

socket.on("receive_total_producers", (producers) => {
    Object.keys(producers).forEach(producer => {
        updateProducerCount(producer, producers[producer])
    });
});

socket.on("receive_total_prestiges", (amount) => {
    totalPrestiges = amount;
    updatePrestige();
});

socket.on("receive_producer_stats", (producer_stats) => {
    Object.keys(producer_stats).forEach(producer => {
        let costSpan = document.getElementById(`${producer}-cost`);
        let valueSpan = document.getElementById(`${producer}-value`);
        let delaySpan = document.getElementById(`${producer}-delay`);

        if (costSpan) {
            costSpan.textContent = producer_stats[producer].cost;
        }

        if (valueSpan) {
            valueSpan.textContent = producer_stats[producer].value;
        }

        if (delaySpan) {
            delaySpan.textContent = producer_stats[producer].delay;
        }
    });
});

socket.on("receive_buy_producer", (type, amount) => {
    updateProducerCount(type, amount);
});

let updateProducerCount = (type, amount) => {
    let countSpan = document.getElementById(`${type}-count`);

    if (countSpan) {
        countSpan.textContent = amount;
    }
};

let requestMoney = () => {
    socket.emit("request_money");
};

let requestTotalMoney = () => {
    socket.emit("request_total_money");
};

let requestBuyProducer = (type) => {
    socket.emit("request_buy_producer", type);
};

let requestPrestige = () => {
    socket.emit("request_prestige");
    sendMessage("You prestiged!")
};