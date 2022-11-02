# -*- coding: utf-8 -*-

import cv2
from Tkinter import *
from ctypes import windll
from PIL import Image, ImageTk
import numpy as np
import pyglet

pyglet.font.add_file('pretendard-light.ttf')


def main():
    capture = cv2.VideoCapture(0)
    window = Tk()
    window.config(bg='white')

    window.title('Detect RED')
    # window.resizable(False, False)

    imgLabel = Label(window, borderwidth=0)
    imgLabel.pack()

    frame = Frame(window, relief='solid', pady=20, bg='white', borderwidth=0)
    frame.pack()

    textLabel = Label(frame,
                      text='빨간색이 감지되지 않았습니다.',
                      font=('Pretendard JP', 15),
                      fg='red',
                      bg='white')
    textLabel.pack()

    infoLabel = Label(frame,
                      text='-',
                      font=('Pretendard JP', 11),
                      fg='#374151',
                      bg='white')
    infoLabel.pack()

    devLabel = Label(frame,
                     text='11216 이다윗, 11104 김영동, 11111 안의찬',
                     font=('Pretendard JP', 10),
                     fg='#6b7280',
                     bg='white')
    devLabel.pack()

    def video_stream():
        _, frame = capture.read()
        if frame is None or frame.size == 0:
            return

        image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        bgr_image = cv2.resize(image, dsize=(480, 360))
        hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

        # bin_image = cv2.inRange(hsv_image, (0, 0, 0), (4, 255, 160))
        bin_image = cv2.inRange(hsv_image, (103, 105, 130), (180, 255, 255))
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
                cv2.rectangle(out_image, (x, y), (x + w, y + h), (255, 0, 255))
                cv2.putText(out_image, 'RED DETECTED', (x, y + h + 15),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
                textLabel.config(text='빨간색이 감지되었습니다.', fg='#10b981')
                infoLabel.config(
                    text='발견된 빨간 물체 수 {0}  |  가장 큰 물체 크기 {1}'.format(
                        num_labels, s))
            else:
                textLabel.config(text='빨간색이 감지되지 않았습니다.', fg='red')
                infoLabel.config(text='-')

        imgTk = ImageTk.PhotoImage(Image.fromarray(out_image))
        imgLabel.imgtk = imgTk
        imgLabel.configure(image=imgTk)
        imgLabel.after(1, video_stream)

    video_stream()
    window.mainloop()


if __name__ == '__main__':
    main()
