import sys
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
import requests
from consts import map_api_server, FORMATS
from PyQt5.QtCore import Qt
import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # required params: map_layer, toponym_longitude, toponym_lattitude, delta
        uic.loadUi('design.ui', self)
        self.setWindowTitle('YandexMaps')
        self.toponym_longitude, self.toponym_lattitude = "37.617734", "55.752004"
        self.map_layer = "map"
        self.z = 15
        # Добавил размер шага для смещения изображения
        self.step = 0.3
        self.show_map()

    def show_map(self):
        map_params = {
            "ll": ",".join([self.toponym_longitude, self.toponym_lattitude]),
            "z": self.z,
            "l": self.map_layer,
        }
        response = requests.get(map_api_server, params=map_params)
        if not response:
            #  todo cause connection exception
            pass
        pixmap = QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(response.content), FORMATS[self.map_layer])
        self.img_lbl.setPixmap(pixmap)
        self.sheme_btn.clicked.connect(self.layer_clicked)
        self.sat_btn.clicked.connect(self.layer_clicked)
        self.hyb_btn.clicked.connect(self.layer_clicked)

    def keyPressEvent(self, event):

        # Заменил названия обрабатываемых клавиш
        if event.key() == Qt.Key_PageUp:
            self.z += 1
            if self.z < 0 or self.z > 19:
                self.z -= 1
            self.show_map()

        elif event.key() == Qt.Key_PageDown:
            self.z -= 1
            if self.z < 0 or self.z > 19:
                self.z += 1
            self.show_map()


        # Добавил обработку кнопок для смещения и кнопку выхода
        elif event.key() == Qt.Key_Right:
            self.toponym_longitude = str(float(self.toponym_longitude) + self.step)
            self.show_map()

        elif event.key() == Qt.Key_Left:
            self.toponym_longitude = str(float(self.toponym_longitude) - self.step)
            self.show_map()

        elif event.key() == Qt.Key_Up:
            self.toponym_lattitude = str(float(self.toponym_lattitude) + self.step)
            self.show_map()

        elif event.key() == Qt.Key_Down:
            self.toponym_lattitude = str(float(self.toponym_lattitude) - self.step)
            self.show_map()

        elif event.key() == Qt.Key_Escape:
            exit()



    def layer_clicked(self):
        button = QApplication.instance().sender()
        print(button.text())

        if button.text() == 'Схема':
            self.map_layer = 'map'
            self.show_map()

        if button.text() == 'Спутник':
            self.map_layer = 'sat'
            self.show_map()

        if button.text() == 'Гибрид':
            self.map_layer = 'sat,skl'
            self.show_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth = MainWindow()
    auth.show()
    sys.exit(app.exec())