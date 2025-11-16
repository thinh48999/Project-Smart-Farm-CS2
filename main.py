import tkinter as tk
from tkinter import messagebox
from weather import WeatherWindow #Đi đến file weather.py và nhập class WeatherWindow từ file đó vào đây
from PIL import Image, ImageTk, ImageFilter
import serial
import serial.tools.list_ports #tự động quét và tìm các cổng COM đang kết nối với máy tính
import threading #tạo một luồng (thread) riêng để đọc dữ liệu từ Arduino mà không làm treo app
import time
import pygame
import json #xử lý dữ liệu định dạng JSON
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ========== CẤU HÌNH HỆ THỐNG ==========
@dataclass
class Config:
    """Cấu hình giao diện và màu sắc"""
    WINDOW_WIDTH: int = 1250
    WINDOW_HEIGHT: int = 900
    # Màu sắc
    ACCENT: str = "#ff3b7f"
    DARK_BG: str = "#111"
    NAV_BG: str = "#231F20"
    TEXT_FG: str = "white"
    # Font
    FONT_FAMILY: str = "Times New Roman"
    FONT_SIZE: int = 10

    # Đường dẫn
    BG_IMAGE: str = r"image\login\background_login.jpg"
    SOUND_CLICK: str = "sound/sound_click.mp3"
    SOUND_BG: str = "sound/sound_background.mp3"
    ICON_OFF: str = r"image\main\control\off.png"
    ICON_ON: str = r"image\main\control\on.png"

    # Arduino
    BAUD_RATE: int = 115200 #Tốc độ truyền dữ liệu của arduino mega
    READ_TIMEOUT: float = 1.0 #Thời gian tối đa (giây) mà hàm .readline() sẽ chờ dữ liệu trước khi bỏ qua.
    #Nếu trong vòng 1.0 giây mà vẫn không thấy gì, hãy từ bỏ, trả về một chuỗi rỗng, và để chương trình chạy tiếp
    SERIAL_DELAY: float = 0.05 #Một khoảng nghỉ nhỏ (giây) sau mỗi lần gửi/đọc để tránh làm quá tải bộ đệm serial.


# ========== QUẢN LÝ DỮ LIỆU CẢM BIẾN ==========
class SensorData:
    def __init__(self):
        self._data = {
            'temperature': 0.0,
            'humidity': 0.0,
            'gas': 0,
            'flame': 0,
            'dark': 0,
            'fan': 0,
            'pump': 0,
            'light': 0,
            'gate': 0,
            'door': 0,
            'mode': 'AUTO'
        }
        self._lock = threading.Lock()

    def update(self, key: str, value) -> None:
        """Cập nhật giá trị (thread-safe)"""
        with self._lock:
            if key in self._data:
                self._data[key] = value

    def get(self, key: str, default=None):
        """Lấy giá trị (thread-safe)"""
        with self._lock:
            return self._data.get(key, default)

    def update_from_dict(self, data_dict: Dict) -> None:
        mapping = {
            'temp': 'temperature',
            'hum': 'humidity',
            'humidity': 'humidity',
            'gas': 'gas',
            'flame': 'flame',
            'dark': 'dark',
            'fan': 'fan',
            'pump': 'pump',
            'light': 'light',
            'gate': 'gate',
            'door': 'door',
            'mode': 'mode'
        }

        with self._lock:
            for key, value in data_dict.items():
                mapped_key = mapping.get(key, key)
                if mapped_key in self._data:
                    # Convert string number to appropriate type
                    if mapped_key in ['temperature', 'humidity']:
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0.0
                    else:
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            value = 0

                    self._data[mapped_key] = value

    @property
    def all_data(self) -> Dict:
        """Trả về bản sao của tất cả dữ liệu"""
        with self._lock:
            return self._data.copy()


# ========== GIAO TIẾP ARDUINO ==========
class ArduinoCommunication:
    """Quản lý kết nối và giao tiếp với Arduino"""
    def __init__(self, app):
        self.app = app
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected: bool = False
        self.sensor_data = SensorData()
        self.read_thread: Optional[threading.Thread] = None
        self._running = False
        # Config
        self.BAUD_RATE = 115200
        self.READ_TIMEOUT = 1.0
        self.SERIAL_DELAY = 0.05

        self._connect()

    def _connect(self) -> None:
        """Tìm và kết nối Arduino"""
        try:
            port = self._find_arduino_port()
            if not port:
                print("✗ Không tìm thấy Arduino")
                return

            self.serial_connection = serial.Serial(
                port,
                self.BAUD_RATE,
                timeout=self.READ_TIMEOUT
            )
            time.sleep(2)  # Đợi Arduino reset
            self.is_connected = True
            print(f"✓ Đã kết nối Arduino tại {port}")

            # Clear buffer
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()

            self._start_reading_thread()

        except Exception as e:
            print(f"✗ Lỗi kết nối Arduino: {e}")
            self.is_connected = False

    def _find_arduino_port(self) -> Optional[str]:
        """Tìm cổng COM của Arduino"""
        ports = list(serial.tools.list_ports.comports())

        print("\n🔍 Quét cổng COM:")
        for port in ports:
            print(f"  - {port.device}: {port.description}")

        # Tìm theo keyword
        keywords = ['ARDUINO', 'CH340', 'USB-SERIAL', 'USB']
        for port in ports:
            desc_upper = port.description.upper()
            if any(kw in desc_upper for kw in keywords):
                print(f"✓ Chọn: {port.device}")
                return port.device

        # Fallback: lấy cổng đầu tiên
        if ports:
            print(f"⚠ Dùng cổng đầu tiên: {ports[0].device}")
            return ports[0].device

        return None

    def _start_reading_thread(self) -> None:
        """Khởi động thread đọc dữ liệu"""
        self._running = True
        self.read_thread = threading.Thread(
            target=self._read_loop,
            daemon=True,
            name="Arduino-Reader"
        )
        self.read_thread.start()
        print("✓ Thread đọc dữ liệu đã khởi động")

    def _read_loop(self) -> None:
        """Vòng lặp đọc dữ liệu liên tục"""
        while self._running and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting:
                    line = self.serial_connection.readline()
                    line = line.decode('utf-8', errors='ignore').strip()

                    if line:
                        print(f"← Arduino: {line}")
                        self._process_data(line)

            except UnicodeDecodeError:
                pass  # Bỏ qua dữ liệu lỗi encoding
            except Exception as e:
                print(f"✗ Lỗi đọc dữ liệu: {e}")
                time.sleep(0.5)

            time.sleep(self.SERIAL_DELAY)

    def _process_data(self, data: str) -> None:
        try:
            # ===== XỬ LÝ JSON DATA =====
            if data.startswith("REPORT:{"):
                json_str = data[7:]  # Bỏ "REPORT:"
                self._parse_json_data(json_str)

            elif data.startswith("DATA:ALL:{"):
                json_str = data[9:]  # Bỏ "DATA:ALL:"
                self._parse_json_data(json_str)

            # ===== XỬ LÝ XÁC NHẬN LỆNH =====
            elif data.startswith("OK:"):
                parts = data.split(":")
                if len(parts) >= 3:
                    command = parts[1]
                    value = parts[2]
                    print(f"  ✓ {command}: {value}")

                    # Cập nhật trạng thái thiết bị
                    self._update_device_state(command, value)

            # ===== XỬ LÝ CẢNH BÁO =====
            elif "FIRE" in data.upper() or "🔥" in data:
                self.app.after(0, lambda: self.app.show_alert('fire'))

            elif "GAS" in data.upper() or "⚠" in data:
                self.app.after(0, lambda: self.app.show_alert('gas'))

            # ===== XỬ LÝ LỖI =====
            elif data.startswith("ERROR:"):
                error_msg = data[6:]
                print(f"  ✗ Arduino Error: {error_msg}")

        except Exception as e:
            print(f"✗ Lỗi xử lý dữ liệu: {e}")

    def _parse_json_data(self, json_str: str) -> None:
        try:
            data_dict = json.loads(json_str)
            self.sensor_data.update_from_dict(data_dict)

            # Cập nhật giao diện trong main thread
            self.app.after(0, self.app.update_display)

        except json.JSONDecodeError as e:
            print(f"✗ Lỗi parse JSON: {e}")
            print(f"  Data: {json_str}")

    def _update_device_state(self, command: str, value: str) -> None:
        state_map = {
            'FAN': 'fan',
            'PUMP': 'pump',
            'LIGHT': 'light',
            'GATE': 'gate',
            'DOOR': 'door'
        }

        value_map = {
            'ON': 1,
            'OFF': 0,
            'OPEN': 1,
            'CLOSE': 0,
            'CLOSED': 0
        }

        if command in state_map:
            key = state_map[command]
            val = value_map.get(value, 0)
            self.sensor_data.update(key, val)

    def send_command(self, command: str) -> bool:
        if not self.is_connected or not self.serial_connection:
            print("⚠ Arduino chưa kết nối!")
            return False

        try:
            cmd_bytes = f"{command}\n".encode('utf-8')
            self.serial_connection.write(cmd_bytes)
            print(f"→ Gửi: {command}")
            time.sleep(self.SERIAL_DELAY)
            return True

        except Exception as e:
            print(f"✗ Lỗi gửi lệnh: {e}")
            return False

    def close(self) -> None:
        """Đóng kết nối Arduino"""
        print("\n🔌 Đang đóng kết nối Arduino...")
        self._running = False
        self.is_connected = False

        if self.serial_connection:
            try:
                self.serial_connection.close()
                print("✓ Đã đóng kết nối Arduino")
            except Exception as e:
                print(f"✗ Lỗi đóng kết nối: {e}")


# ========== QUẢN LÝ ÂM THANH ==========
class AudioManager:
    """Quản lý âm thanh trong ứng dụng"""

    def __init__(self):
        self.config = Config()
        pygame.mixer.init()
        self._load_background_music()

    def _load_background_music(self) -> None:
        """Load và phát nhạc nền"""
        try:
            pygame.mixer.music.load(self.config.SOUND_BG)
            pygame.mixer.music.play(-1)
            print("✓ Đã phát nhạc nền")
        except Exception as e:
            print(f"✗ Lỗi phát nhạc nền: {e}")

    def play_click(self) -> None:
        """Phát âm thanh click"""
        try:
            sound = pygame.mixer.Sound(self.config.SOUND_CLICK)
            sound.play()
        except Exception as e:
            print(f"✗ Lỗi phát âm thanh click: {e}")

    def stop_all(self) -> None:
        """Dừng tất cả âm thanh"""
        pygame.mixer.music.stop()


# ========== QUẢN LÝ HÌNH ẢNH ==========
class ImageManager:
    """Quản lý tải và lưu trữ hình ảnh"""

    def __init__(self):
        self.config = Config()
        self.images: Dict[str, ImageTk.PhotoImage] = {}

    def load_background(self, width: int, height: int) -> Optional[ImageTk.PhotoImage]:
        """Load background với blur effect"""
        try:
            bg = Image.open(self.config.BG_IMAGE)
            bg = bg.resize((width, height))
            bg = bg.filter(ImageFilter.GaussianBlur(5))
            photo = ImageTk.PhotoImage(bg)
            self.images['background'] = photo
            return photo
        except Exception as e:
            print(f"✗ Lỗi load background: {e}")
            return None

    def load_toggle_icons(self, size: Tuple[int, int] = (80, 80)) -> Tuple[
        Optional[ImageTk.PhotoImage], Optional[ImageTk.PhotoImage]]:
        """Load icon ON/OFF"""
        try:
            img_off = Image.open(self.config.ICON_OFF).resize(size, Image.Resampling.LANCZOS)
            img_on = Image.open(self.config.ICON_ON).resize(size, Image.Resampling.LANCZOS)

            photo_off = ImageTk.PhotoImage(img_off)
            photo_on = ImageTk.PhotoImage(img_on)

            self.images['toggle_off'] = photo_off
            self.images['toggle_on'] = photo_on

            return photo_off, photo_on
        except Exception as e:
            print(f"✗ Lỗi load toggle icons: {e}")
            return None, None

    def load_device_image(self, name: str, size: Tuple[int, int] = (300, 200)) -> Optional[ImageTk.PhotoImage]:
        """Load hình ảnh thiết bị"""
        try:
            img = Image.open(rf"image\main\control\{name}.png")
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.images[name] = photo
            return photo
        except Exception as e:
            print(f"✗ Lỗi load image {name}: {e}")
            return None


# ========== TRANG TỔNG QUAN ==========
class DashboardPage:
    """Trang hiển thị tổng quan cảm biến"""

    def __init__(self, parent, config: Config):
        self.parent = parent
        self.config = config
        self.widgets: List[tk.Widget] = []
        self.canvases: Dict[str, tk.Canvas] = {}
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Tạo các widget cho trang tổng quan"""
        # Header
        header = tk.Label(
            self.parent,
            text="",  # Sẽ update động
            font=(self.config.FONT_FAMILY, 24, "bold"),
            bg=self.config.DARK_BG,
            fg="white"
        )
        self.widgets.append(header)

        # Tạo canvas cho các cảm biến
        sensor_configs = [
            ('temperature', 250, 100, "#2E86AB"),
            ('humidity', 550, 100, "#A23B72"),
            ('gas', 850, 100, "#C73E1D"),
            ('fire', 250, 350, "#3D5A80"),
            ('light_sensor', 550, 350, "#533A71")
        ]

        for name, x, y, color in sensor_configs:
            canvas = self._create_sensor_canvas(color)
            self.canvases[name] = canvas
            self.widgets.append(canvas)

    def _create_sensor_canvas(self, bg_color: str) -> tk.Canvas:
        """Tạo canvas cho một cảm biến"""
        return tk.Canvas(
            self.parent,
            width=280,
            height=180,
            bg=bg_color,
            highlightthickness=0
        )

    def update_display(self, sensor_data: SensorData, username: str) -> None:
        """Cập nhật hiển thị dữ liệu"""
        # Update header
        self.widgets[0].configure(text=f"Xin chào, {username}! 👋")

        # Update từng cảm biến
        self._update_temperature(sensor_data.get('temperature'))
        self._update_humidity(sensor_data.get('humidity'))
        self._update_gas(sensor_data.get('gas'))
        self._update_fire(sensor_data.get('flame'))
        self._update_light(sensor_data.get('dark'))

    def _update_temperature(self, temp: float) -> None:
        """Cập nhật hiển thị nhiệt độ"""
        canvas = self.canvases['temperature']
        canvas.delete("all")

        is_high = temp > 35
        color = "#FF6B6B" if is_high else "#4FC3F7"
        status = "⚠ Cao" if is_high else "✓ Bình thường"

        canvas.create_text(140, 30, text="NHIỆT ĐỘ",
                           font=(self.config.FONT_FAMILY, 12, "bold"), fill="white")
        canvas.create_text(140, 70, text=f"{temp:.1f}°C",
                           font=(self.config.FONT_FAMILY, 24, "bold"), fill=color)
        canvas.create_text(140, 110, text=status,
                           font=(self.config.FONT_FAMILY, 10), fill="white")

    def _update_humidity(self, humidity: float) -> None:
        """Cập nhật hiển thị độ ẩm"""
        canvas = self.canvases['humidity']
        canvas.delete("all")

        is_low = humidity < 50
        color = "#FFD700" if is_low else "#4FC3F7"
        status = "⚠ Khô" if is_low else "✓ Bình thường"

        canvas.create_text(140, 30, text="ĐỘ ẨM",
                           font=(self.config.FONT_FAMILY, 12, "bold"), fill="white")
        canvas.create_text(140, 70, text=f"{humidity:.1f}%",
                           font=(self.config.FONT_FAMILY, 24, "bold"), fill=color)
        canvas.create_text(140, 110, text=status,
                           font=(self.config.FONT_FAMILY, 10), fill="white")

    def _update_gas(self, gas_detected: int) -> None:
        """Cập nhật hiển thị cảm biến gas"""
        canvas = self.canvases['gas']
        canvas.delete("all")

        is_detected = gas_detected == 1
        color = "#FF6B6B" if is_detected else "#90EE90"
        text = "⚠ Phát hiện!" if is_detected else "✓ An toàn"

        canvas.create_text(140, 30, text="KHÍ GAS",
                           font=(self.config.FONT_FAMILY, 12, "bold"), fill="white")
        canvas.create_text(140, 70, text=text,
                           font=(self.config.FONT_FAMILY, 20, "bold"), fill=color)

    def _update_fire(self, fire_detected: int) -> None:
        """Cập nhật hiển thị cảm biến lửa"""
        canvas = self.canvases['fire']
        canvas.delete("all")

        is_detected = fire_detected == 1
        color = "#FF6B6B" if is_detected else "#90EE90"
        text = "🔥 PHÁT HIỆN!" if is_detected else "✓ An toàn"

        canvas.create_text(140, 30, text="CẢNH BÁO LỬA",
                           font=(self.config.FONT_FAMILY, 12, "bold"), fill="white")
        canvas.create_text(140, 70, text=text,
                           font=(self.config.FONT_FAMILY, 18, "bold"), fill=color)

    def _update_light(self, is_dark: int) -> None:
        """Cập nhật hiển thị cảm biến ánh sáng"""
        canvas = self.canvases['light_sensor']
        canvas.delete("all")

        color = "#FFD700" if is_dark == 1 else "#90EE90"
        text = "🌙 Tối" if is_dark == 1 else "☀ Sáng"

        canvas.create_text(140, 30, text="ÁNH SÁNG",
                           font=(self.config.FONT_FAMILY, 12, "bold"), fill="white")
        canvas.create_text(140, 70, text=text,
                           font=(self.config.FONT_FAMILY, 20, "bold"), fill=color)

    def show(self) -> None:
        """Hiển thị trang"""
        self.widgets[0].place(x=250, y=30)

        positions = [(250, 100), (550, 100), (850, 100), (250, 350), (550, 350)]
        for i, (x, y) in enumerate(positions):
            self.widgets[i + 1].place(x=x, y=y)

    def hide(self) -> None:
        """Ẩn trang"""
        for widget in self.widgets:
            widget.place_forget()


# ========== TRANG ĐIỀU KHIỂN ==========
class ControlsPage:
    """Trang điều khiển thiết bị"""

    def __init__(self, parent, config: Config, image_manager: ImageManager,
                 audio_manager: AudioManager, arduino: ArduinoCommunication):
        self.parent = parent
        self.config = config
        self.image_manager = image_manager
        self.audio_manager = audio_manager
        self.arduino = arduino
        self.widgets: List[tk.Widget] = []
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Tạo các widget cho trang điều khiển"""
        # Header
        header = tk.Label(
            self.parent,
            text="🎛️ Điều khiển Thiết bị",
            font=(self.config.FONT_FAMILY, 24, "bold"),
            bg=self.config.DARK_BG,
            fg="white"
        )
        self.widgets.append(header)

        # Nút chế độ AUTO
        btn_auto = self._create_mode_button(
            "🤖 Chế độ Tự động",
            "#4CAF50",
            lambda: self._set_mode('AUTO')
        )
        self.widgets.append(btn_auto)

        # Nút chế độ MANUAL
        btn_manual = self._create_mode_button(
            "👆 Chế độ Thủ công",
            self.config.ACCENT,
            lambda: self._set_mode('MANUAL')
        )
        self.widgets.append(btn_manual)

        # Tạo các thiết bị điều khiển
        self._create_device_controls()

    def _create_mode_button(self, text: str, bg_color: str, command) -> tk.Button:
        """Tạo nút chuyển chế độ"""
        return tk.Button(
            self.parent,
            text=text,
            font=(self.config.FONT_FAMILY, 12, "bold"),
            bg=bg_color,
            fg=self.config.TEXT_FG,
            relief="flat",
            cursor="hand2",
            command=lambda: [self.audio_manager.play_click(), command()]
        )

    def _create_device_controls(self) -> None:
        """Tạo điều khiển cho các thiết bị"""
        devices = [
            ("hinh_4", "hinh_4.1", self._toggle_fan, "🌀 Quạt"),
            ("hinh_1", "hinh_1.1", self._toggle_light, "💡 Đèn"),
            ("hinh_6", "hinh_6.1", self._toggle_pump, "💧 Bơm"),
            ("hinh_3.1", "hinh_3", self._toggle_door, "🚪 Cửa"),
            ("hinh_3.1", "hinh_3", self._toggle_gate, "🚧 Cổng"),
        ]

        for img_off, img_on, toggle_func, label_text in devices:
            device_widgets = self._create_device_widget(
                img_off, img_on, toggle_func, label_text
            )
            self.widgets.extend(device_widgets)

    def _create_device_widget(self, img_off_name: str, img_on_name: str,
                              toggle_func, label_text: str) -> List[tk.Widget]:
        """Tạo widget cho một thiết bị"""
        widgets = []

        # Label tên thiết bị
        label = tk.Label(
            self.parent,
            text=label_text,
            font=(self.config.FONT_FAMILY, 14, "bold"),
            bg=self.config.DARK_BG,
            fg="white"
        )
        widgets.append(label)

        # Load hình ảnh thiết bị
        img_off = self.image_manager.load_device_image(img_off_name)
        img_on = self.image_manager.load_device_image(img_on_name)

        if not img_off or not img_on:
            return widgets

        # Label hiển thị hình ảnh
        img_label = tk.Label(self.parent, image=img_off, bd=0)
        img_label.image_off = img_off
        img_label.image_on = img_on
        widgets.append(img_label)

        # Nút công tắc
        check_var = tk.BooleanVar()

        def on_toggle():
            state = check_var.get()
            toggle_func(state)
            img_label.configure(image=img_on if state else img_off)

        # Load icon riêng cho từng Checkbutton
        icon_off, icon_on = self.image_manager.load_toggle_icons()

        check_btn = tk.Checkbutton(
            self.parent,
            variable=check_var,
            image=icon_off,
            selectimage=icon_on,
            command=lambda: [self.audio_manager.play_click(), on_toggle()],
            indicatoron=0,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )

        check_btn.icon_off = icon_off
        check_btn.icon_on = icon_on

        widgets.append(check_btn)

        return widgets

    def _set_mode(self, mode: str) -> None:
        """Đặt chế độ hoạt động"""
        self.arduino.send_command(f"MODE:{mode}")
        mode_text = "TỰ ĐỘNG" if mode == "AUTO" else "THỦ CÔNG"
        messagebox.showinfo("Chế độ", f"Đã chuyển sang chế độ {mode_text}")

    def _toggle_fan(self, state: bool) -> None:
        """Bật/tắt quạt"""
        cmd = "FAN:ON" if state else "FAN:OFF"
        self.arduino.send_command(cmd)

    def _toggle_light(self, state: bool) -> None:
        """Bật/tắt đèn"""
        cmd = "LIGHT:ON" if state else "LIGHT:OFF"
        self.arduino.send_command(cmd)

    def _toggle_pump(self, state: bool) -> None:
        """Bật/tắt bơm"""
        cmd = "PUMP:ON" if state else "PUMP:OFF"
        self.arduino.send_command(cmd)

    def _toggle_door(self, state: bool) -> None:
        """Mở/đóng cửa"""
        cmd = "DOOR:OPEN" if state else "DOOR:CLOSE"
        self.arduino.send_command(cmd)

    def _toggle_gate(self, state: bool) -> None:
        """Mở/đóng cổng"""
        cmd = "GATE:OPEN" if state else "GATE:CLOSE"
        self.arduino.send_command(cmd)

    def show(self) -> None:
        """Hiển thị trang"""
        # Header và nút chế độ
        self.widgets[0].place(x=250, y=30)
        self.widgets[1].place(x=250, y=100, width=200, height=50)
        self.widgets[2].place(x=470, y=100, width=200, height=50)

        # Thiết bị
        positions = [(250, 200), (580, 200), (910, 200), (250, 480), (580, 480)]

        device_widgets_start = 3
        for i, (x, y) in enumerate(positions):
            idx = device_widgets_start + i * 3
            self.widgets[idx].place(x=x, y=y - 30)  # Label
            self.widgets[idx + 1].place(x=x, y=y)  # Image
            self.widgets[idx + 2].place(x=x + 200, y=y + 30)  # Button

    def hide(self) -> None:
        """Ẩn trang"""
        for widget in self.widgets:
            widget.place_forget()


# ========== ỨNG DỤNG CHÍNH ==========
class MainApplication(tk.Toplevel):
    """Ứng dụng chính Smart Farm"""

    def __init__(self, login_root, username: str):
        super().__init__(login_root)

        self.login_root = login_root
        self.username = username
        self.config = Config()

        self._setup_window()
        self._initialize_managers()
        self._setup_background()
        self._create_pages()
        self._show_page('dashboard')
        self._start_update_loop()

    def _setup_window(self) -> None:
        """Cấu hình cửa sổ chính"""
        self.title("Smart Farm - Nông trại thông minh")
        self.geometry(f"{self.config.WINDOW_WIDTH}x{self.config.WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.login_root.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _initialize_managers(self) -> None:
        """Khởi tạo các manager"""
        self.audio_manager = AudioManager()
        self.image_manager = ImageManager()
        self.arduino = ArduinoCommunication(self)

    def _setup_background(self) -> None:
        """Thiết lập background"""
        bg_frame = tk.Frame(self, bg=self.config.DARK_BG)
        bg_frame.place(x=0, y=0, width=self.config.WINDOW_WIDTH,
                       height=self.config.WINDOW_HEIGHT)

        bg_image = self.image_manager.load_background(
            self.config.WINDOW_WIDTH,
            self.config.WINDOW_HEIGHT
        )

        if bg_image:
            canvas = tk.Canvas(
                bg_frame,
                width=self.config.WINDOW_WIDTH,
                height=self.config.WINDOW_HEIGHT,
                highlightthickness=0
            )
            canvas.create_image(0, 0, anchor="nw", image=bg_image)
            canvas.place(x=0, y=0)

    def _create_pages(self) -> None:
        """Tạo các trang của ứng dụng"""
        # Tạo navigation bar
        self._create_navigation()

        # Tạo trang tổng quan
        self.dashboard_page = DashboardPage(self, self.config)

        # Tạo trang điều khiển
        self.controls_page = ControlsPage(
            self,
            self.config,
            self.image_manager,
            self.audio_manager,
            self.arduino
        )

        print("✓ Đã tạo tất cả các trang")

    def _create_navigation(self) -> None:
        """Tạo thanh điều hướng"""
        nav_frame = tk.Frame(
            self,
            bg=self.config.NAV_BG,
            width=220,
            height=self.config.WINDOW_HEIGHT
        )
        nav_frame.place(x=0, y=0)

        # Logo
        tk.Label(
            nav_frame,
            text="🌱 SMART FARM",
            font=(self.config.FONT_FAMILY, 18, "bold"),
            bg=self.config.NAV_BG,
            fg=self.config.ACCENT
        ).place(x=20, y=20)

        # Các nút điều hướng
        nav_buttons = [
            ("📊 Tổng quan", 100, lambda: self._show_page('dashboard')),
            ("🎛️ Điều khiển", 150, lambda: self._show_page('controls')),
            ("🌤️ Thời tiết", 200, self._open_weather)
        ]

        for text, y_pos, command in nav_buttons:
            tk.Button(
                nav_frame,
                text=text,
                font=(self.config.FONT_FAMILY, 12, "bold"),
                bg=self.config.NAV_BG,
                fg=self.config.TEXT_FG,
                relief="flat",
                cursor="hand2",
                command=lambda cmd=command: [self.audio_manager.play_click(), cmd()]
            ).place(x=20, y=y_pos, width=180, height=40)

        # Thông tin user
        tk.Label(
            nav_frame,
            text=f"👤 {self.username}",
            font=(self.config.FONT_FAMILY, 10, "bold"),
            bg=self.config.NAV_BG,
            fg="#aaa"
        ).place(x=50, y=780)

        # Nút đăng xuất
        tk.Button(
            nav_frame,
            text="🚪 Đăng xuất",
            font=(self.config.FONT_FAMILY, 11, "bold"),
            bg=self.config.ACCENT,
            fg=self.config.TEXT_FG,
            relief="flat",
            cursor="hand2",
            command=lambda: [self.audio_manager.play_click(), self.on_close()]
        ).place(x=20, y=820, width=180, height=40)

    def _show_page(self, page_name: str) -> None:
        """Chuyển đổi giữa các trang"""
        print(f"\n✓ Chuyển sang trang {page_name}")

        # Ẩn tất cả trang
        self.dashboard_page.hide()
        self.controls_page.hide()

        # Hiển thị trang được chọn
        if page_name == 'dashboard':
            self.dashboard_page.show()
            self.update_display()
        elif page_name == 'controls':
            self.controls_page.show()

    def _open_weather(self) -> None:
        """Mở cửa sổ thời tiết"""
        try:
            WeatherWindow(self)
        except Exception as e:
            print(f"✗ Lỗi mở cửa sổ thời tiết: {e}")
            messagebox.showerror("Lỗi", "Không thể mở cửa sổ thời tiết")

    def _start_update_loop(self) -> None:
        """Bắt đầu vòng lặp cập nhật dữ liệu"""
        self._update_sensor_data()

    def _update_sensor_data(self) -> None:
        """Yêu cầu dữ liệu từ Arduino định kỳ"""
        if self.arduino.is_connected:
            self.arduino.send_command("GET:ALL")

        # Lặp lại sau 3 giây
        self.after(3000, self._update_sensor_data)

    def update_display(self) -> None:
        """Cập nhật hiển thị dữ liệu trên giao diện"""
        try:
            self.dashboard_page.update_display(
                self.arduino.sensor_data,
                self.username
            )
        except Exception as e:
            print(f"✗ Lỗi cập nhật hiển thị: {e}")

    def show_alert(self, alert_type: str) -> None:
        """Hiển thị cảnh báo"""
        alerts = {
            'fire': {
                'title': "🔥 CẢNH BÁO LỬA",
                'message': "Phát hiện lửa!\nHệ thống đã tự động kích hoạt chế độ an toàn.",
                'type': 'error'
            },
            'gas': {
                'title': "⚠ CẢNH BÁO GAS",
                'message': "Phát hiện khí gas vượt ngưỡng!\nVui lòng kiểm tra hệ thống.",
                'type': 'warning'
            }
        }

        if alert_type in alerts:
            alert = alerts[alert_type]
            if alert['type'] == 'error':
                messagebox.showerror(alert['title'], alert['message'])
            else:
                messagebox.showwarning(alert['title'], alert['message'])

    def on_close(self) -> None:
        """Xử lý khi đóng ứng dụng"""
        print("\n✓ Đóng ứng dụng...")

        # Dừng âm thanh
        self.audio_manager.stop_all()

        # Đóng kết nối Arduino
        if hasattr(self, 'arduino'):
            self.arduino.close()

        # Đóng cửa sổ
        self.destroy()
        self.login_root.deiconify()


# ========== MAIN ==========
if __name__ == "__main__":
    print("=" * 50)
    print("SMART FARM MANAGEMENT SYSTEM")
    print("=" * 50)

