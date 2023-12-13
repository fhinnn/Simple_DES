import socketio
import eventlet


sio = socketio.Server()
app = socketio.WSGIApp(sio)

clients = {}

@sio.event
def connect(sid, environ):
    print(f"Client {sid} connected")

@sio.event
def disconnect(sid):
    print(f"Client {sid} disconnected")

    clients.pop(sid, None)

@sio.event
def send_message(sid, data):
    sender_sid = sid
    encrypted_text = data['text']
    recipient_sid = data['recipient_sid']
    encrypted_encryption_key = data['encrypted_encryption_key']
    
    for client_sid, client_info in clients.items():
        if client_sid == recipient_sid:
            sio.emit('receive_message', {'sender_sid': sender_sid, 'encrypted_text': encrypted_text, 'encrypted_encryption_key':encrypted_encryption_key}, room=client_sid)
            break

@sio.event
def set_username(sid, data):
    username = data.get('username')
    public_key = data.get('public_key')
    if username:
        clients[sid] = {'sid': sid, 'username': username, 'public_key': public_key}
        print(f"Client {sid} set username to {username}, public key to {public_key}")

@sio.event
def get_user_list(sid):
    user_list = [{'username': client_info['username'], 'sid': client_info['sid'], 'public_key': client_info['public_key']} for client_sid, client_info in clients.items()]
    user_send = []
    for user in user_list:
        if user['sid'] != sid:
            user_send.append(user)
    sio.emit('user_list', {'users': user_send}, room=sid)

@sio.event
def get_message(sid, data):
    decrypted_text = decrypt(data['text'], data['key'])
    sio.emit('open_message', {'username': data['sender_username'], 'text':decrypted_text}, room=sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 6969)), app)