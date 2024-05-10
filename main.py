from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_socketio import SocketIO, emit
import mysql.connector
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
socketio = SocketIO(app)

connection = mysql.connector.connect(
    host='localhost',
    user='admin',
    password='123',
    database='chats',
    port='3306'
)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

# Home page
@app.route('/')
def home():
    return render_template("index.html")

# Sign Up page
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = connection.cursor()
        query = 'INSERT INTO `users` (username, password) VALUES (%s, %s)'
        form_data = (username, password)
        cursor.execute(query, form_data)
        cursor.close()
        connection.commit()
        
        return redirect(url_for('home'))
    return render_template("sign_up.html")

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = connection.cursor()
    query = 'SELECT username, password FROM `users`'
    cursor.execute(query)
    data = cursor.fetchall()
    users = {}
    for row in data:
        username, password = row
        users[username] = {
            'password': password
        }

    cursor.close()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User()
            user.id = username
            login_user(user)
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

# Logout page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('home'))

# Chat-menu page
@app.route('/chat_menu')
@login_required
def chat_menu():
    cursor = connection.cursor()

    query = 'SELECT user_id FROM users WHERE username = %s'
    cursor.execute(query, (session['username'],))
    user_id = cursor.fetchall()[0][0]

    query = '''
    SELECT c.chat_id, c.chat_name FROM 
    chats c JOIN chat_user cu
    ON c.chat_id = cu.chat_id and cu.user_id = %s
    '''
    cursor.execute(query, (user_id,))
    data = cursor.fetchall()
    result = []
    for row in data:
        result.append(dict(zip(cursor.column_names, row)))

    cursor.close()
    return render_template("chat_menu.html", username=session['username'], chat_list=result)


# @app.route('/chat-menu')
# @login_required
# def chat_menu():
#     cursor = connection.cursor()

#     query = 'SELECT user_id FROM users WHERE username = %s'
#     cursor.execute(query, (session['username'],))
#     user_id = cursor.fetchall()[0][0]

#     query = '''
#     SELECT c.chat_id, c.chat_name FROM 
#     chats c JOIN chat_user cu
#     ON c.chat_id = cu.chat_id and cu.user_id = %s
#     '''
#     cursor.execute(query, (user_id,))
#     data = cursor.fetchall()
#     result = []
#     for row in data:
#         result.append(dict(zip(cursor.column_names, row)))

#     cursor.close()
#     return render_template("chat-menu.html", username=session['username'], chat_list=result)

# New chat page
@app.route('/new-chat', methods=['GET', 'POST'])
def new_chat():
    if request.method == 'POST':
        chat_name = request.form['chat_name']
        chat_type = request.form['chat_type']
        cursor = connection.cursor()
        query = 'INSERT INTO `chats` (chat_name, chat_type) VALUES (%s, %s)'
        form_data = (chat_name, chat_type)
        cursor.execute(query, form_data)
        query = '''
        SELECT chat_id FROM `chats` 
        WHERE chat_name = %s
        ORDER BY chat_id DESC
        LIMIT 1
        '''
        cursor.execute(query, (chat_name,))
        chat_id = cursor.fetchall()[0][0]

        query = 'SELECT user_id FROM users WHERE username = %s'
        cursor.execute(query, (session['username'],))
        user_id = cursor.fetchall()[0][0]

        query = 'INSERT INTO `chat_user` (chat_id, user_id, added_time) VALUES (%s, %s, %s)'
        form_data = (chat_id, user_id, datetime.now())
        cursor.execute(query, form_data)
        connection.commit()

        cursor.close()
        
        return redirect(url_for('add_members', chat_id=chat_id))
    return render_template('new_chat.html')

# Add members page
@app.route('/add-members/<chat_id>', methods=['GET', 'POST'])
def add_members(chat_id):
    if request.method == 'POST':
        member_cnt = int(request.form.get('cnt'))

        cursor = connection.cursor()

        for i in range(1,member_cnt+1):
            username = request.form.get(f'member-{i}')

            query = 'SELECT user_id FROM users WHERE username = %s'
            cursor.execute(query, (username,))
            user_id = cursor.fetchall()[0][0]

            query = 'INSERT INTO `chat_user` (chat_id, user_id, added_time) VALUES (%s, %s, %s)'
            form_data = (chat_id, user_id, datetime.now())
            cursor.execute(query, form_data)

        cursor.close()
        connection.commit()
        
        return redirect(url_for('chat_menu'))
    
    cursor = connection.cursor()
    query = 'SELECT chat_name FROM chats WHERE chat_id = %s'
    cursor.execute(query, (chat_id,))
    chat_name = cursor.fetchall()[0][0]
    cursor.close()
    return render_template("add_members.html", chat_id=chat_id)

# New message handler
@socketio.on('new_message')
def handle_new_message(data):
    cursor = connection.cursor()

    query = 'SELECT user_id FROM users WHERE username = %s'
    cursor.execute(query, (session['username'],))
    user_id = cursor.fetchall()[0][0]
    chat_id=data['chat_id']

    query = 'INSERT INTO `messages` (msg_text, user_id, chat_id, sent_time) VALUES (%s, %s, %s, %s)'
    sent_time = datetime.now()
    form_data = (data['message'], user_id, chat_id, sent_time)
    cursor.execute(query, form_data)

    cursor.close()
    connection.commit()

    message = {
        'user_id': user_id, 
        'username': session['username'], 
        'msg_text': data['message'],
        'chat_id': chat_id,
        'sent_time': sent_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    }
    emit('message_added', message, broadcast=True)

# APIs to communicate with DB
@app.route('/api/messages/<chat_id>', methods=['GET'])
@login_required
def get_messages(chat_id):
    cursor = connection.cursor()
    query = '''
    SELECT msgs.msg_text, msgs.chat_id, msgs.sent_time, u.username FROM 
    messages msgs JOIN users u
    ON msgs.user_id = u.user_id
    WHERE msgs.chat_id = %s
    ORDER by msgs.sent_time ASC
    '''
    cursor.execute(query, (chat_id,))
    data = cursor.fetchall()
    result = []
    for row in data:
        result.append(dict(zip(cursor.column_names, row)))

    cursor.close()

    return jsonify(result)

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    cursor = connection.cursor()
    query = 'SELECT user_id, username FROM users WHERE username != %s'
    cursor.execute(query, (session['username'],))
    data = cursor.fetchall()
    result = []
    for row in data:
        result.append(dict(zip(cursor.column_names, row)))

    cursor.close()

    return jsonify(result)


if __name__ == "__main__":
    socketio.run(app, debug=True)