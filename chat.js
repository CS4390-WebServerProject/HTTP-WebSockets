var chatbox = document.getElementById("chatbox"),
    chatSocket = new WebSocket("ws://udkk0c9e7def.devsyed.koding.io:9999");
    
chatSocket.onopen = function(ev) {
    console.log("Socket opened.");
}

chatSocket.onmessage = function(ev) {
    console.log(ev.data);
}