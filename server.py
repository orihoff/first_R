import socket
import select
import json

# פונקציה להתחברות של השרת

server_socket = socket.socket()
server_socket.bind(('127.0.0.1', 1082))
server_socket.listen(5)

def handle_msg(raw_data, current_socket):
    d =json.loads( raw_data.decode())
    print('server got', d)
    if(d["opcode"] == 1):
        # שליחת ההודעה לכל הלקוחות 
        d["name"] = get_name_of(current_socket)
        data = json.dumps(d).encode('utf-8')
        for client in open_client_sockets:
            client.send(data)
    if(d["opcode"] == 5):
        #שליחת הודעה פרטית
        d["name"] = get_name_of(current_socket)
        data = json.dumps(d).encode('utf-8')
        target = d["target"]
        names[target].send(data)
        names[get_name_of(current_socket)].send(data)
        print('sent', data, 'to', names[target].getpeername())
        print('sent', data, 'to', names[get_name_of(current_socket)].getpeername())
    if(d["opcode"] == 3):
        # העפת משתמש
        target = d["target"]
        client_remove = names[target]
        client_remove.close()
        open_client_sockets.remove(client_remove)
        del names[target]
    if(d["opcode"] == 2):
        #מנהל
        target = d["target"]
        socket = names[target] 
        del names[target]
        names["admin_"+ target] = socket

names = {}# מילון של שמות וסוקטים

def get_name_of(socket):
    for name, sock in names.items():
        if sock is socket:
            return name
    return "<unknown>"

# רשימה של חיבורים פעילים
open_client_sockets = []

print("Server is running on port 1082...")

while True:
    rlist, wlist, xlist = select.select(open_client_sockets + [server_socket], [], [])
    for current_socket in rlist:
        # חיבור חדש
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            open_client_sockets.append(new_socket)
            print(f"New connection from {address}")
            name = new_socket.recv(1024).decode('utf-8')
            print(f"שם הלקוח הוא: {name}")
            names[name] = new_socket
        # קריאת הודעה מהלקוח ושליחתו בתגובה לכל הלקוחות האחרים
        else: # existing client
            raw_data = current_socket.recv(1024)
            if not raw_data: # disconnected
                # אין נתונים, החיבור נסגר
                print(f"Connection from {current_socket.getpeername()} closed")
                current_socket.close()
                open_client_sockets.remove(current_socket)
                
            else: # if client sent data
                handle_msg(raw_data, current_socket)