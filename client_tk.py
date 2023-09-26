import tkinter as tk
import socket
import json
import threading
my_name = "anon"

# פרטי השרת
server_ip = '127.0.0.1'  # כתובת ה-IP של השרת
server_port = 1082         # פורט השרת

# יצירת חיבור לשרת
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def swap_frames():
    frame1.pack_forget()
    frame2.pack()

# פונקציה שתופעל כאשר הכפתור נלחץ
def when_user_submits_name():
    global my_name
    my_name = entry.get()  # לקבל את הטקסט מהתיבת הטקסט
    client_socket.connect((server_ip, server_port))
    client_socket.send(my_name.encode('utf-8'))
    swap_frames()
    
    recv_thread = threading.Thread(target=recv_msg)
    recv_thread.daemon = True  # הפעלת התהליך ברקע
    # הפעלת הthreads
    recv_thread.start()
    

def recv_msg():
    while True:
        try:
            raw_data = client_socket.recv(1024)
            if raw_data != b'':
                data = raw_data.decode('utf-8')
                print("client got", data)
                _dict = json.loads(data)
                name = _dict["name"]
                msg = _dict["msg"]
                display_message(name, msg)
        except:
            print("")
# פונקציה להצגת הודעות בתיבת הטקסט
def display_message(name, msg):
    formatted_msg = f"{name}: {msg}\n"
    text.config(state="normal")  # הפעל את ה-text widget כדי להוסיף טקסט
    text.insert("end", formatted_msg)  # הוסף את ההודעה ל-text widget
    text.config(state="disabled")  # השבת את ה-text widget למצב "לא ניתן לעריכה"
    text.see(tk.END)  # scroll to end to see the new msg

def when_user_sends():
    msg = entry2.get()  # לקבל את הטקסט מהתיבת הטקסט
    entry2.delete(0, tk.END)  # delete content of input box
    _dict = { "opcode": 1, "msg": msg }
    try:
        client_socket.send(json.dumps(_dict).encode('utf-8'))
    except:
        pass


def show_prompt(question, on_answer):
    """
    מקפיצה חלון עם שאלה
    וכשהיוזר עונה, קוראת לפונקציה
    on_answer
    ושולחת לה את מה שהיוזר הקליד
    """
    def on_ok():
        user_input = entry.get()
        prompt_window.destroy()
        on_answer(user_input)  
    prompt_window = tk.Toplevel(window)
    prompt_window.title("pkuda")
    label = tk.Label(prompt_window, text=question)
    label.pack()
    entry = tk.Entry(prompt_window)
    entry.pack()
    ok_button = tk.Button(prompt_window, text="OK", command=on_ok)
    ok_button.pack()

# יצירת חלון
window = tk.Tk()
window.title("חלון עם תיבת טקסט וכפתור")

# יצירת frame 1
frame1 = tk.Frame(window)
frame1.pack()

# יצירת תווית (label) ב-frame 1 להצגת התוצאה
label = tk.Label(frame1, text="enter name")
label.pack()

# יצירת תיבת טקסט ב-frame 1
entry = tk.Entry(frame1)
entry.pack()

# יצירת כפתור ב-frame 1
button = tk.Button(frame1, text="לחץ עליי", command=when_user_submits_name)
button.pack()

def make_admin(username):
    print("user name to make admin", username)
    _dict = { "target": username, "opcode": 2 }
    client_socket.send(json.dumps(_dict).encode('utf-8'))

def private_msg(username):
    print("user name to sent private msg", username)
    msg = entry2.get()  # לקבל את הטקסט מהתיבת הטקסט
    entry2.delete(0, tk.END)  # delete content of input box
    _dict = { "target": username, "opcode": 5, "msg": msg }
    client_socket.send(json.dumps(_dict).encode('utf-8'))
    
def kick(username):
    print("user name to kick", username)
    _dict = { "target": username, "opcode": 3 }
    client_socket.send(json.dumps(_dict).encode('utf-8'))
    



def onAdminClick():
    show_prompt("who do you want to make an admin?", make_admin)
def onPrivateClick():
    show_prompt("who do you want to sent private msg?", private_msg)
def onKickClick():
    show_prompt("who do you want to kick?", kick)


# יצירת frame 2 (הנראה לאחר הלחיצה על הכפתור)
frame2 = tk.Frame(window)
frame2.pack()


buttonAdmin = tk.Button(frame2, text="give Admin", command=onAdminClick)
buttonAdmin.pack()

buttonPrivate = tk.Button(frame2, text="send private msg", command=onPrivateClick)
buttonPrivate.pack()

buttonKick = tk.Button(frame2, text="kick", command=onKickClick)
buttonKick.pack()
# יצירת תיבת טקסט בת 30 עמודות שאי אפשר להקליד בתוכה
text = tk.Text(frame2, height=30, width=40)
text.config(state="disabled")
text.pack()

# יצירת תיבת טקסט וכפתור שלח צמודים ב-frame 2
entry2 = tk.Entry(frame2)
entry2.pack()
send_button = tk.Button(frame2, text="שלח לכולם", command = when_user_sends)
send_button.pack()

# הרצת התוכנית
window.mainloop()