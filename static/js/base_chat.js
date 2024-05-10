var chatBox = document.getElementById('chat_box');
// Establish WebSocket connection
const socket = io();
socket.on('connect', () => {
    console.log('Connected to the server');
});

function showChatHistory(chat_id){
    document.getElementById('chat_id').innerHTML = chat_id;
    fetchMessages(chat_id);
    chatBox.style.display = 'block';
}

function scrollToBottom() {
    var msgList = document.getElementById("message-list");
    msgList.scrollTop = msgList.scrollHeight;
}

// Function to update the message list
function updateMessages(message) {
    const messageList = document.getElementById('message-list');
    const item = document.createElement('div');
    item.classList.add('item')

    const usernameItem = document.createElement('div');
    usernameItem.classList.add('username-item');

    const messageItem = document.createElement('div');
    messageItem.classList.add('message-item');

    if (message.username == username){
        item.classList.add('own-msg');

        messageItem.textContent = `${message.msg_text}`;
    }
    else{
        item.classList.add('other-msg');

        usernameItem.textContent = `${message.username}`;

        messageItem.textContent = `${message.msg_text}`;
    }
    item.appendChild(usernameItem);
    item.appendChild(messageItem);
    messageList.appendChild(item);
    scrollToBottom();
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

document.addEventListener('DOMContentLoaded', () => {
    chatBox.style.display = 'none';
    const socket = io();

    // Event listener for the form submission
    const form = document.getElementById('message-form');
    form.addEventListener('submit', event => {
        event.preventDefault();
        const input = document.getElementById('message-input');
        const message = input.value;
        input.value = '';

        // Send the message to the server
        const chat_id = document.getElementById('chat_id').innerHTML;
        socket.emit('new_message', {'message': message, 'chat_id': chat_id});
    });

    // Listen for 'message_added' event from the server
    socket.on('message_added', data => {
        updateMessages(data);
    });
});