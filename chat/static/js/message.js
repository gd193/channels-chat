
 document.querySelector('#inbox').onclick = function(e) {
 		var sidebar = document.getElementsByClassName('sidebar')[0];
 		notes = sidebar.children;
 		for (var i=1;i<notes.length;i++){ //0th Element is the default header in the sidebar and not a notification
 			var timestamp = notes[i].getAttribute('timestamp');
 			var len = notes[i].getAttribute('len_time');
 			var str = notes[i].innerHTML;
 			content = str.split("<div")[0];
 			content = content.slice(0, -len);
 			content += timesince(timestamp);
 			notes[i].innerHTML = content + "<div" + str.split("<div")[1] ;
 		}


 		console.log("toggling sidebar");
 		var sidebar = document.querySelector(".sidebar");
 		sidebar.classList.toggle('active');
 		var counter = document.getElementById("notification_counter");
		counter.innerHTML = '';

		  	chatSocket.send(JSON.stringify({
  			'tag' : 'toggling_sidebar',
        }));
    };



    var chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/chat/' + roomName + '/');

    chatSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);

        if (data['type'] === 'message') {
        var message = data['message'];
        var timestamp = data['timestamp']
        var username = data['user']

        drawMessage(message, username, timestamp);
        }

        else if (data['type'] === 'notification') {
            if (!(window.location.href.includes(data['user']))) {
                console.log('notification from ' + data['user']);
                if (document.getElementsByClassName("sidebar active").length === 0) {
                add_Notificationcount();
                }
                drawNotification(data['user'], data['timestamp'], data['key']);
                console.log(data)
        }
        }
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    document.querySelector('#chat-message-input').focus();
    document.querySelector('#chat-message-input').onkeyup = function(e) {
        if (e.keyCode === 13) {  // enter, return
            document.querySelector('#chat-message-submit').click();
        }
    };

    document.querySelector('#chat-message-submit').onclick = function(e) {
        var messageInputDom = document.querySelector('#chat-message-input');
        var message = messageInputDom.value;
        chatSocket.send(JSON.stringify({
            'tag' : 'message',
            'message': message,
        }));

        messageInputDom.value = '';
    };

    function drawMessage(message,username,timestamp) {
        var block_to_insert, container_block, content, author, time , br;

        block_to_insert = document.createElement('div');
        container_block = document.getElementById('event_container');
        author = document.createElement('strong');
        time = document.createElement('span');
        content = document.createElement('p');
        br = document.createElement('br');

        author.innerHTML = username;
        time.innerHTML = timestamp;
        content.innerHTML = message;

        time.setAttribute('class', 'time-right');
        author.setAttribute('class', 'user-left');

        if (authenticated && (username === current_user )) {
            block_to_insert.setAttribute('class', 'container');
        }
        else {
            block_to_insert.setAttribute('class', 'container darker');
        }

        block_to_insert.appendChild(author);
        block_to_insert.appendChild(time);
        block_to_insert.appendChild(br);
        block_to_insert.appendChild(content);

        container_block.insertBefore(block_to_insert, document.getElementById('chat-tool'));



    };

    function drawNotification(username, timestamp, key) {
        var block_to_insert = document.createElement('div');
        var container_block = document.getElementsByClassName('sidebar')[0];
        var cancel = document.createElement('div');
        var delta_t = timesince(timestamp).toLowerCase();


        block_to_insert.setAttribute('class', 'notibox');
        block_to_insert.setAttribute('id', key);
        block_to_insert.setAttribute('timestamp',timestamp);
        block_to_insert.setAttribute('len_time', delta_t.length);
        block_to_insert.setAttribute('author', username);
        block_to_insert.innerHTML = 'You recieved a message by ' + username + ' ' + delta_t;
        cancel.setAttribute('class', 'cancel');
        cancel.setAttribute('onclick', 'cancel_click(this)');
        cancel.innerHTML = 'x';
        container_block.appendChild(block_to_insert);
        document.getElementById('notification_bar').appendChild(cancel);
        block_to_insert.appendChild(cancel);
    }

    function timesince(timestamp) {

        const rtf1 = new Intl.RelativeTimeFormat('en', { style: 'narrow' });
        timestamp += ':00';
        timestamp = '20' + timestamp;
        var time = Date.parse(timestamp)
        var now = Date.now();
        var diff = Math.abs(now - time) - (1000 * 60 * 60);
        if (diff/1000 < 60) {
            return 'Just a Moment ago';
        }
        else if (diff/(1000 * 60) < 60) {
            delta_t = Math.round(diff/(1000*60));
            return rtf1.format(-delta_t, 'minutes');
        }
        else {
        delta_t = Math.round(diff/(1000*60*60));
        return rtf1.format(-delta_t, 'hours');
        }
    }

     function add_Notificationcount() {
       var counter = document.getElementById('notification_counter');
       var n = parseInt(counter.innerHTML);
       if (n) {}
       else { n=0; }
       counter.innerHTML = n+1;
    }