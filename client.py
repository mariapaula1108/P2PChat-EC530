import PySimpleGUI as sg
import socket
import threading
import sqlite3


layout = [
    [sg.Text("Name:"), sg.InputText(key="-NAME-"), sg.Button("Connect")],
    [sg.Multiline(key="-CHAT-", size=(50, 20), disabled=True)],
    [sg.InputText(key="-MSG-"), sg.Button("Send"), sg.Button("Exit")]
]

window = sg.Window("Client", layout)

username = ""
client = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) 

        window["-NAME-"].update(disabled=True)
        window["Connect"].update(disabled=True)
        window["-MSG-"].update(disabled=False)

        
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        sg.popup_error("Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


# Function to display chat history
def display_chat_history(name):
    try:
        conn = sqlite3.connect('chat_history.db')
        c = conn.cursor()
        c.execute("SELECT * FROM messages WHERE sender=? OR receiver=?", (name, name))
        chat_history = c.fetchall()
        for row in chat_history:
            sender, receiver, message, timestamp = row
            window["-CHAT-"].print(f"{sender}: {message}")
        conn.close()
    except sqlite3.Error as e:
        print("Error connecting to database:", e)
    except Exception as e:
        print("Error displaying chat history:", e)


def receive_message_from_server(sck, m):
    global username
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server:
            break

        if "joined the chat." in from_server or "left the chat." in from_server:
            # If the message is a user join/leave notification, print it to the chat window
            window["-CHAT-"].print(from_server)
        else:
            # If the message is a regular chat message, save it to the database and print it to the chat window
            save_to_database(username, "All", from_server)
            window["-CHAT-"].print(from_server)

    sck.close()
    window.close()


def save_to_database(sender, receiver, message):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender TEXT NOT NULL,
                 receiver TEXT NOT NULL,
                 message TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);''')
    c.execute('''INSERT INTO messages (sender, receiver, message) 
                 VALUES (?, ?, ?);''', (sender, receiver, message))
    conn.commit()
    conn.close()



while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
       
        if client:
            client.close()
        break

    if event == "Connect":
        if len(values["-NAME-"]) < 1:
            sg.popup_error("Enter your first name")
        else:
            username = values["-NAME-"]
            connect_to_server(username)

    if event == "Send":
        msg = values["-MSG-"].strip()
        if len(msg) > 0:
            if not username:  
                username = values["-NAME-"]
            client.send((f"{username}: {msg}").encode())
            window["-CHAT-"].print(f"Me: {msg}")
            window["-MSG-"].update("")


window.close()