import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QPushButton, QCheckBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap  # убедитесь, что добавили этот импорт в начало файла

class VirtualLab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Виртуальная лаборатория")
        self.setGeometry(100, 100, 600, 400)

        self.mass_object = 0
        self.total_weights = 0

        self.weights_image_label = QLabel()

        # Основной виджет с вкладками
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладки
        self.work_tab = self.create_work_tab()
        self.experiment_tab = self.create_experiment_tab()
        self.tabs.addTab(self.work_tab, "Ход работы")
        self.tabs.addTab(self.experiment_tab, "Эксперимент")

    def create_work_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Добавление текста
                
        self.image_label = QLabel()
        pixmap = QPixmap(self.resource_path("весыпусто.jpg"))  # Загрузка изображения с использованием метода resource_path
        self.image_label.setPixmap(pixmap)  # Установка изображения в QLabel

        layout.addWidget(self.image_label)
        layout.addWidget(QLabel("""    <h3>Как пользоваться весами с гирями?</h3>
        <div>
            <p>Для того, чтобы правильно использовать весы с гирями, выполните следующие шаги:</p>
            <ol>
                <li>Кладите гирю большей массы, чем предполагаемый вес предмета.</li>
                <li>Заменяйте гирю меньшей массой до тех пор, пока предмет не будет уравновешен.</li>
                <li>Когда масса гирь начнет приближаться к массе предмета, арретир открывают и наблюдают за качанием стрелки, до ее совпадения с нулевым уровнем.</li>
            </ol>
            <p><em>Не забывайте следить за точностью измерений и внимательно наблюдать за результатом!</em></p>
        </div>"""))

        tab.setLayout(layout)
        return tab
    def create_experiment_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.update_image('весыпусто.jpg')  # строка 35 (для установки пустых весов при запуске)э

        # Кнопка для создания предмета
        self.create_button = QPushButton("Создать предмет")
        self.create_button.clicked.connect(self.generate_object)
        layout.addWidget(self.create_button)

        # Информация о предмете
        self.object_label = QLabel("Масса предмета: неизвестна")
        layout.addWidget(self.object_label)

        # Сумма гирь
        self.total_label = QLabel("Сумма гирь: 0 грамм")
        layout.addWidget(self.total_label)

        # Индикатор больше/меньше
        self.indicator_label = QLabel("Сравнение: ")
        layout.addWidget(self.indicator_label)

        # Переключатели для гирь (набор гирь: 5 г, 10 г, 20 г, 40 г, 50 г, 100 г, 200 г, 500 г, 1000 г)
        self.weights = [5, 10, 20, 40, 50, 100, 200, 500, 1000]
        self.checkboxes = []
        checkboxes_layout = QHBoxLayout()
        for weight in self.weights:
            checkbox = QCheckBox(f"{weight} г")
            checkbox.stateChanged.connect(self.update_weights)
            self.checkboxes.append(checkbox)
            checkboxes_layout.addWidget(checkbox)

        layout.addLayout(checkboxes_layout)

        # Сообщение об успехе
        self.message_label = QLabel("")
        layout.addWidget(self.message_label)

        
        self.weights_image_label = QLabel()
        self.update_image('весыпусто.jpg')  # строка 35
        

        layout.addWidget(self.weights_image_label)

        tab.setLayout(layout)
        return tab

    def generate_object(self):
        # Генерация случайной массы объекта от 5 до 885 с шагом 5
        self.mass_object = random.randint(1, 200) * 5
        self.object_label.setText(f"Предмет создан!")
        self.message_label.setText("")  # Очистить сообщение
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        self.total_weights = 0
        self.total_label.setText("Сумма гирь: 0 грамм")
        self.indicator_label.setText("Сравнение: ")

    def update_weights(self):
        # Обновление суммы гирь
        self.total_weights = sum(
            weight for checkbox, weight in zip(self.checkboxes, self.weights) if checkbox.isChecked()
        )
        self.total_label.setText(f"Сумма гирь: {self.total_weights} грамм")

        # Обновление индикатора сравнения
        if self.total_weights < self.mass_object:
            self.indicator_label.setText("Сравнение: меньше")
            self.update_image('весыбольше.jpg')  # Обновляем изображение
        elif self.total_weights > self.mass_object:
            self.indicator_label.setText("Сравнение: больше")
            self.update_image('весыменьше.jpg')  # Обновляем изображение
        else:
            self.indicator_label.setText("Сравнение: равны")
            self.update_image('весыравно.jpg')  # Обновляем изображение

        # Проверка на успех
        if self.total_weights == self.mass_object:
            self.message_label.setText("Успешно!")
        else:
            self.message_label.setText("")
    def update_image(self, image_name):
    # Загрузка изображения и обновление отображения
        pixmap = QPixmap(self.resource_path(image_name))
        
        self.weights_image_label.setPixmap(pixmap.scaled(300, 200))  # Подгоняем размер изображения
    
    def resource_path(self, relative_path):
        """ Получение абсолютного пути к ресурсу, работает для сборок и разработки """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualLab()
    window.show()
    sys.exit(app.exec_())
