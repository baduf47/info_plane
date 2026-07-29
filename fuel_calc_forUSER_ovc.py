import customtkinter as ctk
from tkinter import scrolledtext, Menu, StringVar
from datetime import datetime
import os
from PIL import Image

# ----------------------------------------------------------------------
# Логика расчёта
# ----------------------------------------------------------------------

FUEL_FACTORS = {
    'тип': {'большой': 1.2, 'маленький': 0.8},
    'погода': {'нормальный': 1.0, 'сильный ветер': 1.3, 'дождь': 1.15}
}

def normalize_string(s):
    if s is None:
        return ''
    return str(s).strip().lower()

def calculate_fuel(v, t, c, f):
    if v is None or str(v).strip() == '':
        return False, "Ошибка: поле 'Скорость' обязательно."
    if t is None or str(t).strip() == '':
        return False, "Ошибка: поле 'Время' обязательно."
    if c is None or str(c).strip() == '':
        return False, "Ошибка: выберите тип самолёта."
    if f is None or str(f).strip() == '':
        return False, "Ошибка: выберите условия полёта."

    try:
        speed = float(v)
    except ValueError:
        return False, "Ошибка: скорость должна быть числом."
    try:
        time = float(t)
    except ValueError:
        return False, "Ошибка: время должно быть числом."

    if speed <= 0:
        return False, "Ошибка: скорость должна быть > 0."
    if time <= 0:
        return False, "Ошибка: время должно быть > 0."

    c_norm = normalize_string(c)
    if c_norm not in FUEL_FACTORS['тип']:
        return False, "Ошибка: недопустимый тип самолёта."
    f_norm = normalize_string(f)
    if f_norm not in FUEL_FACTORS['погода']:
        return False, "Ошибка: недопустимые условия полёта."

    fuel = speed * time * FUEL_FACTORS['тип'][c_norm] * FUEL_FACTORS['погода'][f_norm]
    return True, fuel

# ----------------------------------------------------------------------
# Класс для отображения информации о самолёте (картинка + текст)
# ----------------------------------------------------------------------

class AircraftInfoWindow(ctk.CTkToplevel):
    def __init__(self, parent, initial_type="большой"):
        super().__init__(parent)
        self.title("Информация о самолёте")
        self.geometry("750x650")
        self.minsize(600, 500)

        self.aircraft_type = StringVar(value=initial_type)

        self.texts = {
            "большой": (
                "Предназначен для перевозки значительного числа пассажиров на дальние расстояния. "
                "Эти самолеты могут вмещать 352 пассажира и используются в коммерческой авиации для "
                "регулярных рейсов между городами и странами. Имеет два мотора, расположенных на крыльях. "
                "Корпус выполнен из прочных и легких материалов, таких как титан и углепластик, что позволяет "
                "обеспечить высокую прочность при меньшем весе. Крылья у таких самолетов часто имеют сложную "
                "геометрию для улучшения аэродинамических характеристик."
            ),
            "маленький": (
                "Часто называется лёгким или спортивным, предназначен для коротких перелётов и может "
                "использоваться как для частных, так и для коммерческих целей. Обычно такие самолёты имеют "
                "вместимость от 2 до 6 пассажиров и могут использоваться для обучения пилотов, частных путешествий "
                "или даже для аэрофотосъёмки. Имеет одномоторную конфигурацию, с крыльями, расположенными сверху "
                "или снизу. Корпус выполнен из лёгких материалов, таких как алюминий или композитные материалы, "
                "что обеспечивает хорошую манёвренность и экономию топлива."
            )
        }

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_paths = {
            "большой": os.path.join(base_dir, "picture_1.png"),
            "маленький": os.path.join(base_dir, "picture_2.png")
        }

        self.configure(fg_color="#2b2b2b")
        main_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        radio_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        radio_frame.pack(fill="x", pady=(0, 15))

        self.radio_big = ctk.CTkRadioButton(radio_frame, text="Большой", variable=self.aircraft_type,
                                            value="большой", command=self.update_content,
                                            fg_color="#4a6fa5", hover_color="#3a5a8a")
        self.radio_big.pack(side=ctk.LEFT, padx=10)

        self.radio_small = ctk.CTkRadioButton(radio_frame, text="Маленький", variable=self.aircraft_type,
                                              value="маленький", command=self.update_content,
                                              fg_color="#4a6fa5", hover_color="#3a5a8a")
        self.radio_small.pack(side=ctk.LEFT, padx=10)

        self.image_label = ctk.CTkLabel(main_frame, text="", fg_color="transparent")
        self.image_label.pack(pady=10)

        self.textbox = ctk.CTkTextbox(main_frame, wrap="word",
                                      font=ctk.CTkFont(size=13),
                                      fg_color="#1e1e1e", text_color="#e0e0e0",
                                      border_width=2, border_color="#3a3a3a",
                                      height=200)
        self.textbox.pack(fill="both", expand=True, pady=10)
        self.textbox.configure(state="disabled")

        self.update_content()

    def update_content(self):
        current_type = self.aircraft_type.get()
        self.textbox.configure(state="normal")
        self.textbox.delete(1.0, "end")
        self.textbox.insert("end", self.texts[current_type])
        self.textbox.configure(state="disabled")

        img_path = self.image_paths[current_type]
        if os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path)
                max_width, max_height = 500, 300
                pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(pil_img.width, pil_img.height))
                self.image_label.configure(image=ctk_img, text="")
            except Exception as e:
                self.image_label.configure(image=None, text=f"Не удалось загрузить картинку:\n{str(e)}")
        else:
            self.image_label.configure(image=None, text="Картинка не найдена.\nУбедитесь, что файлы picture_1.png и picture_2.png лежат в папке с программой.")

# ----------------------------------------------------------------------
# Главное приложение
# ----------------------------------------------------------------------

class FuelAppSimple(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("✈️ Авиа-калькулятор топлива")
        self.geometry("850x650")
        self.minsize(700, 500)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)  # поля ввода
        main_frame.grid_rowconfigure(2, weight=0)  # кнопки
        main_frame.grid_rowconfigure(3, weight=1)  # поле вывода

        # Заголовок
        title = ctk.CTkLabel(main_frame, text="✈️ Расчёт топлива для рейса",
                             font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(0, 15), sticky="w")

        # Поля ввода (два столбца)
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)

        # Левый столбец
        left_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left_frame, text="Скорость (км/ч):", anchor="w").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_speed = ctk.CTkEntry(left_frame, placeholder_text="например, 800")
        self.entry_speed.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(left_frame, text="Время полёта (ч):", anchor="w").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_time = ctk.CTkEntry(left_frame, placeholder_text="например, 3")
        self.entry_time.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Правый столбец
        right_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        right_frame.grid_columnconfigure(0, weight=1)

        # Строка для типа самолёта + кнопка информации
        type_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        type_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        type_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(type_frame, text="Тип самолёта:", anchor="w").grid(row=0, column=0, sticky="w")
        self.combo_type = ctk.CTkComboBox(right_frame, values=["большой", "маленький"], state="readonly")
        self.combo_type.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.combo_type.set("большой")

        # Кнопка информации о самолёте
        btn_info_plane = ctk.CTkButton(right_frame, text="ℹ️", width=40, height=30,
                                       fg_color="transparent", hover_color="#444",
                                       command=self.open_aircraft_info)
        btn_info_plane.grid(row=1, column=1, padx=(5, 0), sticky="w")

        # Условия полёта
        ctk.CTkLabel(right_frame, text="Условия полёта:", anchor="w").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.combo_weather = ctk.CTkComboBox(right_frame, values=["нормальный", "сильный ветер", "дождь"], state="readonly")
        self.combo_weather.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.combo_weather.set("нормальный")

        # ========== Кнопки (только Рассчитать и Очистить) ==========
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.btn_calc = ctk.CTkButton(button_frame, text="🚀 Рассчитать", command=self.calculate,
                                      height=40, corner_radius=8)
        self.btn_calc.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_clear = ctk.CTkButton(button_frame, text="🧹 Очистить", command=self.clear_output,
                                       height=40, corner_radius=8, fg_color="#555", hover_color="#444")
        self.btn_clear.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # ========== Поле вывода ==========
        self.result_text = scrolledtext.ScrolledText(main_frame, wrap="word",
                                                     font=("Segoe UI", 12),
                                                     bg="#2b2b2b", fg="#ffffff",
                                                     insertbackground="white")
        self.result_text.grid(row=3, column=0, sticky="nsew", pady=10)
        self.result_text.config(state="disabled")

        # Копирование текста
        self.result_text.bind("<Control-Key>", self.copy_selection)
        self.result_text.bind("<Button-3>", self.show_context_menu)

        # Строка состояния
        self.status_label = ctk.CTkLabel(main_frame, text="Готов к работе", font=ctk.CTkFont(size=12), anchor="w")
        self.status_label.grid(row=4, column=0, sticky="w", pady=(5, 0))

        # Контекстное меню для копирования
        self.context_menu = Menu(self.result_text, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_selection)

        self.log_result("Добро пожаловать!\nВведите данные и нажмите «Рассчитать».\n")

    # ------------------------------------------------------------------
    # Методы вывода, очистки, расчёта
    # ------------------------------------------------------------------

    def log_result(self, text, color=None):
        self.result_text.config(state="normal")
        if color:
            self.result_text.insert("end", text, color)
            self.result_text.tag_config(color, foreground=color)
        else:
            self.result_text.insert("end", text)
        self.result_text.see("end")
        self.result_text.config(state="disabled")

    def clear_output(self):
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, "end")
        self.result_text.config(state="disabled")
        self.status_label.configure(text="Вывод очищен", text_color="#ffffff")

    def calculate(self):
        v = self.entry_speed.get()
        t = self.entry_time.get()
        c = self.combo_type.get()
        f = self.combo_weather.get()

        self.log_result("\n" + "─" * 60 + "\n", "#42a5f5")
        self.log_result(f"📅 {datetime.now().strftime('%H:%M:%S')}  Расчёт:\n", "#42a5f5")
        self.log_result(f"  Скорость: {v} км/ч\n")
        self.log_result(f"  Время: {t} ч\n")
        self.log_result(f"  Тип: {c}\n")
        self.log_result(f"  Погода: {f}\n")

        success, result = calculate_fuel(v, t, c, f)
        if success:
            self.log_result(f"✅ РЕЗУЛЬТАТ: {result:.2f} усл. ед.\n", "#4caf50")
            self.status_label.configure(text="Расчёт выполнен успешно", text_color="#4caf50")
        else:
            self.log_result(f"❌ {result}\n", "#f44336")
            self.status_label.configure(text="Ошибка в данных", text_color="#f44336")

    # ------------------------------------------------------------------
    # Копирование выделенного текста
    # ------------------------------------------------------------------

    def copy_selection(self, event=None):
        # Если событие от клавиатуры, проверяем, что это клавиша C (keycode 67)
        if event:
            if event.keycode != 67:  # 67 — код клавиши 'C' в Windows
                return
        try:
            selected = self.result_text.get("sel.first", "sel.last")
            if selected:
                self.clipboard_clear()
                self.clipboard_append(selected)
                self.status_label.configure(text="Текст скопирован", text_color="#4caf50")
        except:
            pass

    def show_context_menu(self, event):
        try:
            self.result_text.focus_set()
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # ------------------------------------------------------------------
    # Открытие окна с информацией о самолёте
    # ------------------------------------------------------------------

    def open_aircraft_info(self):
        current_type = self.combo_type.get()
        AircraftInfoWindow(self, initial_type=current_type)

# ----------------------------------------------------------------------
# Запуск
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = FuelAppSimple()
    app.mainloop()
