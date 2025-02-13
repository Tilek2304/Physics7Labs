import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont

class LabWorkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Виртуальная лабораторная работа по физике')
        self.setGeometry(100, 100, 400, 750)

        self.initial_volume = 400
        self.item_volume = 0
        self.correct_item_volume = 0  # Добавил переменную для проверки ответа
        self.animation_progress = 0
        self.is_animating = False
        self.item_generated = False
        self.scale_value = 40  # Цена деления шкалы

        # Поля для ответов
        self.init_volume_label = QLabel('Начальный объем жидкости (мл):', self)
        self.init_volume_input = QLineEdit(self)

        self.item_volume_label = QLabel('Объем предмета (мл):', self)
        self.item_volume_input = QLineEdit(self)

        self.scale_label = QLabel('Цена деления шкалы (мл):', self)
        self.scale_input = QLineEdit(self)

        self.result_label = QLabel('', self)

        # Кнопки
        self.generate_button = QPushButton('Сгенерировать предмет', self)
        self.generate_button.clicked.connect(self.generate_item)

        self.immerse_button = QPushButton('Погрузить предмет', self)
        self.immerse_button.clicked.connect(self.start_immersion)

        self.check_button = QPushButton('Проверить', self)
        self.check_button.clicked.connect(self.check_answers)

        # Размещение элементов
        layout = QVBoxLayout()
        layout.addWidget(self.init_volume_label)
        layout.addWidget(self.init_volume_input)
        layout.addWidget(self.item_volume_label)
        layout.addWidget(self.item_volume_input)
        layout.addWidget(self.scale_label)
        layout.addWidget(self.scale_input)
        layout.addWidget(self.result_label)
        layout.addStretch(1)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.immerse_button)
        layout.addWidget(self.check_button)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_immersion)

    def generate_item(self):
        if self.item_generated:
            self.result_label.setText('Можно создать только один предмет!')
            return
        
        self.correct_item_volume = random.choice(range(40, 601, 40))  # Генерация кратного 40
        self.item_volume = self.correct_item_volume  # Устанавливаем текущий объем предмета
        self.item_generated = True
        self.result_label.setText(f'Предмет создан ({self.item_volume} мл). Теперь его можно погрузить.')

    def start_immersion(self):
        if self.item_volume == 0:
            self.result_label.setText('Сначала сгенерируйте предмет!')
            return

        if self.initial_volume + self.item_volume > 1000:
            self.result_label.setText('Мензурка переполнена! Предмет не помещается.')
            return

        self.is_animating = True
        self.animation_progress = 0
        self.timer.start(20)

    def animate_immersion(self):
        self.animation_progress += 2
        if self.animation_progress >= 100:
            self.timer.stop()
            self.is_animating = False
            self.initial_volume += self.item_volume
            self.item_volume = 0
            self.result_label.setText(f'Новый объем жидкости: {self.initial_volume} мл')
        self.update()

    def check_answers(self):
        try:
            user_init_volume = int(self.init_volume_input.text())
            user_item_volume = int(self.item_volume_input.text())
            user_scale = int(self.scale_input.text())

            correct_init_volume = 400
            correct_item_volume = self.correct_item_volume  # Используем сохраненный объем
            correct_scale = self.scale_value

            errors = []
            if user_init_volume != correct_init_volume:
                errors.append('Ошибка в начальном объеме жидкости.')
            if user_item_volume != correct_item_volume:
                errors.append('Ошибка в объеме предмета.')
            if user_scale != correct_scale:
                errors.append('Ошибка в цене деления шкалы.')

            if errors:
                self.result_label.setText('\n'.join(errors))
            else:
                self.result_label.setText('Все ответы правильные!')

        except ValueError:
            self.result_label.setText('Ошибка: Введите числовые значения.')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        menzurka_x = 150
        menzurka_y = 250  # Опустил мензурку ниже
        menzurka_width = 100
        menzurka_height = 400

        painter.setPen(Qt.black)
        painter.setBrush(QBrush(QColor(200, 200, 255)))
        painter.drawRect(menzurka_x, menzurka_y, menzurka_width, menzurka_height)

        liquid_height = int((self.initial_volume / 1000) * menzurka_height)
        painter.setBrush(QBrush(QColor(0, 0, 255)))
        painter.drawRect(menzurka_x, menzurka_y + menzurka_height - liquid_height, menzurka_width, liquid_height)

        painter.setPen(Qt.black)
        font = QFont('Arial', 8)
        painter.setFont(font)

        for volume in range(0, 1001, 200):
            y = menzurka_y + menzurka_height - int((volume / 1000) * menzurka_height)
            painter.drawLine(menzurka_x - 20, y, menzurka_x, y)
            painter.drawText(menzurka_x - 50, y + 5, f'{volume} мл')

        for volume in range(0, 1001, 40):
            y = menzurka_y + menzurka_height - int((volume / 1000) * menzurka_height)
            if volume % 200 != 0:
                painter.drawLine(menzurka_x - 10, y, menzurka_x, y)

        if self.is_animating:
            item_height = int((self.item_volume / 1000) * menzurka_height)
            start_y = menzurka_y - item_height
            item_y = start_y + int((self.animation_progress / 100) * (menzurka_y + menzurka_height - liquid_height - start_y))
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawRect(menzurka_x + 25, item_y, 50, item_height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LabWorkApp()
    ex.show()
    sys.exit(app.exec_())
