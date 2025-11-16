import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk, ImageFilter
import pygame

from main import MainApplication

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 400
WINDOWNSIZE = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
ACCENT = "#ff3b7f"
FONT = ("Times new roman", 10)
DARK_BG = "#111"

user_database = { #nơi lưu tài khoản và mk
    "t": "t",
    "thinh": "12345",
    "nhuan": "nhuan",
    "dat": "dat",
    "duy": "duy"
}

root = tk.Tk()

pygame.mixer.init()
SOUND_CLICK_PATH = "sound\sound_click.mp3"


def play_sound():
    try:
        sound = pygame.mixer.Sound(SOUND_CLICK_PATH)
        sound.play()
    except Exception as e:
        print(f"Không thể phát âm thanh: {e}")

#tạo ra một hộp thoại thông báo thay cho messagebox truyền thống
def show_custom_message(title_text, message_text, is_error=False, parent=None): #parent la cua so cha ma hop thoai nay se bam vao
    parent = parent if parent else root
    dialog = tk.Toplevel(parent, bg=DARK_BG, padx=20, pady=20) #Toplevel tao ra cua so moi nhung van thuoc ve parent
    dialog.title(title_text)
    dialog.geometry("400x150")

    #Thực hiện việc căn giữa bằng cách lấy tọa độ đã được update và lấy điểm ở giữa để di chuyển cửa sổ dialog tới
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    dialog.geometry(f'+{x}+{y}')

    dialog.transient(parent) #dialog là cửa sổ tạm thời của parent, sẽ luôn nổi lên trên parent vaf không hiển thị trên thanh taskbar như 1 ứng dụng mới
    dialog.grab_set() #Khóa toàn bộ tương tác với các cửa sổ khác trong ứng dụng

    icon_color = "#33c461" if not is_error else ACCENT
    content_frame = tk.Frame(dialog, bg=DARK_BG)
    content_frame.pack(pady=10)

    tk.Label(content_frame, text="ⓘ", fg=icon_color, bg=DARK_BG, font=("Segoe UI", 24)).pack(side="left", padx=10)
    tk.Label(content_frame, text=message_text, fg="white", bg=DARK_BG, font=("Segoe UI", 10)).pack(side="left",
                                                                                                   anchor="w")

    close_btn = tk.Button(dialog, text="Đóng", bg=ACCENT, fg="white",
                          relief="flat", font=("Segoe UI", 10, "bold"),
                          command=lambda: [play_sound(), dialog.destroy()]) #đóng cửa sổ thông báo
    close_btn.pack(pady=10)
    root.wait_window(dialog)


def open_register_window(): #cửa sổ đăng ký
    register_window = tk.Toplevel(root, bg=DARK_BG, bd=0)
    register_window.title("Register New Account")
    register_window.geometry("380x380")
    register_window.resizable(False, False)

    register_window.update_idletasks() #lấy tọadđộ để thực hiện việc căn giữa
    width = register_window.winfo_width()
    height = register_window.winfo_height()
    x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
    register_window.geometry(f'+{x}+{y}')

    register_window.transient(root)
    register_window.grab_set()

    tk.Label(register_window, text="Create Account",
             bg=DARK_BG, fg="white", font=("Times new roman", 16, "bold")).pack(pady=(20, 20))

    tk.Label(register_window, text="User name", fg="white", bg=DARK_BG, font=FONT).pack(anchor="w", padx=30)
    reg_username = tk.Entry(register_window, bg=DARK_BG, fg="white", insertbackground="white", bd=0, font=FONT)
    reg_username.pack(fill="x", padx=30)
    tk.Frame(register_window, height=1, bg="white").pack(fill="x", padx=30, pady=(0, 10))

    tk.Label(register_window, text="Password", fg="white", bg=DARK_BG, font=FONT).pack(anchor="w", padx=30)
    reg_password = tk.Entry(register_window, show="*", bg=DARK_BG, fg="white", insertbackground="white", bd=0,
                            font=FONT)
    reg_password.pack(fill="x", padx=30)
    tk.Frame(register_window, height=1, bg="white").pack(fill="x", padx=30, pady=(0, 10))

    tk.Label(register_window, text="Confirm Password", fg="white", bg=DARK_BG, font=FONT).pack(anchor="w", padx=30)
    reg_confirm_password = tk.Entry(register_window, show="*", bg=DARK_BG, fg="white", insertbackground="white", bd=0,
                                    font=FONT)
    reg_confirm_password.pack(fill="x", padx=30)
    tk.Frame(register_window, height=1, bg="white").pack(fill="x", padx=30, pady=(0, 10))

    def register_user_logic():
        u = reg_username.get().strip()
        p1 = reg_password.get()
        p2 = reg_confirm_password.get()

        if not u or not p1 or not p2:
            show_custom_message("Thiếu thông tin", "Vui lòng điền đầy đủ các trường.", is_error=True,
                                parent=register_window)
            return

        if p1 != p2:
            show_custom_message("Thất bại", "Mật khẩu nhập lại không khớp!", is_error=True, parent=register_window)
            return

        if u in user_database:
            show_custom_message("Thất bại", f"Tên đăng nhập '{u}' đã tồn tại!", is_error=True, parent=register_window)
        else:
            user_database[u] = p1 #lưu người dùng mới vào database, dưới dạng dict
            username_combo['values'] = list(user_database.keys())
            show_custom_message("Thành công", f"Đăng ký thành công cho '{u}'!", parent=register_window)
            register_window.destroy()

    reg_btn = tk.Button(register_window, text="Register", bg=ACCENT, fg="white",
                        relief="flat", font=("Times new roman", 11, "bold"),
                        command=lambda: [play_sound(), register_user_logic()]) #lambda tạo hàm vô danh mới để thực thi cả 2 lệnh cùng lúc
    reg_btn.pack(fill="x", padx=30, pady=(15, 10))
    root.wait_window(register_window)

root.title("Smart Farm - Login")
root.geometry(WINDOWNSIZE)
root.resizable(False, False)

try:
    bg_path = r"image\login\background_login.jpg"
    bg_original = Image.open(bg_path).resize((WINDOW_WIDTH, WINDOW_HEIGHT))
    background_image_blurred = bg_original.filter(ImageFilter.GaussianBlur(5))
    background_image_tk = ImageTk.PhotoImage(background_image_blurred)
except Exception as e:
    messagebox.showerror("Lỗi", f"Không thể mở ảnh nền: {e}")
    root.destroy() #thoats cửa sổ thay vì crash
    exit()

canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, highlightthickness=0)
canvas.create_image(0, 0, anchor="nw", image=background_image_tk)
canvas.place(x=0, y=0)
root.background_image_ref = background_image_tk

FRAME_WIDTH = 340
FRAME_HEIGHT = 360

frame = tk.Frame(root, bg=DARK_BG, bd=0)
frame.place(relx=0.5, rely=0.5, anchor="center", width=FRAME_WIDTH, height=FRAME_HEIGHT)

title = tk.Label(frame, text="Login App", bg=DARK_BG, fg="white", font=("Segoe UI", 16, "bold"))
title.pack(pady=(10, 20))

tk.Label(frame, text="User name", fg="white", bg=DARK_BG, font=FONT).pack(anchor="w", padx=30)

username_combo = ttk.Combobox(
    frame,
    values=list(user_database.keys()), #Lấy tất cả tên người dùng từ user_database và nạp vào làm các giá trị xổ xuống cho Combobox
    font=FONT,
    state="normal"
)
username_combo.pack(fill="x", padx=30)
tk.Frame(frame, height=1, bg="white").pack(fill="x", padx=30, pady=(0, 10))

username_combo.bind("<Button-1>", lambda e: play_sound()) #nhấp chuột trái
username_combo.bind("<<ComboboxSelected>>", lambda e: play_sound()) #chọn option trong combobox

tk.Label(frame, text="Password", fg="white", bg=DARK_BG, font=FONT).pack(anchor="w", padx=30)
password = tk.Entry(frame, show="*", bg=DARK_BG, fg="white", insertbackground="white", bd=0, font=FONT)
password.pack(fill="x", padx=30)
tk.Frame(frame, height=1, bg="white").pack(fill="x", padx=30, pady=(0, 10))

show_frame = tk.Frame(frame, bg=DARK_BG) #tạo frame để show pass voiws đăng kí cùng hàng
show_frame.pack(fill="x", padx=30, pady=5)

show_password = tk.BooleanVar() #tick vào hiện pass

def toggle_password_visibility():
    if show_password.get():
        password.config(show="")
    else:
        password.config(show="*")


check_btn = tk.Checkbutton(show_frame, text="Show password", variable=show_password,
                           bg=DARK_BG, fg="white", activebackground=DARK_BG,
                           selectcolor=DARK_BG, command=lambda: [play_sound(), toggle_password_visibility()])
check_btn.pack(side="left")

forgot_label = tk.Label(show_frame, text="Forgot Password?", fg=ACCENT, bg=DARK_BG, cursor="hand2")
forgot_label.pack(side="right")
forgot_label.bind("<Button-1>", lambda e: [play_sound(), show_custom_message("Thông báo",
                                                                             "Vui lòng liên hệ nhóm 404 để được cấp lại tài khoản")])

def authenticate():
    u = username_combo.get().strip()
    p = password.get()

    if not u or not p:
        show_custom_message("Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu.", is_error=True)
    elif u in user_database and user_database[u] == p:
        show_custom_message("Thành công", f"Đăng nhập thành công, chào mừng {u}!")
        MainApplication(login_root=root, username=u)    #Khởi tạo cửa sổ mới và mở cửa sổ trong file main.py
    else:
        show_custom_message("Thất bại", "Sai tên đăng nhập hoặc mật khẩu!", is_error=True)


login_btn = tk.Button(frame, text="Login", bg=ACCENT, fg="white",
                      relief="flat", font=("Times new roman", 11, "bold"),
                      command=lambda: [play_sound(), authenticate()])
login_btn.pack(fill="x", padx=30, pady=(15, 5))

register_btn = tk.Button(frame, text="Register", bg="#333", fg="white",
                         relief="flat", font=("Times new roman", 11, "bold"),
                         command=lambda: [play_sound(), open_register_window()])
register_btn.pack(fill="x", padx=30, pady=(0, 10))

root.bind("<Return>", lambda event: [play_sound(), authenticate()])

tk.Label(frame, text="App was designed by @404 Team", bg=DARK_BG, fg="#aaa", font=("Times new roman", 8)).pack(side="bottom",
                                                                                                        pady=(10, 0))

root.mainloop()