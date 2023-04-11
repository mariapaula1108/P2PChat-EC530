import PySimpleGUI as sg
import socket
import threading
import sqlite3

layout = [
    [sg.Frame("Client List", [[sg.Multiline(key="-CLIENTS-", size=(40, 10), disabled=True)]]), sg.Button("Start Chat")],
    [sg.Text("Host: "), sg.Text("0.0.0.0", key="-HOST-"), sg.Text("Port: "), sg.Text("8080", key="-PORT-")]
]

window = sg.Window("P2P Server", layout)

server = None
host_add = "0.0.0.0"
host_port = 8080
client_name = ""
clients = []
clients_names = []


def start_server():
    global server, host_add, host_port
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host_add, host_port))
    server.listen(10)
    window["-HOST-"].update(host_add)
    window["-PORT-"].update(host_port)
    threading._start_new_thread(listen_for_clients, (server, ""))

def listen_for_clients(server, y):
    while True:
        client, addr = server.accept()
        clients.append(client)
        threading._start_new_thread(messaging, (client, addr))

def messaging(client_connection, client_ip_addr):
    global server, client_name, clients
    client_msg = ""
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " 
    client_connection.send(welcome_msg.encode())

    clients_names.append(client_name)
    
    server_msg = f"{client_name} joined the chat."
    for c in clients:
        if c != client_connection:
            c.send(server_msg.encode())

    update_client_names_display(clients_names) 

    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "exit": break

        client_msg = data

        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                server_msg = str(client_msg)
                c.send(server_msg.encode())

    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_client_names_display(clients_names) 

def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx

def update_client_names_display(name_list):
    clients_str = "\n".join(name_list)
    window["-CLIENTS-"].update(clients_str)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Start Chat":
        start_server()

window.close()