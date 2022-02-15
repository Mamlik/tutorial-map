import sys
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
import requests
from consts import map_api_server, FORMATS, map_move_speed, delta, geocoder_api_server
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()  # required params: map_layer, toponym_longitude, toponym_lattitude, delta
        uic.loadUi('design.ui', self)
        self.setWindowTitle('YandexMaps')
        self.toponym_longitude, self.toponym_lattitude = "37.617734", "55.752004"
        self.map_layer = "map"
        self.delta = delta
        self.show_map()
        self.sheme_btn.clicked.connect(self.layer_clicked)
        self.sat_btn.clicked.connect(self.layer_clicked)
        self.hyb_btn.clicked.connect(self.layer_clicked)
        self.search_btn.clicked.connect(self.search_adress)

    def show_map(self):
        map_params = {
            "ll": ",".join([self.toponym_longitude, self.toponym_lattitude]),
            "spn": ",".join([self.delta, self.delta]),
            "l": self.map_layer,
            "pt": ",".join([self.toponym_longitude, self.toponym_lattitude, "pm2rdm"])
        }
        response = requests.get(map_api_server, params=map_params)

        print(response.url)

        if not response:
            self.internet_connection_error()
        pixmap = QPixmap()
        pixmap.loadFromData(QtCore.QByteArray(response.content), FORMATS[self.map_layer])
        self.img_lbl.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.delta = str(float(self.delta) / 2)
            if float(self.delta) < 0.0009:
                self.delta = '0.0009'
            self.show_map()

        elif event.key() == Qt.Key_Down:
            self.delta = str(float(self.delta) * 2)
            if float(self.delta) > 50:
                self.delta = '50'
            self.show_map()

        elif event.key() == Qt.Key_D:
            self.toponym_longitude = str(float(self.toponym_longitude) + float(self.delta))  # СДВИГ ПРОИСХОДИТ
            # НЕ НА ШИРИНУ ЭКРАНА, А НА ПОЛОВИНУ ЭКРАНА ДЛЯ УДОБСТВА
            self.show_map()

        elif event.key() == Qt.Key_A:
            self.toponym_longitude = str(float(self.toponym_longitude) - float(self.delta))  # СДВИГ ПРОИСХОДИТ
            # НЕ НА ШИРИНУ ЭКРАНА, А НА ПОЛОВИНУ ЭКРАНА ДЛЯ УДОБСТВА
            self.show_map()

        elif event.key() == Qt.Key_W:
            self.toponym_lattitude = str(float(self.toponym_lattitude) + float(self.delta))  # СДВИГ ПРОИСХОДИТ
            # НЕ НА ШИРИНУ ЭКРАНА, А НА ПОЛОВИНУ ЭКРАНА ДЛЯ УДОБСТВА
            self.show_map()

        elif event.key() == Qt.Key_S:
            self.toponym_lattitude = str(float(self.toponym_lattitude) - float(self.delta))
            self.show_map()

    def layer_clicked(self):
        button = QApplication.instance().sender()
        if button.text() == 'Схема':
            self.map_layer = 'map'
            self.show_map()

        if button.text() == 'Спутник':
            self.map_layer = 'sat'
            self.show_map()

        if button.text() == 'Гибрид':
            self.map_layer = 'sat,skl'
            self.show_map()

    def search_adress(self):
        user_request = self.adress_edit.text()
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": user_request,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            self.internet_connection_error()
        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            self.toponym_longitude, self.toponym_lattitude = toponym_longitude, toponym_lattitude
            self.show_map()
        except IndexError:
            self.object_not_found_error()

    def internet_connection_error(self):
        msg = QMessageBox()
        msg.setWindowTitle("Ошибка")
        msg.setText("Интернет соединение не найдено")
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()

    def object_not_found_error(self):
        msg = QMessageBox()
        msg.setWindowTitle("Ошибка")
        msg.setText("Объект не найден")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    auth = MainWindow()
    auth.show()
    sys.exit(app.exec())