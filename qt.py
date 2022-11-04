# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget, QGridLayout, QLabel
from PyQt5.QtGui import QFont, QFontDatabase, QIcon, QImage, QPixmap

# from blurWindow import GlobalBlur

import sys
import cv2
import numpy as np


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    changeDetectState = pyqtSignal(int)
    changeDetectInfo = pyqtSignal(list)

    def run(self):
        capture = cv2.VideoCapture(0)

        while True:
            _, frame = capture.read()
            if frame is None or frame.size == 0:
                continue

            image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            bgr_image = cv2.resize(image, dsize=(480, 360))
            hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

            # bin_image = cv2.inRange(hsv_image, (0, 0, 0), (4, 255, 160))
            bin_image = cv2.inRange(hsv_image, (103, 105, 130),
                                    (180, 255, 255))
            out_image = bgr_image
            num_labels, _, stats, center = cv2.connectedComponentsWithStats(
                bin_image)

            num_labels = num_labels - 1
            stats = np.delete(stats, 0, 0)
            center = np.delete(center, 0, 0)

            if num_labels >= 1:
                max_index = np.argmax(stats[:, 4])

                x = stats[max_index][0]
                y = stats[max_index][1]
                w = stats[max_index][2]
                h = stats[max_index][3]
                s = stats[max_index][4]

                if s >= 700:
                    cv2.rectangle(out_image, (x, y), (x + w, y + h),
                                  (255, 0, 255))
                    cv2.putText(out_image, 'RED DETECTED', (x, y + h + 15),
                                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

                    self.changeDetectState.emit(True)
                    self.changeDetectInfo.emit([True, num_labels, s])
                else:
                    self.changeDetectState.emit(False)
                    self.changeDetectInfo.emit([False, 0, 0])

            height, width, channel = out_image.shape

            qImg = QImage(out_image.data, width, height, channel * width,
                          QImage.Format_RGB888)
            pixmap = qImg.scaled(540, 540, Qt.KeepAspectRatio)

            self.changePixmap.emit(pixmap)


class RedDetectionApp(QWidget):
    state = False

    def __init__(self):
        super(RedDetectionApp, self).__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        grid.setContentsMargins(0, 0, 0, 0)

        self.imgLabel = QLabel(self)
        self.stateLabel = QLabel(self)
        self.infoLabel = QLabel(self)

        print(self.state)
        # self.imgLabel.setStyleSheet('background-color: rgba(0, 0, 0, 0);')
        self.stateLabel.setStyleSheet(
            'font-family: "Pretendard", sans-serif;'
            'font-size: 16pt;'
            'font-weight: 600;'
            'color: red;' if self.state else 'color: black;'
            'margin: 12px 16px 0 16px;'
            # 'background-color: rgba(0, 0, 0, 0);'
        )
        # self.infoLabel.setStyleSheet('background-color: rgba(0, 0, 0, 0);')
        self.infoLabel.setStyleSheet('font-family: "Pretendard", sans-serif;'
                                     'font-size: 11pt;'
                                     'font-weight: 500;'
                                     'color: #374151;'
                                     'margin: 0 20px 16px 20px;')

        grid.addWidget(self.imgLabel, 0, 0)
        grid.addWidget(self.stateLabel, 1, 0)
        grid.addWidget(self.infoLabel, 2, 0)

        th = Thread(parent=self)
        th.changePixmap.connect(self.setImage)
        th.changeDetectState.connect(self.setState)
        th.changeDetectInfo.connect(self.setInfo)
        th.start()

        self.setWindowTitle('Detect RED')
        self.setWindowIcon(QIcon('icon.png'))
        self.center()

        # GlobalBlur(self.winId(), Dark=True, QWidget=self)
        # self.setStyleSheet('background-color: rgba(0, 0, 0, 0.7)')
        self.setStyleSheet('background-color: #f9f9f9')

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.imgLabel.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(int)
    def setState(self, state):
        self.state = state
        self.stateLabel.setText(
            '빨간색이 감지되었습니다!' if state else '빨간색이 감지되지 않았습니다.')

    @pyqtSlot(list)
    def setInfo(self, info):
        self.infoLabel.setText('발견된 빨간 물체 수 {0}  |  가장 큰 물체 크기 {1}'.
                               format(info[1], info[2]) if info[0] else '-')


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fontDB = QFontDatabase()
    fontDB.addApplicationFont('./pretendard/Pretendard-Thin.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-ExtraLight.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-Light.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-Regular.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-Medium.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-SemiBold.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-ExtraBold.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-Bold.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-Black.ttf')
    app.setFont(QFont('Pretendard'))

    ex = RedDetectionApp()
    sys.exit(app.exec_())
