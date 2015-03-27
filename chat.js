var chatbox = document.getElementById("chatbox"),
	chatInput = document.getElementById("chat-input"),
    chatSocket = new WebSocket("ws://localhost:82/chat");

chatInput.addEventListener('keyup', function(ev) {
	var d = new Date(),
		hour = d.getUTCHours().toString(),
		min = d.getUTCMinutes().toString(),
		time = hour + ':' + min;

	if (ev.which === 13) {
		console.log(time + '::' + chatInput.value);
		chatSocket.send(time + '::' + chatInput.value);
		chatInput.value = ''
	}

}, false);
    
chatSocket.onopen = function(ev) {
    console.log("Socket opened.");
}

chatSocket.onmessage = function(ev) {
	var messEl = document.createElement('div'),
		messElInner = document.createElement('div'),
		timeEl = document.createElement('div');

	messEl.class = 'message';
	messElInner.class = 'inner';

	// Parse message
	var time = ev.data.split('::')[0],
		mess = ev.data.split('::')[1];

	messElInner.textContent = mess;
	timeEl.textContent = time;

	messEl.appendChild(timeEl);
	messEl.appendChild(messElInner);

	chatbox.appendChild(messEl);
}
