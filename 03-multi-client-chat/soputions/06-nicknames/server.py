import socket
import threading

HOST = ""
PORT = 5555

clients = dict()
clients_lock = threading.Lock()


def broadcast(text: str, sender) -> None:
    with clients_lock:
        for conn in clients.values():
            if conn is sender:
                continue
            conn.sendall((text + "\n").encode("utf-8"))


def handle_client(conn: socket.socket, addr) -> None:
    incoming = conn.makefile("r", encoding="utf-8", newline="\n")
    try:
        username = next(incoming).rstrip('\n')
    except StopIteration:
        conn.close()
        return
    print(f"Подключился клиент {username}, ({addr})")
    broadcast(f'{username} присоединился к чату', conn)
    with clients_lock:
        clients[username] = conn
    try:
        for line in incoming:
            text = line.rstrip("\n")
            print(f"{addr}: {text}")
            broadcast(f"{username}: {text}", conn)
    except:
        pass
    finally:
        with clients_lock:
            clients.pop(username)
        conn.close()
        print(f"Клиент {username} отключился")
        broadcast(f'{username} вышел из чата', conn)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Сервер слушает {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()