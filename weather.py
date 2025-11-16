import tkinter as tk
from tkinter import ttk, Button, Label, PhotoImage
from geopy.geocoders import Nominatim
from tkinter import messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
from PIL import Image, ImageTk

DAY_BG = "#F5F5dc"  # màu nền cho ban ngày
NIGHT_BG = "#1d2629"  # Nền đen cho ban đêm
DAY_TEXT = "#111111"  # Chữ đen cho ban ngày
NIGHT_TEXT = "#FFFFFF"  # Chữ trắng cho ban đêm
ACCENT = "#ff3b7f"

# Biến toàn cục để lưu múi giờ hiện tại
current_timezone = None

def get_time_based_theme(timezone_str=None):
    """Xác định theme dựa trên thời gian của múi giờ cụ thể"""
    if timezone_str:
        try:
            # Sử dụng múi giờ của thành phố hiện tại
            tz = pytz.timezone(timezone_str)
            local_time = datetime.now(tz)
            current_hour = local_time.hour
        except:
            # Fallback về múi giờ local nếu có lỗi
            current_hour = datetime.now().hour
    else:
        # Mặc định dùng múi giờ local
        current_hour = datetime.now().hour

    if 5 <= current_hour < 18:  # Từ 5h sáng đến 17h59 (ban ngày)
        return DAY_BG, DAY_TEXT, "day"
    else:  # Từ 18h đến 4h59 sáng hôm sau (ban đêm)
        return NIGHT_BG, NIGHT_TEXT, "night"


def WeatherWindow(parent):
    global current_timezone
    # Lấy theme dựa trên thời gian hiện tại (mặc định local)
    bg_color, text_color, current_theme = get_time_based_theme()

    # 1. Tạo cửa sổ Toplevel mới
    weather_window = tk.Toplevel(parent, bg=bg_color, bd=0, padx=20, pady=20)
    weather_window.title("Weather")
    weather_window.geometry("900x500")
    weather_window.resizable(False, False)

    # Biến để theo dõi theme hiện tại
    weather_window.current_theme = current_theme
    weather_window.current_timezone = None

    # Căn giữa cửa sổ
    weather_window.update_idletasks()
    width = weather_window.winfo_width()
    height = weather_window.winfo_height()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    weather_window.geometry(f'+{x}+{y}')

    # 3. Cài đặt modal
    weather_window.transient(parent)
    weather_window.grab_set()

    def update_theme_by_time():
        """Cập nhật theme dựa trên thời gian và trả về xem có thay đổi không"""
        # Sử dụng múi giờ của thành phố hiện tại nếu có
        timezone_to_use = weather_window.current_timezone
        new_bg_color, new_text_color, new_theme = get_time_based_theme(timezone_to_use)

        # Chỉ cập nhật nếu theme thay đổi
        if new_theme != weather_window.current_theme:
            weather_window.current_theme = new_theme

            # Cập nhật màu nền cửa sổ
            weather_window.configure(bg=new_bg_color)

            # Cập nhật màu cho các widget
            name.configure(bg=new_bg_color, fg=new_text_color)
            clock.configure(bg=new_bg_color, fg=new_text_color)
            t.configure(bg=new_bg_color, fg=new_text_color)
            c.configure(bg=new_bg_color, fg=new_text_color)

            # Cập nhật màu nền cho các label ảnh
            myimage.configure(bg=new_bg_color)
            logo.configure(bg=new_bg_color)
            frame_myimage.configure(bg=new_bg_color)

            # Cập nhật màu chữ cho textfield
            textfield.configure(bg="#404040", fg=new_text_color, insertbackground=new_text_color)

            print(f"Theme đã thay đổi: {new_theme} (Múi giờ: {timezone_to_use})")  # Debug

            return True  # Có thay đổi
        return False  # Không thay đổi

    def auto_update_theme():
        """Tự động kiểm tra và cập nhật theme mỗi phút"""
        if weather_window.winfo_exists():  # Kiểm tra cửa sổ còn tồn tại
            update_theme_by_time()
            # Lên lịch kiểm tra lại sau 1 phút (60000 ms)
            weather_window.after(60000, auto_update_theme)

    def getWeather(city_name=None):
        # Nếu không có city_name được truyền vào, lấy từ textfield
        if city_name is None:
            city = textfield.get().strip()
        else:
            city = city_name
            textfield.delete(0, tk.END)  # Xóa nội dung cũ
            textfield.insert(0, city)  # Chèn thành phố mặc định

        if not city:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên thành phố!", parent=weather_window)
            return
        try:
            # Hiển thị trạng thái loading
            name.config(text="ĐANG TẢI DỮ LIỆU...")
            weather_window.update()

            geolocator = Nominatim(user_agent="weather_app_404")
            location = geolocator.geocode(city)
            if not location:
                messagebox.showerror("Lỗi", f"Không tìm thấy thành phố: {city}", parent=weather_window)
                name.config(text="THỜI TIẾT TẠI: --")
                return

            # Lấy múi giờ
            obj = TimezoneFinder()
            result = obj.timezone_at(lng=location.longitude, lat=location.latitude)

            if not result:
                home = pytz.utc
                current_time = datetime.now(home).strftime("%I:%M %p (UTC)")
                weather_window.current_timezone = "UTC"
            else:
                home = pytz.timezone(result)
                local_time = datetime.now(home)
                current_time = local_time.strftime("%I:%M %p")
                weather_window.current_timezone = result

            clock.config(text=current_time)
            city_name_found = location.address.split(',')[0]
            name.config(text=f"THỜI TIẾT TẠI: {city_name_found.upper()}")

            # API call với units=metric để lấy độ C
            api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=643242f782f12ed33d3a6a7a9444c78d&units=metric&lang=vi"

            json_data = requests.get(api, timeout=10).json()

            # Kiểm tra lỗi API
            if json_data.get('cod') != 200:
                error_message = json_data.get('message', 'Lỗi không xác định')
                messagebox.showerror("Lỗi API", f"Không thể lấy dữ liệu: {error_message}", parent=weather_window)
                name.config(text="THỜI TIẾT TẠI: --")
                return

            # Cập nhật giao diện với dữ liệu mới
            condition = json_data['weather'][0]['main']
            description = json_data['weather'][0]['description'].capitalize()

            temp = int(json_data['main']['temp'])
            feels_like = int(json_data['main']['feels_like'])

            pressure = json_data['main']['pressure']
            humidity = json_data['main']['humidity']
            wind = json_data['wind']['speed']
            visibility = json_data.get('visibility', 'N/A')

            # Chuyển đổi visibility từ mét sang km nếu có
            if visibility != 'N/A':
                visibility = f"{visibility / 1000:.1f} km"

            t.config(text=f"{temp}°C")
            c.config(text=f"{description} | CẢM GIÁC NHƯ {feels_like}°C")

            w.config(text=f"{wind} m/s")
            h.config(text=f"{humidity}%")
            p.config(text=f"{pressure} hPa")
            v.config(text=visibility)

            # CẬP NHẬT THEME SAU KHI CÓ MÚI GIỚI
            update_theme_by_time()

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Lỗi mạng", "Không thể kết nối. Vui lòng kiểm tra internet.", parent=weather_window)
            name.config(text="THỜI TIẾT TẠI: --")
        except requests.exceptions.Timeout:
            messagebox.showerror("Lỗi", "Kết nối quá thời gian chờ!", parent=weather_window)
            name.config(text="THỜI TIẾT TẠI: --")
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            messagebox.showerror("Lỗi", "Đã xảy ra lỗi không xác định!", parent=weather_window)
            name.config(text="THỜI TIẾT TẠI: --")

    def get_default_weather():
        """Lấy thời tiết mặc định cho Hồ Chí Minh khi khởi động"""
        getWeather("Ho Chi Minh")

    # --- Tạo Widgets ---
    try:
        # Search image
        weather_window.Search_image = PhotoImage(file=r"image\weather\search.png")
        myimage = Label(weather_window, image=weather_window.Search_image, bg=bg_color)
        myimage.place(x=20, y=20)
    except Exception as e:
        print(f"Không thể tải ảnh search: {e}")

    # Text field - để trống ban đầu
    textfield = tk.Entry(weather_window, justify="center", width=17, font=("Segoe UI", 16, "bold"),
                         bg="#404040", border=0, fg=text_color, insertbackground=text_color)
    textfield.place(x=50, y=40, height=35)
    textfield.focus()
    textfield.bind('<Return>', lambda e: getWeather())  # Gọi không tham số để lấy từ textfield

    try:
        # Search icon
        weather_window.Search_icon = PhotoImage(file=r"image\weather\search_icon.png")
        myimage_icon = Button(weather_window, image=weather_window.Search_icon, borderwidth=0,
                              cursor="hand2", bg="#404040", command=getWeather)  # Gọi không tham số
        myimage_icon.place(x=350, y=34)
    except Exception as e:
        print(f"Không thể tải ảnh search icon: {e}")
        # Fallback: tạo nút tìm kiếm bằng text
        search_btn = Button(weather_window, text="TÌM", font=("Segoe UI", 10, "bold"),
                            bg=ACCENT, fg="white", command=getWeather)  # Gọi không tham số
        search_btn.place(x=350, y=34, width=60, height=35)

    try:
        # Logo
        weather_window.Logo_image = PhotoImage(file=r"image\weather\logo.png")
        logo = Label(weather_window, image=weather_window.Logo_image, bg=bg_color)
        logo.place(x=100, y=140)
    except Exception as e:
        print(f"Không thể tải logo: {e}")

    try:
        # Bottom box
        weather_window.Frame_image = PhotoImage(file=r"image\weather\box.png")
        frame_myimage = Label(weather_window, image=weather_window.Frame_image, bg=bg_color)
        frame_myimage.place(x=0, y=380)
    except Exception as e:
        print(f"Không thể tải ảnh box: {e}")

    # Time and city labels
    name = Label(weather_window, font=("Segoe UI", 15, "bold"), bg=bg_color, fg=text_color)
    name.place(x=30, y=100)
    name.config(text="THỜI TIẾT TẠI: --")

    clock = Label(weather_window, font=("Segoe UI", 14), bg=bg_color, fg=text_color)
    clock.place(x=30, y=130)
    clock.config(text="--:-- --")

    # Temperature
    t = Label(weather_window, font=("Segoe UI", 48, "bold"), fg=text_color, bg=bg_color)
    t.place(x=350, y=140)
    t.config(text="--°C")

    # Description
    c = Label(weather_window, font=("Segoe UI", 12, 'bold'), bg=bg_color, fg=text_color)
    c.place(x=350, y=220)
    c.config(text="Đang tải dữ liệu...")

    # Info labels (giữ nguyên màu cho các label thông tin)
    label1 = Label(weather_window, text="Gió", font=("Segoe UI", 12, 'bold'), fg="white", bg="#1ab5ef")
    label1.place(x=50, y=400)

    label2 = Label(weather_window, text="Độ ẩm", font=("Segoe UI", 12, 'bold'), fg="white", bg="#1ab5ef")
    label2.place(x=180, y=400)  # Điều chỉnh vị trí

    label3 = Label(weather_window, text="Áp suất", font=("Segoe UI", 12, 'bold'), fg="white", bg="#1ab5ef")
    label3.place(x=350, y=400)  # Thay thế vị trí của DESCRIPTION

    label4 = Label(weather_window, text="Tầm nhìn", font=("Segoe UI", 12, 'bold'), fg="white", bg="#1ab5ef")
    label4.place(x=520, y=400)  # Điều chỉnh vị trí

    # Value labels (giữ nguyên màu cho các giá trị thông tin)
    w = Label(weather_window, text="...", font=("Segoe UI", 14, "bold"), bg="#1ab5ef", fg="white")
    w.place(x=50, y=430)

    h = Label(weather_window, text="...", font=("Segoe UI", 14, "bold"), bg="#1ab5ef", fg="white")
    h.place(x=180, y=430)  # Điều chỉnh vị trí

    p = Label(weather_window, text="...", font=("Segoe UI", 14, "bold"), bg="#1ab5ef", fg="white")
    p.place(x=350, y=430)  # Thay thế vị trí của DESCRIPTION

    v = Label(weather_window, text="...", font=("Segoe UI", 14, "bold"), bg="#1ab5ef", fg="white")
    v.place(x=520, y=430)  # Điều chỉnh vị trí

    # Close button với style đồng bộ
    style = ttk.Style()
    style.configure('Accent.TButton',
                    background=ACCENT,

                    font=("Segoe UI", 10, "bold"),
                    relief='flat')
    style.map('Accent.TButton',
              background=[('active', '#ff5c99'), ('pressed', '#ff2170')])

    close_button = ttk.Button(weather_window, text="ĐÓNG", style='Accent.TButton',
                              command=weather_window.destroy)
    close_button.place(x=800, y=40, width=80, height=35)

    # BẮT ĐẦU TỰ ĐỘNG CẬP NHẬT THEME
    weather_window.after(1000, auto_update_theme)  # Bắt đầu sau 1 giây

    # GỌI HÀM LẤY THỜI TIẾT MẶC ĐỊNH SAU KHI TẠO XONG GIAO DIỆN
    weather_window.after(100, get_default_weather)

    # Chờ cho đến khi cửa sổ này được đóng
    parent.wait_window(weather_window)