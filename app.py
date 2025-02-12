from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, ChatMessage
from config import Config
from datetime import datetime, timezone
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)

# Cấu hình SocketIO với async_mode='threading'
socketio = SocketIO(app, 
                   async_mode='threading',
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.status = 'ONLINE'
            user.last_seen = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    current_user.status = 'OFFLINE'
    current_user.last_seen = datetime.now(timezone.utc)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)
    return render_template('chat.html', other_user=other_user)

@app.route('/api/messages/<int:user_id>')
@login_required
def get_messages(user_id):
    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == user_id)) |
        ((ChatMessage.sender_id == user_id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return jsonify([{
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'timestamp': msg.timestamp.isoformat(),
        'is_read': msg.is_read
    } for msg in messages])

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room(str(current_user.id))
        current_user.status = 'ONLINE'
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        emit('user_status', {
            'user_id': current_user.id,
            'status': 'ONLINE'
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(str(current_user.id))
        current_user.status = 'OFFLINE'
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        emit('user_status', {
            'user_id': current_user.id,
            'status': 'OFFLINE'
        }, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    if not current_user.is_authenticated:
        return
    
    try:
        # Tạo timestamp
        timestamp = datetime.now(timezone.utc)
        
        # Thực thi stored procedure với text()
        result = db.session.execute(
            text("EXEC InsertChatMessage :content, :sender_id, :receiver_id, :type, :timestamp, :is_read"),
            {
                'content': data['content'],
                'sender_id': current_user.id,
                'receiver_id': int(data['receiver_id']),
                'type': 'TEXT',
                'timestamp': timestamp,
                'is_read': False
            }
        )
        
        # Lấy ID của tin nhắn mới
        message_id = result.scalar()
        
        message_data = {
            'id': message_id,
            'content': data['content'],
            'sender_id': current_user.id,
            'receiver_id': int(data['receiver_id']),
            'timestamp': timestamp.isoformat(),
            'is_read': False,
            'sender_name': current_user.full_name
        }
        
        # Commit transaction
        db.session.commit()
        
        # Gửi tin nhắn tới cả người gửi và người nhận
        emit('new_message', message_data, room=str(current_user.id))
        emit('new_message', message_data, room=str(data['receiver_id']))
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        db.session.rollback()
        emit('message_error', {'error': 'Failed to send message'}, room=str(current_user.id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(
            username=username,
            full_name=full_name,
            status='OFFLINE'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/test_db')
def test_db():
    try:
        users = User.query.all()
        return f"Connected successfully! Found {len(users)} users."
    except Exception as e:
        return f"Connection error: {str(e)}"

if __name__ == '__main__':
    socketio.run(app, 
                debug=True,
                host='0.0.0.0',
                port=5001,
                use_reloader=True,
                allow_unsafe_werkzeug=True) 