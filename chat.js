(function() {
	var chatbox = document.getElementById("chatbox"),
		chatInput = document.getElementById("chat-input"),
	    chatSocket = new WebSocket("ws://localhost:83/chat"),
		badWordList = {
			'fuck': 'fork',
			'shiti[A-Za-z]+': 'kiddi',
			'shit': 'cool',
			'cunt': 'kitty',
			'bitchi[A-Za-z]+': 'pitching',
			'bitch': 'puppy',
			'faggot': 'fake',
			'whore': 'lore',
			'whori[A-Za-z]': 'boring'
		}

	function convertToLocal(hour,min,sec) {
		var d = new Date(),
			hour, min, period;

		d.setUTCHours(hour);
		d.setUTCMinutes(min);

		hour = d.getHours();
		min = d.getMinutes();

		if (hour < 12) {
			period = 'AM';
		} else {
			period = 'PM';

			if (hour > 12)
				hour = hour - 12;
		}

		if (min < 10) {
			min = '0' + min.toString();
		}

		return [hour, min, sec, period];
	}

	function filterBadWords(words) {
		var filteredWords = words;

		for (var prop in badWordList) {
			if (badWordList.hasOwnProperty(prop)) {
				filteredWords = filteredWords.replace(new RegExp(prop, "g"), badWordList[prop]);
			}
		}

		return filteredWords;
	}

	chatInput.addEventListener('keyup', function(ev) {
		var d = new Date(),
			hour = d.getUTCHours().toString(),
			min = d.getUTCMinutes().toString(),
			sec = d.getUTCSeconds().toString(),
			time = hour + ':' + min + ':' + sec;


		if (ev.which === 13 && chatInput.value.trim() != '') {
			if (sessionStorage['name'] === undefined) {
				sessionStorage['name'] = chatInput.value;
				chatInput.placeholder = "Enter your message.";
			} else {
				chatSocket.send(time + '::' + filterBadWords(sessionStorage['name']) + '::' + filterBadWords(chatInput.value));
			}

			chatInput.value = '';
		}

	}, false);

	chatSocket.onopen = function(ev) {
	    console.log("Socket opened.");
		if (sessionStorage['name'] === undefined) {
			// Ask for name
			chatInput.placeholder = "Enter your name.";
			chatInput.focus();
		}
	}

	chatSocket.onmessage = function(ev) {
		var messEl = document.createElement('div'),
			messElInner = document.createElement('div'),
			nameEl = document.createElement('div'),
			timeEl = document.createElement('div');

			console.log("Recieved message: " + ev.data);
			messEl.className = 'message';
			messElInner.className = 'inner';
			timeEl.className = 'time';
			nameEl.className = 'name';

			// Parse message
			var time = ev.data.split('::')[0],
				name = ev.data.split('::')[1],
				mess = ev.data.split('::')[2],
				localTime = null;

			// Convert UTC time to localtime
			time = time.split(':');
			localTime = convertToLocal(parseInt(time[0]), parseInt(time[1]), parseInt(time[2]));
			time = localTime.slice(0,3).join(':');
			time = time + ' ' + localTime[3];

			messElInner.textContent = mess;
			timeEl.textContent = time;
			nameEl.textContent = name;

			messEl.appendChild(timeEl);
			messEl.appendChild(nameEl);
			messEl.appendChild(messElInner);

			chatbox.appendChild(messEl);

			// Scroll to bottom
			chatbox.scrollTop = chatbox.scrollHeight;
	}

}());
