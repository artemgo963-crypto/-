import socket
import threading


HOST = "0.0.0.0"
PORT = 7070


# =========================================================
# ПОДКЛЮЧЕННЫЕ КЛИЕНТЫ
# client -> информация о пользователе
# =========================================================

clients = {}

clients_lock = threading.Lock()


# =========================================================
# ДОСТУПНЫЕ АВАТАРКИ
# =========================================================

AVATARS = {
    "avatar1",
    "avatar2",
    "avatar3",
    "avatar4",
    "avatar5",
    "avatar6",
    "avatar7",
    "avatar8"
}


# =========================================================
# ДОСТУПНЫЕ ЭМОДЗИ
# =========================================================

EMOJIS = {
    "😀",
    "😎",
    "😃",
    "😂",
    "🥳",
    "😈",
    "🤖",
    "👻",
    "🐱",
    "🐶",
    "🦊",
    "🐼",
    "🐸",
    "🦁",
    "🐯",
    "🐵",
    "🍕",
    "🚀",
    "⭐",
    "🔥"
}


# =========================================================
# ОТПРАВКА ВСЕМ КЛИЕНТАМ
# =========================================================

def broadcast(message):

    data = message.encode("utf-8")

    with clients_lock:
        connected_clients = list(clients.keys())

    for client in connected_clients:

        try:
            client.sendall(data)

        except (ConnectionResetError, BrokenPipeError, OSError):

            remove_client(client)


# =========================================================
# ОТПРАВКА СПИСКА ПОЛЬЗОВАТЕЛЕЙ
# =========================================================

def send_users():

    with clients_lock:

        users = []

        for user in clients.values():

            username = user["username"]
            avatar = user["avatar"]
            emoji = user["emoji"]

            users.append(
                f"{username}|{avatar}|{emoji}"
            )

    users_text = ",".join(users)

    broadcast(
        f"USERS|{users_text}"
    )


# =========================================================
# УДАЛЕНИЕ КЛИЕНТА
# =========================================================

def remove_client(client):

    with clients_lock:

        if client not in clients:
            return

        user = clients.pop(client)

    username = user["username"]

    try:
        client.shutdown(socket.SHUT_RDWR)

    except OSError:
        pass

    try:
        client.close()

    except OSError:
        pass

    print(
        f"[-] {username} вышел"
    )

    broadcast(
        f"SYSTEM|{username} вышел из чата"
    )

    send_users()


# =========================================================
# ПРОВЕРКА ДАННЫХ ПОЛЬЗОВАТЕЛЯ
# =========================================================

def validate_user(username, avatar, emoji):

    # Имя

    if not username:
        return False, "Имя пользователя не может быть пустым"

    if len(username) > 30:
        return False, "Имя пользователя слишком длинное"

    # Аватар

    if avatar not in AVATARS:
        return False, "Недопустимый аватар"

    # Эмодзи

    if emoji not in EMOJIS:
        return False, "Недопустимый эмодзи"

    # Проверяем, занято ли имя

    with clients_lock:

        for user in clients.values():

            if user["username"].lower() == username.lower():

                return False, "Это имя пользователя уже занято"

    return True, ""


# =========================================================
# РАБОТА С КЛИЕНТОМ
# =========================================================

def handle_client(client, address):

    print(
        f"[+] Подключение: {address}"
    )

    username = None

    try:

        # -------------------------------------------------
        # ПЕРВОЕ СООБЩЕНИЕ
        # -------------------------------------------------

        data = client.recv(4096)

        if not data:

            client.close()
            return

        message = data.decode(
            "utf-8"
        ).strip()

        print(
            f"[DEBUG] Получено от {address}: {message}"
        )

        # -------------------------------------------------
        # USER|имя|аватар|эмодзи
        # -------------------------------------------------

        parts = message.split("|", 3)

        if len(parts) != 4 or parts[0] != "USER":

            client.sendall(
                "SYSTEM|Неверный формат подключения. Используйте USER|имя|аватар|эмодзи"
                .encode("utf-8")
            )

            client.close()
            return

        username = parts[1].strip()
        avatar = parts[2].strip()
        emoji = parts[3].strip()

        # -------------------------------------------------
        # ПРОВЕРКА
        # -------------------------------------------------

        valid, error = validate_user(
            username,
            avatar,
            emoji
        )

        if not valid:

            client.sendall(
                f"SYSTEM|{error}".encode("utf-8")
            )

            client.close()
            return

        # -------------------------------------------------
        # СОХРАНЯЕМ ПОЛЬЗОВАТЕЛЯ
        # -------------------------------------------------

        with clients_lock:

            clients[client] = {
                "username": username,
                "avatar": avatar,
                "emoji": emoji
            }

        print(
            f"[+] Пользователь: {username}"
        )

        print(
            f"    Аватар: {avatar}"
        )

        print(
            f"    Эмодзи: {emoji}"
        )

        # -------------------------------------------------
        # СООБЩАЕМ О НОВОМ ПОЛЬЗОВАТЕЛЕ
        # -------------------------------------------------

        broadcast(
            f"SYSTEM|{username} присоединился к чату"
        )

        # -------------------------------------------------
        # ОТПРАВЛЯЕМ ОБНОВЛЁННЫЙ СПИСОК
        # -------------------------------------------------

        send_users()

        # -------------------------------------------------
        # ОЖИДАНИЕ СООБЩЕНИЙ
        # -------------------------------------------------

        while True:

            data = client.recv(4096)

            if not data:
                break

            message = data.decode(
                "utf-8"
            ).strip()

            if not message:
                continue

            print(
                f"[{username}] {message}"
            )

            # -------------------------------------------------
            # MSG|имя|текст
            # -------------------------------------------------

            parts = message.split("|", 2)

            if parts[0] == "MSG":

                if len(parts) >= 3:

                    text = parts[2]

                    # Имя берём только с сервера
                    broadcast(
                        f"MSG|{username}|{text}"
                    )

                else:

                    client.sendall(
                        "SYSTEM|Неверный формат сообщения"
                        .encode("utf-8")
                    )

            # -------------------------------------------------
            # CHANGE_PROFILE|аватар|эмодзи
            # -------------------------------------------------

            elif parts[0] == "CHANGE_PROFILE":

                if len(parts) != 3:

                    client.sendall(
                        "SYSTEM|Неверный формат изменения профиля"
                        .encode("utf-8")
                    )

                    continue

                new_avatar = parts[1].strip()
                new_emoji = parts[2].strip()

                # Проверяем новые данные

                if new_avatar not in AVATARS:

                    client.sendall(
                        "SYSTEM|Недопустимый аватар"
                        .encode("utf-8")
                    )

                    continue

                if new_emoji not in EMOJIS:

                    client.sendall(
                        "SYSTEM|Недопустимый эмодзи"
                        .encode("utf-8")
                    )

                    continue

                # Обновляем профиль

                with clients_lock:

                    if client in clients:

                        clients[client]["avatar"] = new_avatar
                        clients[client]["emoji"] = new_emoji

                print(
                    f"[PROFILE] {username}: "
                    f"{new_avatar} {new_emoji}"
                )

                # Отправляем новый список всем

                send_users()

    except ConnectionResetError:

        print(
            f"[-] Соединение сброшено: {address}"
        )

    except ConnectionAbortedError:

        print(
            f"[-] Соединение прервано: {address}"
        )

    except OSError as e:

        print(
            f"[ERROR] Ошибка соединения {address}: {e}"
        )

    except Exception as e:

        print(
            f"[ERROR] {address}: {e}"
        )

    finally:

        remove_client(client)


# =========================================================
# СОЗДАНИЕ СЕРВЕРА
# =========================================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)


# =========================================================
# ПРИВЯЗКА IP + PORT
# =========================================================

try:

    server.bind(
        (HOST, PORT)
    )

except OSError as e:

    print()
    print("======================================")
    print("      ОШИБКА ЗАПУСКА СЕРВЕРА")
    print("======================================")
    print(e)
    print()
    print("Порт 7070 уже используется.")
    print("Закрой старый сервер или измени PORT.")
    print()

    server.close()

    input(
        "Нажмите Enter для выхода..."
    )

    exit()


# =========================================================
# ПРОСЛУШИВАНИЕ
# =========================================================

server.listen(20)


print()
print("======================================")
print("       СЕРВЕР ЧАТА ЗАПУЩЕН")
print("======================================")
print(f"IP:   {HOST}")
print(f"PORT: {PORT}")
print()
print("Аватарки: avatar1 - avatar8")
print("Эмодзи: 20 вариантов")
print()
print("Ожидание подключений...")
print("======================================")


# =========================================================
# ГЛАВНЫЙ ЦИКЛ
# =========================================================

try:

    while True:

        client, address = server.accept()

        print(
            f"[+] Новый клиент: {address}"
        )

        thread = threading.Thread(
            target=handle_client,
            args=(client, address),
            daemon=True
        )

        thread.start()


except KeyboardInterrupt:

    print()
    print("Сервер остановлен.")


except Exception as e:

    print(
        f"[SERVER ERROR] {e}"
    )


finally:

    with clients_lock:

        connected_clients = list(
            clients.keys()
        )

    for client in connected_clients:

        try:
            client.close()

        except OSError:
            pass

    server.close()

    print(
        "Сервер закрыт."
    )