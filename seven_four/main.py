import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QLineEdit, QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Виртуальная лабораторная работа")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.create_theory_tab()
        self.create_experiment_tab()
        self.create_result_tab()
        
        self.tabs.addTab(self.theory_tab, "Теория")
        self.tabs.addTab(self.experiment_tab, "Эксперимент")
        self.tabs.addTab(self.result_tab, "Результат")
        
        self.correct_volume = 0
        self.correct_mass = 0

    def create_theory_tab(self):
        self.theory_tab = QWidget()
        layout = QVBoxLayout()
        
        theory_text = """
        <h2>Определение плотности твердого тела</h2>
        <p>Для определения плотности вещества необходимо измерить массу и объем тела.</p>
        <p>Плотность вычисляется по формуле: ρ = m / V</p>
        <p>Объем можно измерить с помощью мензурки, а массу — с помощью весов.</p>
        """
        theory_text2 = """
        <h3>Мензурка</h3>
        <p>Мензурка — это мерный цилиндр с делениями. При погружении предмета уровень жидкости поднимается. Объем предмета равен разности уровней до и после погружения.</p>
        """

        theory_text3 = """
        <h3>Весы с гирями</h3>
        <p>Весы позволяют определить массу предмета путем подбора гирь до достижения равновесия.</p>
        """

        theory_label = QLabel(theory_text)
        theory_label.setAlignment(Qt.AlignTop)

        theory_label2 = QLabel(theory_text2)
        theory_label2.setAlignment(Qt.AlignTop)

        theory_label3 = QLabel(theory_text3)
        theory_label3.setAlignment(Qt.AlignTop)
        image1_label = QLabel()
        pixmap1 = QPixmap(self.resource_path("menzurka.png")) if hasattr(sys, '_MEIPASS') else QPixmap("menzurka.png")
        image1_label.setPixmap(pixmap1.scaled(300, 200, Qt.KeepAspectRatio))
        
        image2_label = QLabel()
        pixmap2 = QPixmap(self.resource_path("весыпусто.jpg")) if hasattr(sys, '_MEIPASS') else QPixmap("весыпусто.jpg")
        image2_label.setPixmap(pixmap2.scaled(300, 200, Qt.KeepAspectRatio))
        
        layout.addWidget(theory_label)
        layout.addWidget(theory_label2)
        layout.addWidget(image1_label)
        layout.addWidget(theory_label3)
        layout.addWidget(image2_label)
        self.theory_tab.setLayout(layout)

    def create_experiment_tab(self):
        self.experiment_tab = QWidget()
        main_layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.menzurka_widget = MenzurkaWidget()
        splitter.addWidget(self.menzurka_widget)
        
        self.scales_widget = ScalesWidget()
        splitter.addWidget(self.scales_widget)
        
        main_layout.addWidget(splitter)
        
        control_layout = QHBoxLayout()
        self.volume_input = QLineEdit()
        self.mass_input = QLineEdit()
        
        btn_generate = QPushButton("Сгенерировать предмет")
        btn_generate.clicked.connect(self.generate_item)
        btn_immerse = QPushButton("Погрузить предмет")
        btn_immerse.clicked.connect(self.menzurka_widget.start_immersion)
        btn_check = QPushButton("Проверить")
        btn_check.clicked.connect(self.check_answers)
        
        control_layout.addWidget(btn_generate)
        control_layout.addWidget(btn_immerse)
        control_layout.addWidget(QLabel("Объем (мл):"))
        control_layout.addWidget(self.volume_input)
        control_layout.addWidget(QLabel("Масса (г):"))
        control_layout.addWidget(self.mass_input)
        control_layout.addWidget(btn_check)
        
        main_layout.addLayout(control_layout)
        self.experiment_tab.setLayout(main_layout)

    def create_result_tab(self):
        self.result_tab = ResultTab()

    def generate_item(self):
        self.correct_volume = random.choice(range(40, 601, 40))
        self.correct_mass = random.randint(1, 185) * 5
        self.menzurka_widget.generate_item(self.correct_volume)
        self.scales_widget.generate_object(self.correct_mass)

    def check_answers(self):
        try:
            user_volume = int(self.volume_input.text())
            user_mass = int(self.mass_input.text())
            if user_volume == self.correct_volume and user_mass == self.correct_mass:
                if user_mass != 0 and user_volume != 0:
                    self.tabs.setCurrentIndex(2)
                    self.result_tab.update_results(self.correct_volume, self.correct_mass)
                else:
                    QMessageBox.warning(self, "Ошибка", "Сгенерируйте предмет.")
            else:
                QMessageBox.warning(self, "Ошибка", "Неправильные значения.")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите числа.")

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

class MenzurkaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initial_volume = 400
        self.item_volume = 0
        self.animation_progress = 0
        self.is_animating = False
        self.item_generated = False
        self.scale_value = 40
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_immersion)

    def generate_item(self, volume):
        self.item_volume = volume
        self.item_generated = True
        self.update()

    def start_immersion(self):
        if not self.item_generated:
            QMessageBox.warning(self, "Ошибка", "Создайте предмет!")
            return
        if self.initial_volume + self.item_volume > 1000:
            QMessageBox.warning(self, "Ошибка", "Мензурка переполнена!")
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
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        menzurka_x, menzurka_y = 50, 50
        menzurka_width, menzurka_height = 100, 400
        
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
            current_y = start_y + int((self.animation_progress / 100) * (menzurka_y + menzurka_height - liquid_height - start_y))
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawRect(menzurka_x + 25, current_y, 50, item_height)

class ScalesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.mass_object = 0
        self.total_weights = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.update_image('весыпусто.jpg')
        
        self.object_label = QLabel("Масса предмета: неизвестна")
        self.total_label = QLabel("Сумма гирь: 0 г")
        self.indicator_label = QLabel("Сравнение: ")
        
        checkboxes_layout = QHBoxLayout()
        self.checkboxes = []
        weights = [5, 10, 20, 40, 50, 100, 200, 500, 1000]
        for weight in weights:
            checkbox = QCheckBox(f"{weight} г")
            checkbox.stateChanged.connect(self.update_weights)
            self.checkboxes.append(checkbox)
            checkboxes_layout.addWidget(checkbox)
        
        layout.addWidget(self.image_label)
        layout.addWidget(self.object_label)
        layout.addWidget(self.total_label)
        layout.addWidget(self.indicator_label)
        layout.addLayout(checkboxes_layout)
        self.setLayout(layout)

    def generate_object(self, mass):
        self.mass_object = mass
        self.object_label.setText("Предмет создан!")
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        self.total_weights = 0
        self.total_label.setText("Сумма гирь: 0 г")
        self.indicator_label.setText("Сравнение: ")
        self.update_image('весыпусто.jpg')

    def update_weights(self):
        self.total_weights = sum(weight for checkbox, weight in zip(self.checkboxes, [5,10,20,40,50,100,200,500,1000]) if checkbox.isChecked())
        self.total_label.setText(f"Сумма гирь: {self.total_weights} г")
        
        if self.total_weights < self.mass_object:
            self.indicator_label.setText("Сравнение: меньше")
            self.update_image('весыбольше.jpg')
        elif self.total_weights > self.mass_object:
            self.indicator_label.setText("Сравнение: больше")
            self.update_image('весыменьше.jpg')
        else:
            self.indicator_label.setText("Сравнение: равны")
            self.update_image('весыравно.jpg')

    def update_image(self, image_name):
        pixmap = QPixmap(self.resource_path(image_name))
        self.image_label.setPixmap(pixmap.scaled(300, 200, Qt.KeepAspectRatio))

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

class ResultTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        formula_label = QLabel()
        pixmap = QPixmap("formula.png") if os.path.exists("formula.png") else QPixmap()
        formula_label.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio))
        
        self.volume_result = QLabel("Объем: ")
        self.mass_result = QLabel("Масса: ")
        self.density_input = QLineEdit()
        
        btn_check = QPushButton("Проверить плотность")
        btn_check.clicked.connect(self.check_density)
        
        layout.addWidget(formula_label)
        layout.addWidget(self.volume_result)
        layout.addWidget(self.mass_result)
        layout.addWidget(QLabel("Плотность (г/мл):"))
        layout.addWidget(self.density_input)
        layout.addWidget(btn_check)
        self.setLayout(layout)

    def update_results(self, volume, mass):
        self.volume_result.setText(f"Объем: {volume} мл")
        self.mass_result.setText(f"Масса: {mass} г")
        self.correct_density = mass / volume if volume != 0 else 0

    def check_density(self):
        try:
            user_density = round(float(self.density_input.text()), 2)
            correct = round(self.correct_density, 2)
            if user_density == correct:
                QMessageBox.information(self, "Успех", "Верно!")
            else:
                QMessageBox.warning(self, "Ошибка", f"Неверно. Правильно: {correct}")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите число.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())