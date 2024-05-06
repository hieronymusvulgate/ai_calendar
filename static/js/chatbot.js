function sendMessage() {
    var userInput = document.getElementById("user-input").value;
    document.getElementById("chat-box").innerHTML += "<p class='user-message'><strong>You:</strong> " + userInput.replace(/\n/g, '<br>') + "</p>"; // Also handle input newlines
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Replace \n with <br> in the response text
            var responseWithBreaks = this.responseText.replace(/\n/g, '<br>').replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;');
            document.getElementById("chat-box").innerHTML += "<p class='bot-message'><strong>Lexi:</strong> " + responseWithBreaks + "</p>";
            document.getElementById("user-input").value = "";
            document.getElementById("chat-box").scrollTop = document.getElementById("chat-box").scrollHeight;
        }
    };
    xhttp.open("GET", "/chatbot/get?msg=" + encodeURIComponent(userInput), true);
    xhttp.send();
}
function handleKeyPress(event) {
    if (event.keyCode === 13) { // 13 is the keycode for Enter
        event.preventDefault(); // Prevent the default action to avoid form submission
        sendMessage();
    }
}