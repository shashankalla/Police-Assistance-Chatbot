document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chatBox");
    const inputField = document.getElementById("userInput");
    const sendButton = document.getElementById("sendBtn");

    const socket = io("http://127.0.0.1:5000"); // Connect WebSocket

    sendButton.addEventListener("click", function () {
        sendMessage();
    });

    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = inputField.value.trim();
        if (userMessage === "") return;

        appendMessage("User", userMessage, "user-message");
        inputField.value = "";

        socket.send(userMessage); // Send message to Flask backend
    }

    socket.on("message", function (data) {
        console.log("Bot response received:", data);
        appendMessage("Bot", data, "bot-message");
    });

    function appendMessage(sender, message, className) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", className);
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
