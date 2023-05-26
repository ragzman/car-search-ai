function sendMessage(): void {
    const userInput = (document.getElementById("user-input") as HTMLInputElement).value;
    (document.getElementById("user-input") as HTMLInputElement).value = "";

    const messageContainer = document.getElementById("messages");
    if (!messageContainer) {
        console.error("message container not found.")
        return;
    }

    const userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.innerText = userInput;
    messageContainer.appendChild(userMessage);

    // Replace this with your chatbot logic
    const botResponse = "This is the bot's response.";
    const botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    botMessage.innerText = botResponse;
    messageContainer.appendChild(botMessage);
}


let socket;

function initWebSocket() {
    socket = new WebSocket("ws://localhost:8000/chat");

    socket.onopen = function () {
        console.log("WebSocket connection established.");
    };

    socket.onmessage = function (event) {
        const message = JSON.parse(event.data);
        const messageContainer = document.getElementById("messages");
        if (!messageContainer) {
            console.error("message container not found.")
            return;
        }

        if (message.type === "user") {
            const userMessage = document.createElement("div");
            userMessage.className = "user-message";
            userMessage.innerText = message.text;
            messageContainer.appendChild(userMessage);
        } else if (message.type === "bot") {
            const botMessage = document.createElement("div");
            botMessage.className = "bot-message";
            botMessage.innerText = message.text;
            messageContainer.appendChild(botMessage);
        }
    };

    socket.onclose = function () {
        console.log("WebSocket connection closed.");
    };
}
