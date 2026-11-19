"""Веб-клиент чата: вместо консоли — страница в браузере.

Сервер чата — тот же, что в уроке 3 (python server.py).
Этот сайт подключается к нему как обычный клиент (client.py):
  - что пришло от сервера, складываем в список и показываем на странице;
  - что написали в форме, отправляем серверу.
"""

import socket
import threading

from flask import Flask, redirect, render_template, request, url_for

HOST = "127.0.0.1"  # адрес сервера чата
PORT = 5555         # порт сервера чата
WEB_PORT = 5000     # порт нашего сайта

app = Flask(__name__)

# Подключение к серверу чата — одно на весь сайт, как в client.py.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Всё, что прислал сервер. Список читают и меняют разные потоки, поэтому замок.
messages = []
messages_lock = threading.Lock()


def receive_loop():
    """Работает в отдельном потоке: всё, что прислал сервер, — в список.

    В client.py здесь был print(), теперь — messages.append().
    """
    incoming = sock.makefile("r", encoding="utf-8", newline="\n")
    try:
        for line in incoming:
            text = line.rstrip("\n")
            with messages_lock:
                messages.append(text)
    except OSError:
        pass  # соединение оборвалось резко (например, сервер «упал»)
    # Сюда попадаем, когда сервер закрыл соединение
    with messages_lock:
        messages.append("*** Соединение с сервером потеряно ***")


@app.route("/")
def index():
    """Главная страница: окно сообщений (iframe) и форма."""
    return render_template("index.html")


@app.route("/messages")
def show_messages():
    """Только список сообщений. Эта страница сама обновляется каждые 2 секунды."""
    with messages_lock:
        shown = list(messages)  # копия: шаблон будет читать её уже без замка
    return render_template("messages.html", messages=shown)


@app.route("/send", methods=["POST"])
def send():
    """Сюда приходит форма. В client.py здесь был input()."""
    text = request.form.get("text", "").strip()
    if text:
        sock.sendall((text + "\n").encode("utf-8"))
    # POST → redirect → GET (урок 21): после отправки — снова на главную
    return redirect(url_for("index"))


def main():
    sock.connect((HOST, PORT))
    print(f"Подключились к серверу чата {HOST}:{PORT}")

    threading.Thread(target=receive_loop, daemon=True).start()

    # Без debug=True: в режиме отладки Flask запускает программу дважды
    # (второй раз — чтобы следить за изменениями файлов), и к серверу чата
    # подключились бы два клиента вместо одного.
    app.run(port=WEB_PORT)


if __name__ == "__main__":
    main()
