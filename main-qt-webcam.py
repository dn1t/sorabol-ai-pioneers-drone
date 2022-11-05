# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QWidget, QGridLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QBrush, QColor, QFont, QFontDatabase, QIcon, QImage, QPixmap, QPainter

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
            radius = 12

            rounded = QPixmap(pixmap.size())
            rounded.fill(QColor('transparent'))

            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(pixmap))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(pixmap.rect(), radius, radius)
            painter.end()

            self.changePixmap.emit(rounded.toImage())


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
        self.stateLabel = QLabel(self, text='빨간색이 감지되지 않았습니다.')
        self.infoLabel = QLabel(self, text='-')

        self.imgLabel.setStyleSheet('margin: 16px 0 0 16px;')
        self.stateLabel.setStyleSheet('font-family: "Pretendard", sans-serif;'
                                      'font-size: 16pt;'
                                      'font-weight: 600;'
                                      'color: black;'
                                      'margin: 12px 16px 0 16px;')
        self.infoLabel.setStyleSheet('font-family: "Pretendard", sans-serif;'
                                     'font-size: 11pt;'
                                     'font-weight: 500;'
                                     'color: #374151;'
                                     'margin: 0 19px 0 19px;')

        grid.addWidget(self.imgLabel, 0, 0)
        grid.addWidget(self.stateLabel, 1, 0)
        grid.addWidget(self.infoLabel, 2, 0)

        statusBarLayout = QGridLayout()

        devLabel = QLabel(self, text='11216 이다윗, 11104 김영동, 11111 안의찬')
        devLabel.setStyleSheet('font-family: "Pretendard", sans-serif;'
                               'font-size: 9pt;'
                               'font-weight: 500;'
                               'color: #6b7280;'
                               'margin: 4px 20px 12px 20px;')

        self.batteryLabel = QLabel(self, text='배터리 100%')
        self.batteryLabel.setStyleSheet(
            'font-family: "Pretendard", sans-serif;'
            'font-size: 9pt;'
            'font-weight: 500;'
            'color: #374151;'
            'margin: 4px 20px 12px 20px;')

        statusBarLayout.addWidget(devLabel, 0, 0)
        statusBarLayout.addWidget(self.batteryLabel, 0, 1, Qt.AlignRight)

        grid.addLayout(statusBarLayout, 3, 0, 1, 2)

        controllerLayout = QVBoxLayout()
        controllerLayout.setContentsMargins(0, 0, 0, 0)

        grid.addLayout(controllerLayout, 0, 1, 3, 1)

        tipTitleLabel = QLabel(self, text='키보드로 조종하기')
        tipTitleLabel.setStyleSheet('font-family: "Pretendard", sans-serif;'
                                    'font-size: 10pt;'
                                    'font-weight: 600;'
                                    'color: #374151;'
                                    'margin: 18px 16px 2px 8px;')

        tipLabel = QLabel(self,
                          text='\n'.join([
                              'W: 앞으로 이동', 'S: 뒤로 이동', 'A: 왼쪽으로 이동',
                              'D: 오른쪽으로 이동', '', 'Up: 상승', 'Down: 하강',
                              'Left: -90° 회전', 'Right: 90° 회전', '', 'T: 이륙',
                              'L: 착륙', 'F: 플립'
                          ]))
        tipLabel.setStyleSheet('font-family: "Pretendard", sans-serif;'
                               'font-size: 9pt;'
                               'font-weight: 500;'
                               'color: #6b7280;'
                               'margin: 2px 48px 16px 10px;')

        controllerLayout.addWidget(tipTitleLabel)
        controllerLayout.addWidget(tipLabel)
        controllerLayout.addStretch(1)

        th = Thread(parent=self)
        th.changePixmap.connect(self.setImage)
        th.changeDetectState.connect(self.setState)
        th.changeDetectInfo.connect(self.setInfo)
        th.start()

        self.setWindowTitle('Detect RED')
        self.setWindowIcon(QIcon('icon.png'))
        self.center()

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
        if state:
            self.stateLabel.setStyleSheet(
                'font-family: "Pretendard", sans-serif;'
                'font-size: 16pt;'
                'font-weight: 600;'
                'color: red;'
                'margin: 12px 16px 0 16px;')
            self.stateLabel.setText('빨간색이 감지되었습니다!')
        else:
            self.stateLabel.setStyleSheet(
                'font-family: "Pretendard", sans-serif;'
                'font-size: 16pt;'
                'font-weight: 600;'
                'color: black;'
                'margin: 12px 16px 0 16px;')
            self.stateLabel.setText('빨간색이 감지되지 않았습니다.')

    @pyqtSlot(list)
    def setInfo(self, info):
        self.infoLabel.setText('발견된 빨간 물체 수 {0}  |  가장 큰 물체 크기 {1}'.
                               format(info[1], info[2]) if info[0] else '-')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_F:
            self.showFullScreen()
        elif e.key() == Qt.Key_N:
            self.showNormal()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    fontDB = QFontDatabase()
    fontDB.addApplicationFont('./pretendard/Pretendard-Medium.ttf')
    fontDB.addApplicationFont('./pretendard/Pretendard-SemiBold.ttf')
    app.setFont(QFont('Pretendard'))

    ex = RedDetectionApp()
    sys.exit(app.exec_())
