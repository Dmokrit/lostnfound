document.addEventListener("DOMContentLoaded", function () {
    const chatbotWrapper = document.getElementById("chatbotWrapper");
    const chatbotToggle = document.getElementById("chatbotToggle");
    const chatbotMessages = document.getElementById("chatbotMessages");
    const chatbotInput = document.getElementById("chatbotInput");
    const chatbotSend = document.getElementById("chatbotSend");

    // Toggle chatbot visibility
    chatbotToggle.onclick = () => {
        chatbotWrapper.style.transform =
            chatbotWrapper.style.transform === "translateY(0%)"
                ? "translateY(100%)"
                : "translateY(0%)";
    };

    function addMessage(sender, text) {
        const msg = document.createElement("div");
        msg.style.marginBottom = "8px";
        msg.innerHTML = `<b>${sender}:</b> ${text}`;
        chatbotMessages.appendChild(msg);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    async function sendMessage() {
        const message = chatbotInput.value.trim();
        if (!message) return;

        addMessage("You", message);
        chatbotInput.value = "";

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });

            const data = await res.json();

            if (data.reply) {
                addMessage("AI", data.reply);
            } else if (data.error) {
                addMessage("AI", "Error: " + data.error);
            } else {
                addMessage("AI", "No response from server.");
            }
        } catch (err) {
            addMessage("AI", "Connection error.");
        }
    }

    chatbotSend.onclick = sendMessage;
    chatbotInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });
});

