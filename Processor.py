import cv2
import numpy as np

class Processor:
    def __init__(self):
        self._image = None          # оригинал (BGR)
        self._gray = None           # оттенки серого
        self._binary = None         # бинарное изображение
        self._contours = None       # найденные контуры
        self._boxes = []            # список (x, y, w, h)
        self._object_count = 0

    def load_image(self, path):
        """Загружает изображение из файла. Возвращает True при успехе."""
        self._image = cv2.imread(path)
        if self._image is None:
            return False
        # Сбрасываем все результаты при новой загрузке
        self._gray = None
        self._binary = None
        self._contours = None
        self._boxes = []
        self._object_count = 0
        return True

    def get_original(self):
        """Возвращает оригинальное изображение (BGR)."""
        return self._image

    def process(self, threshold_value):
        """
        Полный конвейер: серый → бинарный → поиск контуров → вычисление прямоугольников.
        Возвращает изображение с нарисованными прямоугольниками (BGR) и количество объектов.
        """
        if self._image is None:
            return None, 0

        # 1. Преобразование в оттенки серого
        self._gray = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

        # 2. Бинарный порог
        _, self._binary = cv2.threshold(self._gray, threshold_value, 255, cv2.THRESH_BINARY)

        # 3. Поиск контуров (внешние)
        result = cv2.findContours(self._binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(result) == 3:
            _, self._contours, _ = result
        else:
            self._contours, _ = result

        # 4. Вычисление ограничивающих прямоугольников для каждого контура
        self._boxes = []
        self._object_count = 0
        img_with_boxes = self._image.copy()

        for cnt in self._contours:
            area = cv2.contourArea(cnt)
            # Отсеиваем слишком мелкий шум (площадь < 100 пикселей)
            if area > 100:
                x, y, w, h = cv2.boundingRect(cnt)
                self._boxes.append((x, y, w, h))
                self._object_count += 1
                # Рисуем прямоугольник на копии
                cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return img_with_boxes, self._object_count

    def get_binary(self):
        """Возвращает бинарное изображение (для отображения или сохранения)."""
        return self._binary

    def get_boxes(self):
        """Возвращает список прямоугольников (x, y, w, h)."""
        return self._boxes

    def get_object_count(self):
        """Возвращает количество найденных объектов."""
        return self._object_count