// Functions
function updateMessages(message) {
    // message = {
    //     'user_id': user_id, 
    //     'username': session['username'], 
    //     'msg_text': data['message'],
    //     'chat_id': chat_id,
    //     'sent_time': sent_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    // }

    var span_item = document.createElement('span');
    span_item.innerHTML = `${message.sent_time}`;
    span_item.classList.add('time_date');

    var p_item = document.createElement('p');
    p_item.innerHTML = `${message.msg_text}`;

    var div_msg, div_msg_container, outer_div_msg;

    if (message.username != username){
        div_msg = document.createElement('div');
        div_msg.classList.add('received_withd_msg');
        div_msg.appendChild(p_item);
        div_msg.appendChild(span_item);

        div_msg_container = document.createElement('div');
        div_msg_container.classList.add('received_msg');
        div_msg_container.appendChild(div_msg);

        var img_item = document.createElement('img');
        img_item.src = 'https://bootdey.com/img/Content/avatar/avatar1.png';
        img_item.alt = `${message.username} avatar`;

        var p_sender_item = document.createElement('p');
        p_sender_item.innerHTML = `${message.username}`;

        var div_sender_item = document.createElement('div');
        div_sender_item.classList.add('incoming_msg_img');
        div_sender_item.appendChild(img_item);
        div_sender_item.appendChild(p_sender_item);

        outer_div_msg = document.createElement('div');
        outer_div_msg.classList.add('incoming_msg');
        outer_div_msg.appendChild(div_sender_item);
        // outer_div_msg.appendChild(div_sender_item);
        outer_div_msg.appendChild(div_msg_container);
    }
    else{
        div_msg = document.createElement('div');
        div_msg.classList.add('sent_msg');
        div_msg.appendChild(p_item);
        div_msg.appendChild(span_item);

        outer_div_msg = document.createElement('div');
        outer_div_msg.classList.add('outgoing_msg');
        outer_div_msg.appendChild(div_msg);
    }
    // message list
    const messageList = document.getElementById('message-list');
    messageList.appendChild(outer_div_msg);

    var chatHistory = document.querySelector(".msg_history");
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function fetchMessages(chat_id) {
    document.getElementById('message-list').innerHTML = '';
    
    fetch(apiMessagesUrl + chat_id)
        .then(response => response.json())
        .then(data => {
            data.forEach(message => {
                updateMessages(message);
            });
        })
        .catch(error => {
            console.error('Error fetching messages:', error);
        });
}

// function showChatHeader(chat_name){
//     document.getElementById('chat-name').innerHTML = chat_name;
//     document.getElementById('chat-header-id').style.visibility = "visible";
// }

function showChatHistory(chat_id){
    document.getElementById('chat-id').innerHTML = chat_id;
    fetchMessages(chat_id);
    document.getElementById('chat-message-id').style.visibility = 'visible';
}

function showChat(chat_id, chat_name){
    //showChatHeader(chat_name);
    showChatHistory(chat_id);
}

// Main
const socket = io();
socket.on('connect', () => {
    console.log('Connected to the server');
});

document.addEventListener('DOMContentLoaded', () => {
    // Event listener for the form submission
    const form = document.getElementById('message-form');
    form.addEventListener('submit', event => {
        event.preventDefault();
        const input = document.getElementById('msg-input');
        const message = input.value;
        input.value = '';

        // Send the message to the server
        const chat_id = document.getElementById('chat-id').innerHTML;
        socket.emit('new_message', {'message': message, 'chat_id': chat_id});
    });

    // Listen for 'message_added' event from the server
    socket.on('message_added', data => {
        updateMessages(data);
    });
});