
    var chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/chat/' + roomName + '/');

    chatSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        var timestamp = data['timestamp']
        var username = data['user']

        drawMessage(message, username, timestamp);
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
            'message': message
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

        if (authenticated && (username === "{{ user.username }}" )) {
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