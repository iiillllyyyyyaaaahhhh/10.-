import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Обработка изображений. Вариант 10")
        self.geometry("950x750")
        self.resizable(True, True)

        # Создаём объект процессора
        self.processor = Processor()

        # Текущее изображение для отображения (PhotoImage)
        self.original_photo = None
        self.processed_photo = None

        self.create_widgets()

    def create_widgets(self):
        # Создаём вкладки
        tab_control = ttk.Notebook(self)
        self.tab_original = ttk.Frame(tab_control)
        self.tab_processed = ttk.Frame(tab_control)
        tab_control.add(self.tab_original, text="Оригинал")
        tab_control.add(self.tab_processed, text="Обработка")
        tab_control.pack(expand=1, fill="both")

        # ----- Вкладка "Оригинал" -----
        self.load_btn = tk.Button(
            self.tab_original,
            text="Загрузить изображение",
            command=self.load_image,
            bg="#4CAF50", fg="white", font=("Arial", 10)
        )
        self.load_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Метка для отображения оригинала
        self.original_label = tk.Label(self.tab_original, bg="#f0f0f0", relief="sunken")
        self.original_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Настройка растягивания метки
        self.tab_original.grid_rowconfigure(1, weight=1)
        self.tab_original.grid_columnconfigure(0, weight=1)

        # ----- Вкладка "Обработка" -----
        # Ползунок порога
        tk.Label(self.tab_processed, text="Порог яркости:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.threshold_slider = tk.Scale(
            self.tab_processed,
            from_=0, to=255,
            orient=tk.HORIZONTAL,
            length=350,
            command=self.on_threshold_change
        )
        self.threshold_slider.set(128)
        self.threshold_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.threshold_value = tk.Label(self.tab_processed, text="128", width=5, font=("Arial", 10))
        self.threshold_value.grid(row=0, column=2, padx=5, pady=5)

        # Информационная метка (количество объектов)
        self.info_label = tk.Label(
            self.tab_processed,
            text="Объектов: 0",
            font=("Arial", 10, "bold"),
            fg="blue"
        )
        self.info_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # Метка для отображения обработанного изображения
        self.processed_label = tk.Label(self.tab_processed, bg="#f0f0f0", relief="sunken")
        self.processed_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Кнопка сохранения
        self.save_btn = tk.Button(
            self.tab_processed,
            text="Сохранить результат",
            command=self.save_image,
            bg="#2196F3", fg="white", font=("Arial", 10)
        )
        self.save_btn.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Настройка растягивания для вкладки обработки
        self.tab_processed.grid_rowconfigure(2, weight=1)
        self.tab_processed.grid_columnconfigure(1, weight=1)

    def load_image(self):
        """Открывает диалог выбора файла и загружает изображение."""
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        if not self.processor.load_image(path):
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")
            return

        # Отображаем оригинал на первой вкладке
        original = self.processor.get_original()
        self.show_image(original, self.original_label)

        # Автоматически применяем порог (текущее значение ползунка)
        thresh = int(self.threshold_slider.get())
        self.apply_and_display(thresh)

        messagebox.showinfo("Загрузка", f"Изображение загружено:\n{path}")

    def show_image(self, cv_img, target_label, max_width=800, max_height=600):
        """
        Конвертирует OpenCV изображение (BGR) в PhotoImage и отображает в target_label.
        Сохраняет ссылку на PhotoImage, чтобы не удалялась сборщиком мусора.
        """
        if cv_img is None:
            target_label.config(image="")
            return

        # Конвертируем BGR → RGB
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)

        # Масштабируем с сохранением пропорций
        pil_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(pil_img)
        target_label.config(image=photo)
        # Храним ссылку в соответствующем атрибуте
        if target_label == self.original_label:
            self.original_photo = photo
        else:
            self.processed_photo = photo

    def on_threshold_change(self, value):
        """Срабатывает при перемещении ползунка."""
        thresh = int(float(value))
        self.threshold_value.config(text=str(thresh))
        self.apply_and_display(thresh)

    def apply_and_display(self, threshold):
        """Запускает обработку и обновляет изображение на второй вкладке."""
        if self.processor.get_original() is None:
            return

        processed_img, count = self.processor.process(threshold)
        if processed_img is not None:
            self.show_image(processed_img, self.processed_label)
            self.info_label.config(text=f"Объектов: {count}")

    def save_image(self):
        """Сохраняет текущее обработанное изображение в файл."""
        if self.processor.get_original() is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        # Бинарное изображение можно сохранить или изображение с прямоугольниками.
        # По условию задачи сохраняем результат обработки (с прямоугольниками).
        # Для этого повторно обработаем с текущим порогом.
        thresh = int(self.threshold_slider.get())
        processed_img, _ = self.processor.process(thresh)
        if processed_img is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if not file_path:
            return

        cv2.imwrite(file_path, processed_img)
        messagebox.showinfo("Сохранение", f"Результат сохранён:\n{file_path}")

if __name__ == "__main__":
    app = App()
    app.mainloop()