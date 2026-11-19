"""Веб-клиент чата: вместо консоли — страница в браузере.

Сервер чата — тот же, что в уроке 4 (python -m server).
Этот сайт подключается к нему как обычный клиент:
  - что пришло от сервера, складываем в список и показываем на странице;
  - что написали в форме, отправляем серверу.
"""

import argparse
import socket
import threading

from flask import Flask, redirect, render_template, request, url_for

from common.config import DEFAULT_HOST, DEFAULT_PORT
from common.protocol import iter_lines, send_line

app = Flask(__name__)

# Подключение к серверу чата — одно на весь сайт, как у консольного клиента.
chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Всё, что прислал сервер. Список читают и меняют разные потоки, поэтому замок (урок 3).
messages = []
lock = threading.Lock()


def receive_loop():
    """Работает в отдельном потоке: всё, что прислал сервер, — в список.

    В уроке 4 здесь был print(), теперь — messages.append().
    """
    try:
        for text in iter_lines(chat):
            with lock:
                messages.append(text)
    except OSError:
        pass  # соединение оборвалось резко (например, сервер «упал»)
    # Сюда попадаем, когда сервер закрыл соединение
    with lock:
        messages.append("*** Соединение с сервером потеряно ***")


@app.route("/")
def index():
    """Главная страница: окно сообщений (iframe) и форма."""
    return render_template("index.html")


@app.route("/messages")
def show_messages():
    """Только список сообщений. Эта страница сама обновляется каждые 2 секунды."""
    with lock:
        shown = list(messages)  # копия: шаблон будет читать её уже без замка
    return render_template("messages.html", messages=shown)


@app.route("/send", methods=["POST"])
def send():
    """Сюда приходит форма. В уроке 4 здесь был input()."""
    text = request.form.get("text", "").strip()
    if text:
        send_line(chat, text)
    # POST → redirect → GET (урок 21): после отправки — снова на главную
    return redirect(url_for("index"))


def main():
    parser = argparse.ArgumentParser(description="Веб-клиент чата")
    parser.add_argument("--host", default=DEFAULT_HOST, help="адрес сервера чата")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="порт сервера чата")
    parser.add_argument("--web-port", type=int, default=5000, help="порт сайта")
    args = parser.parse_args()

    chat.connect((args.host, args.port))
    print(f"Подключились к серверу чата {args.host}:{args.port}")

    threading.Thread(target=receive_loop, daemon=True).start()

    # Без debug=True: в режиме отладки Flask запускает программу дважды
    # (второй раз — чтобы следить за изменениями файлов), и к серверу чата
    # подключились бы два клиента вместо одного.
    app.run(port=args.web_port)


if __name__ == "__main__":
    main()
