import bluetooth

def start_bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = 1
    server_sock.bind(("", port))
    server_sock.listen(1)

    print("等待蓝牙连接...")
    client_sock, address = server_sock.accept()
    print(f"已连接到 {address}")
    return server_sock, client_sock

def receive_data(client_sock):
    try:
        data = client_sock.recv(1024)
        if data:
            print(f"收到的数据: {data.decode('utf-8')}")
        return True
    except bluetooth.btcommon.BluetoothError:
        return False

def main():
    server_sock = None
    client_sock = None

    while True:
        if server_sock is None or client_sock is None:
            if server_sock:
                server_sock.close()
            server_sock, client_sock = start_bluetooth_server()

        if client_sock and receive_data(client_sock):
            pass
        else:
            print("连接丢失，等待重新连接...")
            if client_sock:
                client_sock.close()
            client_sock = None
            server_sock.close()
            server_sock = None

if __name__ == "__main__":
    main()