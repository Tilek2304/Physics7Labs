import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QVBoxLayout, QFormLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt5.QtCore import Qt, QRect

class VirtualLab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Lab")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.image_result_label = QLabel()  # Инициализация image_result_label
        
        self.create_tabs()
        
    def create_tabs(self):
        self.work_tab = QWidget()
        self.experiment_tab = QWidget()
        
        self.tabs.addTab(self.work_tab, "Ход работы")
        self.tabs.addTab(self.experiment_tab, "Эксперимент")
        
        self.create_work_tab()
        self.create_experiment_tab()
        
    def create_work_tab(self):
        layout = QVBoxLayout()
        self.image_label = QLabel()
        pixmap = QPixmap(self.resource_path("teory.jpg"))  # Загрузка изображения с использованием метода resource_path
        self.image_label.setPixmap(pixmap)  # Установка изображения в QLabel
        self.text_edit = QTextEdit()
        self.text_edit.setHtml("""
            <p>Чтобы подсчитать цену делений шкалы, нужно:</p>
            <ul>
                <li>а) выбрать на шкале два ближайших оцифрованных штриха;</li>
                <li>б) сосчитать количество делений между ними;</li>
                <li>в) разность значений около выбранных штрихов разделить на количество делений.</li>
            </ul>
        """)
        layout.addWidget(self.image_label)
        layout.addWidget(self.text_edit)
        self.work_tab.setLayout(layout)
        
    def create_experiment_tab(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.answer1 = QLineEdit()
        self.answer2 = QLineEdit()
        self.answer3 = QLineEdit()
        self.answer4 = QLineEdit()
        
        form_layout.addRow("Полный обьем мензурки:", self.answer1)
        form_layout.addRow("Значение первого снизу оцифрованного штриха:", self.answer2)
        form_layout.addRow("Объем жидкости между 2-м и 3-м неоцифрованными штрихами:", self.answer3)
        form_layout.addRow("Объем налитой воды:", self.answer4)
        
        layout.addLayout(form_layout)
        
        self.burette = Burette()
        layout.addWidget(self.burette)
        
        button_layout = QHBoxLayout()
        self.fill_button = QPushButton("Наполнить")
        self.check_button = QPushButton("Проверка")
        
        self.fill_button.clicked.connect(self.fill_burette)
        self.check_button.clicked.connect(self.check_answers)
        
        button_layout.addWidget(self.fill_button)
        button_layout.addWidget(self.check_button)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.image_result_label)  # Добавляем QLabel для изображения результата
        
        self.experiment_tab.setLayout(layout)
        
    def fill_burette(self):
        self.burette.fill_random()
        
    def check_answers(self):
        level = self.burette.level
        answer1 = self.answer1.text()
        answer2 = self.answer2.text()
        answer3 = self.answer3.text()
        answer4 = self.answer4.text()

        if answer1 != '100' or answer2 != '20' or answer3 != '4' or answer4 != str(level * 4):
            self.show_warning()
            print("проебался, ответ: ", level * 4, ' а ты ввел: ', answer4)
        else:
            self.show_success()
            self.show_image_result(self.resource_path("palchik_verh.jpg"))  # Путь к изображению результата
            print('хорош')
            
    def show_success(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Успех")
        msg.setText("Успешно! Все ответы правильные.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_warning(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Ошибка")
        msg.setText("Неверно! Вы где-то ошиблись.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_image_result(self, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)  # Ограничиваем размер изображения
        self.image_result_label.setPixmap(pixmap)

    def resource_path(self, relative_path):
        """ Получение абсолютного пути к ресурсу, работает для сборок и разработки """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

class Burette(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(150, 450)  # Увеличиваем размер мензурки в 1.5 раза
        self.level = 0
        
    def fill_random(self):
        import random
        self.level = random.randint(1, 24)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = QRect(55, 15, 60, 300)  # Увеличиваем размеры прямоугольника и ставим его по центру
        painter.drawRect(rect)
        painter.setPen(QPen(Qt.black, 2))
        
        for i in range(6):
            y = 315 - i * 60  # Увеличиваем расстояние между делениями
            painter.drawLine(55, y, 115, y)  # Увеличиваем ширину линий делений
            painter.drawText(25, y + 5, str(i * 20))  # Ставим метки ближе к центру
            if i != 5:
                for j in range(1, 5):
                    y_sub = y - j * 12  # Увеличиваем расстояние между промежуточными делениями
                    painter.drawLine(65, y_sub, 105, y_sub)  # Увеличиваем ширину промежуточных линий
                
        painter.setBrush(QColor(0, 0, 255, 128))
        painter.drawRect(55, 315 - self.level * 12, 60, self.level * 12)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualLab()
    window.show()
    sys.exit(app.exec_())
