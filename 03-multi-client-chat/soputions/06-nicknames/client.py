import socket
import threading

HOST = "10.2.1.144"
PORT = 5555


def receive_loop(sock: socket.socket) -> None:
    incoming = sock.makefile("r", encoding="utf-8", newline="\n")
    for line in incoming:
        text = line.rstrip("\n")
        print(f"\n{text}\n> ", end="")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    username = input("name:")
    sock.sendall((username + "\n").encode("utf-8"))

    print("Соединение установлено. Команда /exit — корректный выход.")

    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    while True:
        text = input("> ")
        if text == "/exit":
            sock.close()
            break
        sock.sendall((text + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()