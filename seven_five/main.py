import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, 
                            QMessageBox)
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, Qt, QEasingCurve
from PyQt6.QtGui import QPainter, QPainterPath, QPen
from PyQt6.QtGui import QColor, QPainterPath, QBrush

class SpringWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self._spring_length = 100
        self.k = 80  # Жесткость пружины (Н/м)
        self.pixels_per_meter = 400  # Масштаб (400 пикселей = 1 м)
        self.current_mass = 0  # Добавляем свойство для хранения массы

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        x_center, y_start = 200, 50
        num_coils = 8
        coil_spacing = self._spring_length / num_coils
        spring_width = 40
        
        path = QPainterPath()
        path.moveTo(x_center, y_start)
        
        for i in range(num_coils):
            control_y = y_start + coil_spacing * (i + 0.5)
            if i % 2 == 0:
                path.cubicTo(x_center + spring_width, y_start + coil_spacing*i,
                             x_center + spring_width, control_y,
                             x_center, y_start + coil_spacing*(i+1))
            else:
                path.cubicTo(x_center - spring_width, y_start + coil_spacing*i,
                             x_center - spring_width, control_y,
                             x_center, y_start + coil_spacing*(i+1))
        
        painter.setPen(QPen(Qt.GlobalColor.black, 3))
        painter.drawPath(path)
        self.draw_scale(painter)
        if self._spring_length > 100:
            self.draw_weight(painter)

    def draw_scale(self, painter):
        scale_x = 300
        scale_top = 50
        scale_bottom = 350
        cm_length = (self._spring_length - 100) / self.pixels_per_meter * 100
        
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(scale_x, scale_top, scale_x, scale_bottom)
        
        # for i in range(11):
        #     y_pos = scale_top + i * 30
        #     painter.drawLine(scale_x - 10, y_pos, scale_x + 10, y_pos)
        #     painter.drawText(scale_x + 15, y_pos + 5, f"{i}")
        
        pointer_y = 50 + (self._spring_length - 100)
        painter.setBrush(Qt.GlobalColor.red)
        painter.drawEllipse(scale_x - 5, pointer_y - 5, 10, 10)
        painter.drawText(scale_x - 30, pointer_y + 5, f"{cm_length:.1f} см")


    def draw_weight(self, painter):
        # Настройки внешнего вида груза
        weight_color = QColor(139, 69, 19)  # Коричневый
        size = 40 + self.current_mass * 15  # Размер зависит от массы
        
        # Координаты груза
        x = 200 - size//2
        y = 50 + self._spring_length + 10
        
        # Рисуем груз с тенью
        painter.setPen(QPen(QColor(70, 70, 70), 2))
        painter.setBrush(QBrush(weight_color))
        
        # Основная форма
        path = QPainterPath()
        path.moveTo(x + size//2, y)
        path.arcTo(x, y, size, size, 0, 180)  # Полуокружность
        path.addRect(x, y + size//2, size, size//2)  # Прямоугольная часть
        painter.drawPath(path)
        
        # Крюк
        painter.drawLine(200, 50 + self._spring_length, 200, y)

    def get_spring_length(self):
        return self._spring_length

    def set_spring_length(self, value):
        self._spring_length = value
        self.update()

    spring_length = pyqtProperty(int, get_spring_length, set_spring_length)

class TheoryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        theory_text = """
        <h2>Работа с динамометром</h2>
        <p>Динамометр - прибор для измерения силы.</p>
        
        <h3>Основные понятия:</h3>
        <ul>
            <li><b>Сила (F)</b> - физическая величина, измеряется в Ньютонах (Н)</li>
            <li><b>Масса (m)</b> - измеряется в килограммах (кг)</li>
            <li><b>Ускорение свободного падения (g)</b> ≈ 9.81 м/с²</li>
            <li><b>Жесткость пружины в этом эксперименте равна 80Н/м при работе с сантиметрами поделите на 100</li>
        </ul>
        
        <h3>Закон Гука:</h3>
        <p>F = k · x</p>
        <p>где:<br>
        F - сила упругости (Н)<br>
        k - жесткость пружины (Н/м)<br>
        x - удлинение пружины (м)</p>
        
        <h3>Формула веса тела:</h3>
        <p>P = m · g</p>
        """
        self.text_edit.setText(theory_text)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

class ExperimentTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_mass = 0
        self.initUI()
        self.weight_animation = None

    def initUI(self):
        layout = QVBoxLayout()
        
        self.spring = SpringWidget()
        layout.addWidget(self.spring)
        
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Сгенерировать предмет")
        self.generate_btn.clicked.connect(self.generate_object)
        self.hang_btn = QPushButton("Повесить предмет")
        self.hang_btn.setEnabled(False)
        self.hang_btn.clicked.connect(self.toggle_object)
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.hang_btn)
        
        layout.addLayout(btn_layout)
        
        self.force_input = QLineEdit()
        self.force_input.setPlaceholderText("Определите силу (Н)")
        self.mass_input = QLineEdit()
        self.mass_input.setPlaceholderText("Какова масса предмета? (кг)")
        self.check_btn = QPushButton("Проверить")
        self.check_btn.clicked.connect(self.check_answers)
        
        layout.addWidget(QLabel("Введите ответы:"))
        layout.addWidget(self.force_input)
        layout.addWidget(self.mass_input)
        layout.addWidget(self.check_btn)
        
        self.setLayout(layout)

    def generate_object(self):
        self.current_mass = round(random.uniform(0.5, 5.0), 2)
        QMessageBox.information(self, "Новый предмет", f"Сгенерирован предмет с массой {self.current_mass:.2f} кг")
        self.hang_btn.setEnabled(True)        
        self.mass_indicator = QLabel(f"Масса: {self.current_mass} кг")
        self.mass_indicator.setStyleSheet("""
            QLabel {
                background: #FFEBCD;
                border: 2px solid #DEB887;
                padding: 5px;
                border-radius: 10px;
            }
        """)
        self.layout().addWidget(self.mass_indicator)

    def toggle_object(self):
        if self.spring.spring_length == 100:
            g = 9.81
            force = self.current_mass * g
            delta_x = force / self.spring.k  # В метрах
            target_length = 100 + int(delta_x * self.spring.pixels_per_meter)
            self.animate_spring(target_length)
            self.hang_btn.setText("Снять предмет")            
            self.spring.current_mass = self.current_mass  # Передаем массу
            self.animate_weight(show=True)
        else:
            self.animate_weight(show=False)
            self.animate_spring(100)
            self.hang_btn.setText("Повесить предмет")

    def animate_weight(self, show=True):
        # Анимация появления/исчезновения груза
        self.weight_animation = QPropertyAnimation(self.spring, b"opacity")
        self.weight_animation.setDuration(500)
        self.weight_animation.setStartValue(0 if show else 1)
        self.weight_animation.setEndValue(1 if show else 0)
        self.weight_animation.start()

    def animate_spring(self, target):
        self.anim = QPropertyAnimation(self.spring, b"spring_length")
        self.anim.setDuration(1000)
        self.anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.anim.setStartValue(self.spring.spring_length)
        self.anim.setEndValue(target)
        self.anim.start()

    def check_answers(self):
        g = 9.81
        correct_force = round(self.current_mass * g, 2)
        
        try:
            user_force = float(self.force_input.text())
            user_mass = float(self.mass_input.text())
            if abs(user_force - correct_force) < 0.5 and abs(user_mass - self.current_mass) < 1:
                QMessageBox.information(self, "Результат", "Все верно!")
            else:
                print(correct_force, self.current_mass)
                QMessageBox.warning(self, "Результат", "Попробуйте еще раз.")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите числовые значения.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Виртуальная лаборатория - Динамометр")
        self.setFixedSize(800, 600)
        
        tabs = QTabWidget()
        tabs.addTab(TheoryTab(), "Теория")
        tabs.addTab(ExperimentTab(), "Эксперимент")
        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())