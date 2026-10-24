import socket
import threading
import tkinter as tk
from tkinter import messagebox


SERVER_IP = "127.0.0.1"
SERVER_PORT = 7070


AVATARS = [
    "avatar1",
    "avatar2",
    "avatar3",
    "avatar4",
    "avatar5",
    "avatar6",
    "avatar7",
    "avatar8"
]


EMOJIS = [
    "😀", "😎", "😃", "😂", "🥳",
    "😈", "🤖", "👻", "🐱", "🐶",
    "🦊", "🐼", "🐸", "🦁", "🐯",
    "🐵", "🍕", "🚀", "⭐", "🔥"
]


client = None
username = ""
selected_avatar = "avatar1"
selected_emoji = "😀"
connected = False


BG = "#202124"
PANEL = "#292a2d"
CHAT_BG = "#18191b"
TEXT = "#ffffff"
ACCENT = "#5865f2"


root = tk.Tk()
root.title("Мій чат")
root.geometry("900x600")
root.minsize(700, 500)
root.configure(bg=BG)


# =========================================================
# ВІКНО ВХОДУ
# =========================================================

login_frame = tk.Frame(
    root,
    bg=BG
)

login_frame.pack(
    fill="both",
    expand=True
)


tk.Label(
    login_frame,
    text="Ласкаво просимо до чату",
    font=("Arial", 24, "bold"),
    fg=TEXT,
    bg=BG
).pack(pady=(50, 30))


tk.Label(
    login_frame,
    text="Ім'я користувача",
    font=("Arial", 12),
    fg=TEXT,
    bg=BG
).pack()


name_entry = tk.Entry(
    login_frame,
    font=("Arial", 14),
    width=25,
    justify="center"
)

name_entry.pack(pady=10)


# =========================================================
# АВАТАР
# =========================================================

tk.Label(
    login_frame,
    text="Оберіть аватар",
    font=("Arial", 12),
    fg=TEXT,
    bg=BG
).pack(pady=(15, 5))


avatar_var = tk.StringVar(
    value="avatar1"
)


avatar_menu = tk.OptionMenu(
    login_frame,
    avatar_var,
    *AVATARS
)

avatar_menu.config(
    width=18,
    font=("Arial", 11)
)

avatar_menu.pack()


# =========================================================
# ЕМОДЗІ
# =========================================================

tk.Label(
    login_frame,
    text="Оберіть емодзі",
    font=("Arial", 12),
    fg=TEXT,
    bg=BG
).pack(pady=(15, 5))


emoji_var = tk.StringVar(
    value="😀"
)


emoji_frame = tk.Frame(
    login_frame,
    bg=BG
)

emoji_frame.pack()


emoji_buttons = []


def select_emoji(emoji):

    emoji_var.set(emoji)

    for button in emoji_buttons:

        if button["text"] == emoji:
            button.config(relief="sunken")
        else:
            button.config(relief="raised")


for index, emoji in enumerate(EMOJIS):

    button = tk.Button(
        emoji_frame,
        text=emoji,
        font=("Arial", 18),
        width=2,
        command=lambda e=emoji: select_emoji(e)
    )

    button.grid(
        row=index // 10,
        column=index % 10,
        padx=3,
        pady=3
    )

    emoji_buttons.append(button)


# =========================================================
# СТАТУС
# =========================================================

login_status = tk.Label(
    login_frame,
    text="",
    font=("Arial", 10),
    fg="#ff5555",
    bg=BG
)

login_status.pack(pady=10)


# =========================================================
# ОСНОВНЕ ВІКНО
# =========================================================

main_frame = tk.Frame(
    root,
    bg=BG
)


# =========================================================
# КОРИСТУВАЧІ
# =========================================================

users_frame = tk.Frame(
    main_frame,
    bg=PANEL,
    width=220
)

users_frame.pack(
    side="left",
    fill="y"
)

users_frame.pack_propagate(False)


tk.Label(
    users_frame,
    text="Користувачі",
    font=("Arial", 14, "bold"),
    fg=TEXT,
    bg=PANEL
).pack(pady=15)


users_list = tk.Listbox(
    users_frame,
    bg=PANEL,
    fg=TEXT,
    font=("Arial", 11),
    borderwidth=0,
    highlightthickness=0,
    selectbackground=ACCENT
)

users_list.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# =========================================================
# ЧАТ
# =========================================================

chat_frame = tk.Frame(
    main_frame,
    bg=CHAT_BG
)

chat_frame.pack(
    side="right",
    fill="both",
    expand=True
)


# =========================================================
# ЗАГОЛОВОК
# =========================================================

header = tk.Frame(
    chat_frame,
    bg=PANEL,
    height=60
)

header.pack(
    fill="x"
)

header.pack_propagate(False)


profile_label = tk.Label(
    header,
    text="",
    font=("Arial", 12, "bold"),
    fg=TEXT,
    bg=PANEL
)

profile_label.pack(
    side="left",
    padx=20
)


# =========================================================
# ОБЛАСТЬ ЧАТУ
# =========================================================

chat_text = tk.Text(
    chat_frame,
    bg=CHAT_BG,
    fg=TEXT,
    font=("Arial", 11),
    state="disabled",
    wrap="word",
    borderwidth=0
)

chat_text.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)


# =========================================================
# ПОЛЕ ВВОДУ
# =========================================================

input_frame = tk.Frame(
    chat_frame,
    bg=PANEL,
    height=60
)

input_frame.pack(
    fill="x"
)

input_frame.pack_propagate(False)


message_entry = tk.Entry(
    input_frame,
    font=("Arial", 12),
    bg="#333438",
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat"
)

message_entry.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(10, 5),
    pady=10
)


# =========================================================
# ДОДАВАННЯ ПОВІДОМЛЕННЯ
# =========================================================

def add_chat_message(text):

    def update():

        chat_text.config(
            state="normal"
        )

        chat_text.insert(
            "end",
            text + "\n"
        )

        chat_text.see(
            "end"
        )

        chat_text.config(
            state="disabled"
        )

    root.after(
        0,
        update
    )


# =========================================================
# ОНОВЛЕННЯ КОРИСТУВАЧІВ
# =========================================================

def update_users(data):

    def update():

        users_list.delete(
            0,
            "end"
        )

        if not data:
            return

        users = data.split(",")

        for user in users:

            parts = user.split("|", 2)

            if len(parts) != 3:
                continue

            name = parts[0]
            avatar = parts[1]
            emoji = parts[2]

            users_list.insert(
                "end",
                f"{emoji} {name} [{avatar}]"
            )

    root.after(
        0,
        update
    )


# =========================================================
# ОТРИМАННЯ ДАНИХ
# =========================================================

def receive_messages():

    global connected

    try:

        while connected:

            data = client.recv(4096)

            if not data:
                break

            message = data.decode(
                "utf-8"
            ).strip()

            if not message:
                continue

            parts = message.split(
                "|",
                2
            )

            if parts[0] == "SYSTEM":

                if len(parts) >= 2:

                    add_chat_message(
                        f"⚙ {parts[1]}"
                    )

            elif parts[0] == "MSG":

                if len(parts) >= 3:

                    sender = parts[1]
                    text = parts[2]

                    add_chat_message(
                        f"💬 {sender}: {text}"
                    )

            elif parts[0] == "USERS":

                users_data = message[
                    len("USERS|"):
                ]

                update_users(
                    users_data
                )

    except Exception as e:

        print(
            "[ПОМИЛКА ОТРИМАННЯ]",
            e
        )

    connected = False

    root.after(
        0,
        disconnect_ui
    )


# =========================================================
# ВІДПРАВКА ПОВІДОМЛЕННЯ
# =========================================================

def send_message():

    if not connected:
        return

    text = message_entry.get().strip()

    if not text:
        return

    try:

        message = (
            f"MSG|{username}|{text}"
        )

        client.sendall(
            message.encode("utf-8")
        )

        message_entry.delete(
            0,
            "end"
        )

    except Exception as e:

        print(
            "[ПОМИЛКА ВІДПРАВКИ]",
            e
        )


# =========================================================
# ЗМІНА ПРОФІЛЮ
# =========================================================

def open_profile_window():

    global selected_avatar
    global selected_emoji

    if not connected:
        return

    window = tk.Toplevel(root)

    window.title(
        "Змінити профіль"
    )

    window.geometry(
        "500x350"
    )

    window.configure(
        bg=BG
    )

    tk.Label(
        window,
        text="Аватар",
        font=("Arial", 12),
        fg=TEXT,
        bg=BG
    ).pack(
        pady=(20, 5)
    )

    new_avatar = tk.StringVar(
        value=selected_avatar
    )

    tk.OptionMenu(
        window,
        new_avatar,
        *AVATARS
    ).pack()


    tk.Label(
        window,
        text="Емодзі",
        font=("Arial", 12),
        fg=TEXT,
        bg=BG
    ).pack(
        pady=(20, 5)
    )


    new_emoji = tk.StringVar(
        value=selected_emoji
    )


    emoji_select_frame = tk.Frame(
        window,
        bg=BG
    )

    emoji_select_frame.pack()


    def choose_emoji(emoji):

        new_emoji.set(
            emoji
        )


    for index, emoji in enumerate(EMOJIS):

        tk.Button(
            emoji_select_frame,
            text=emoji,
            font=("Arial", 16),
            width=2,
            command=lambda e=emoji:
                choose_emoji(e)
        ).grid(
            row=index // 10,
            column=index % 10,
            padx=2,
            pady=2
        )


    def save():

        global selected_avatar
        global selected_emoji

        selected_avatar = new_avatar.get()
        selected_emoji = new_emoji.get()

        try:

            client.sendall(
                f"CHANGE_PROFILE|{selected_avatar}|{selected_emoji}"
                .encode("utf-8")
            )

            profile_label.config(
                text=f"{selected_emoji} {username}"
            )

            window.destroy()

        except Exception as e:

            messagebox.showerror(
                "Помилка",
                str(e)
            )


    tk.Button(
        window,
        text="Зберегти",
        font=("Arial", 11, "bold"),
        bg=ACCENT,
        fg=TEXT,
        relief="flat",
        command=save
    ).pack(
        pady=20
    )


# =========================================================
# ПІДКЛЮЧЕННЯ
# =========================================================

def connect_to_server():

    global client
    global username
    global selected_avatar
    global selected_emoji
    global connected

    username = name_entry.get().strip()

    selected_avatar = avatar_var.get()
    selected_emoji = emoji_var.get()

    if not username:

        login_status.config(
            text="Введіть ім'я користувача"
        )

        return

    login_status.config(
        text="Підключення..."
    )

    try:

        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.connect(
            (
                SERVER_IP,
                SERVER_PORT
            )
        )

        login_message = (
            f"USER|{username}|"
            f"{selected_avatar}|"
            f"{selected_emoji}"
        )

        client.sendall(
            login_message.encode("utf-8")
        )

        connected = True

        login_frame.pack_forget()

        main_frame.pack(
            fill="both",
            expand=True
        )

        profile_label.config(
            text=f"{selected_emoji} {username}"
        )

        message_entry.config(
            state="normal"
        )

        send_button.config(
            state="normal"
        )

        thread = threading.Thread(
            target=receive_messages,
            daemon=True
        )

        thread.start()

        message_entry.focus()

    except Exception as e:

        if client:

            try:
                client.close()
            except:
                pass

        client = None

        login_status.config(
            text=f"Помилка підключення: {e}"
        )


# =========================================================
# UI ПІСЛЯ ВІДКЛЮЧЕННЯ
# =========================================================

def disconnect_ui():

    message_entry.config(
        state="disabled"
    )

    send_button.config(
        state="disabled"
    )

    add_chat_message(
        "❌ З'єднання із сервером втрачено"
    )


# =========================================================
# КНОПКА ПРОФІЛЮ
# =========================================================

tk.Button(
    header,
    text="Профіль",
    font=("Arial", 10),
    command=open_profile_window
).pack(
    side="right",
    padx=10
)


# =========================================================
# КНОПКА ВІДПРАВКИ
# =========================================================

send_button = tk.Button(
    input_frame,
    text="Надіслати",
    font=("Arial", 10, "bold"),
    bg=ACCENT,
    fg=TEXT,
    relief="flat",
    command=send_message
)

send_button.pack(
    side="right",
    padx=(5, 10),
    pady=10
)


# =========================================================
# КНОПКА ВХОДУ
# =========================================================

tk.Button(
    login_frame,
    text="Увійти до чату",
    font=("Arial", 12, "bold"),
    bg=ACCENT,
    fg=TEXT,
    relief="flat",
    width=20,
    height=2,
    command=connect_to_server
).pack(
    pady=20
)


# =========================================================
# ENTER
# =========================================================

name_entry.bind(
    "<Return>",
    lambda event: connect_to_server()
)

message_entry.bind(
    "<Return>",
    lambda event: send_message()
)


# =========================================================
# ЗАКРИТТЯ
# =========================================================

def close_program():

    global connected

    connected = False

    if client:

        try:
            client.shutdown(
                socket.SHUT_RDWR
            )
        except:
            pass

        try:
            client.close()
        except:
            pass

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# =========================================================
# ЗАПУСК
# =========================================================

root.mainloop()