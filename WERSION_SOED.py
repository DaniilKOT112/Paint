import os
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QColorDialog, QSlider, \
    QFileDialog, QLabel, QMenu, QAction
from PyQt5.QtGui import QPainter, QPen, QImage, QColor, QPixmap, QPainterPath, QIcon, QCursor
from PyQt5.QtCore import Qt, QPoint, QSize
import random
from qt_material import apply_stylesheet

BgColor = QColor()  # цвет холста
BgColor.setNamedColor('white')

BrColor = QColor()  # цвет инструмента
BrColor.setNamedColor('black')

dictionary = {'width': 877,
              'height': 620,
              'BrSize': 10,
              'BgColor': BgColor.name(),
              'BrColor': BrColor.name(),
              'tool': 'brush'}

directory = os.path.abspath(os.curdir)


class Painter(QWidget):
    def __init__(self):
        super().__init__()
        global color
        self.drawing = True
        self.BrStyle = QPen()
        self.lastPoint = QPoint()
        self.active_color = None
        self.stickers_dictionary = {1: 'приюти собаку',
                                    2: 'любитель собак',
                                    3: 'кот',
                                    4: 'собака в ванне',
                                    5: 'морда собаки',
                                    6: 'лапа',
                                    7: 'миска'}

        self.setGeometry(0, 0, dictionary['width'], dictionary['height'])

        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.path = QPainterPath()
        self.clear_image()

        self.label = QLabel()
        self.label.setPixmap(QPixmap.fromImage(self.image))

        self.active_color = None
        self.primary_color = BrColor
        self.secondary_color = BrColor

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

            if dictionary['tool'] == 'fill':
                if event.button() == Qt.LeftButton:
                    self.active_color = self.primary_color
                else:
                    self.active_color = self.secondary_color
                start_point = event.pos()
                x = start_point.x()
                y = start_point.y()
                image = self.image
                w, h = image.width(), image.height()
                target_color = image.pixel(x, y)
                have_seen = set()
                queue = [(x, y)]

                def get_cardinal_points(have_seen, center_pos):
                    points = []
                    cx, cy = center_pos
                    for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        xx, yy = cx + x, cy + y
                        if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in have_seen:
                            points.append((xx, yy))
                            have_seen.add((xx, yy))
                    return points

                p = QPainter(self.image)
                p.setPen(QColor(self.active_color))
                while queue:
                    x, y = queue.pop()
                    if image.pixel(x, y) == target_color:
                        p.drawPoint(QPoint(x, y))
                        queue[0:0] = get_cardinal_points(have_seen, (x, y))
                self.update()

    def mouseMoveEvent(self, event):
        if dictionary['tool'] == 'brush':
            if (event.buttons() & Qt.LeftButton) & self.drawing:
                painter = QPainter(self.image)
                painter.setPen(
                    QPen(QColor(dictionary['BrColor']), dictionary['BrSize'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, event.pos())
                self.lastPoint = event.pos()
                painter.drawPath(self.path)
                self.update()

        if dictionary['tool'] == 'sprayer':
            if (event.buttons() & Qt.LeftButton) & self.drawing:
                painter = QPainter(self.image)
                pen = painter.pen()
                pen.setColor(QColor(dictionary['BrColor']))
                painter.setPen(pen)
                for n in range(300):
                    xo = random.gauss(0, dictionary['BrSize'])
                    yo = random.gauss(0, dictionary['BrSize'])
                    painter.drawPoint(int(event.x() + xo), int(event.y() + yo))
                self.update()

        if dictionary['tool'] == 'eraser':
            if (event.buttons() & Qt.LeftButton) & self.drawing:
                painter = QPainter(self.image)
                painter.setPen(
                    QPen(QColor('white'), dictionary['BrSize'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, event.pos())
                self.lastPoint = event.pos()
                self.update()

        if dictionary['tool'] == 'beam':
            if (event.buttons() & Qt.LeftButton) & self.drawing:
                painter = QPainter(self.image)
                painter.setPen(
                    QPen(QColor(dictionary['BrColor']), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, event.pos())
                painter.drawPath(self.path)
                self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def contextMenuEvent(self, event):
        context_menu = []
        menu = QMenu()
        for menu_item in range(1, 8):
            sticker = QAction(self.stickers_dictionary[menu_item], self)
            sticker.triggered.connect(lambda: self.actionClicked(event.pos()))
            context_menu.append(sticker)

        menu.addActions(context_menu)
        menu.exec(event.globalPos())

    def actionClicked(self, pos: QPoint):
        global directory
        png_image_path = directory + f'/images/{self.sender().text()}.png'
        png_image = QImage(png_image_path)
        painter = QPainter(self.image)
        painter.drawImage(pos, png_image)
        painter.end()
        self.label.setPixmap(QPixmap.fromImage(self.image))
        self.update()

    def clear_image(self):
        self.path = QPainterPath()
        self.image.fill(QColor(dictionary['BgColor']))
        self.update()

    def save_image(self):
        filePath, _ = QFileDialog.getSaveFileName(self, 'Сохранить рисунок', '',
                                                  'PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)')
        if filePath == '':
            return
        self.image.save(filePath)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        global directory
        self.clicked_ok = None
        self.dialog = None

        # canvas
        self.tool = Painter()
        self.tool.setFixedSize(dictionary['width'], dictionary['height'])
        self.canvas = QHBoxLayout()
        self.canvas.addWidget(self.tool)

        pix = QPixmap(directory + f'/images/cursor.png')
        cursor = QCursor(pix)
        self.tool.setCursor(cursor)

        # menu
        self.brush = QPushButton('Использовать кисть')
        self.brush.clicked.connect(lambda: self.change_tool('brush'))
        self.brush.setToolTip('Рисование с помощью кисти')
        self.brush.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                 'QPushButton:hover {background-color : #545434}')
        self.brush.setCursor(QCursor(Qt.PointingHandCursor))
        self.brush.setIcon(QIcon(directory + f'/images/bt1.png'))
        self.brush.setIconSize(QSize(30, 30))

        self.sprayer = QPushButton('Использовать распылитель')
        self.sprayer.clicked.connect(lambda: self.change_tool('sprayer'))
        self.sprayer.setToolTip('Распылитель, действует \n как балончик с краской')
        self.sprayer.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                   'QPushButton:hover {background-color : #545434}')
        self.sprayer.setCursor(QCursor(Qt.PointingHandCursor))
        self.sprayer.setIcon(QIcon(directory + f'/images/bt2.png'))
        self.sprayer.setIconSize(QSize(30, 30))

        self.fill = QPushButton('Использовать заливку')
        self.fill.clicked.connect(lambda: self.change_tool('fill'))
        self.fill.setToolTip('Закрашивает фигуры относительно замкнутых линий')
        self.fill.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                'QPushButton:hover {background-color : #545434}')
        self.fill.setCursor(QCursor(Qt.PointingHandCursor))
        self.fill.setIcon(QIcon(directory + f'/images/bt3.png'))
        self.fill.setIconSize(QSize(30, 30))

        self.beam = QPushButton('Использовать луч')
        self.beam.clicked.connect(lambda: self.change_tool('beam'))
        self.beam.setToolTip('Рисует линиями из точки, похожими на лучи')
        self.beam.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                'QPushButton:hover {background-color : #545434}')
        self.beam.setCursor(QCursor(Qt.PointingHandCursor))
        self.beam.setIcon(QIcon(directory + f'/images/bt4.png'))
        self.beam.setIconSize(QSize(30, 30))

        self.eraser = QPushButton('Использовать ластик')
        self.eraser.clicked.connect(lambda: self.change_tool('eraser'))
        self.eraser.setToolTip('Стирает неудачные зарисовки')
        self.eraser.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                  'QPushButton:hover {background-color : #545434}')
        self.eraser.setCursor(QCursor(Qt.PointingHandCursor))
        self.eraser.setIcon(QIcon(directory + f'/images/bt5.png'))
        self.eraser.setIconSize(QSize(30, 30))

        self.text = QLabel('Толщина кисти')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(10)
        self.slider.setValue(dictionary['BrSize'])
        self.slider.setToolTip('Слайдер, изменяет размер кисти')
        self.slider.setCursor(QCursor(Qt.PointingHandCursor))
        self.slider.valueChanged.connect(self.change_size)

        self.palette = QPushButton('Изменение цветов')
        self.palette.clicked.connect(self.change_color)
        self.palette.setToolTip('Выбери свой цвет')
        self.palette.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                   'QPushButton:hover {background-color : #545434}')
        self.palette.setCursor(QCursor(Qt.PointingHandCursor))
        self.palette.setIcon(QIcon(directory + f'/images/bt6.png'))
        self.palette.setIconSize(QSize(30, 30))

        self.clear_canvas = QPushButton('Очистить холст')
        self.clear_canvas.clicked.connect(self.tool.clear_image)
        self.clear_canvas.setToolTip('Стирает все зарисовки одним нажатием')
        self.clear_canvas.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                        'QPushButton:hover {background-color : #545434}')
        self.clear_canvas.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_canvas.setIcon(QIcon(directory + f'/images/bt7.png'))
        self.clear_canvas.setIconSize(QSize(30, 30))

        self.save_canvas = QPushButton('Сохранить рисунок')
        self.save_canvas.clicked.connect(self.tool.save_image)
        self.save_canvas.setToolTip('Сохраняет рисунок в указанную директорию')
        self.save_canvas.setStyleSheet('QPushButton {background-color : #2c2c14}'
                                       'QPushButton:hover {background-color : #545434}')
        self.save_canvas.setCursor(QCursor(Qt.PointingHandCursor))
        self.save_canvas.setIcon(QIcon(directory + f'/images/bt8.png'))
        self.save_canvas.setIconSize(QSize(30, 30))

        self.menu = QVBoxLayout()
        self.menu.addWidget(self.brush)
        self.menu.addWidget(self.sprayer)
        self.menu.addWidget(self.fill)
        self.menu.addWidget(self.beam)
        self.menu.addWidget(self.eraser)
        self.menu.addWidget(self.text)
        self.menu.addWidget(self.slider)
        self.menu.addWidget(self.palette)
        self.menu.addWidget(self.clear_canvas)
        self.menu.addWidget(self.save_canvas)
        self.menu.addStretch(1)

        # Main_window
        self.setWindowIcon(QIcon(directory + f'/images/ico'))
        self.screen_widget = QWidget()
        self.screen_widget.setStyleSheet('background: #6C6C6C')
        self.screen_widget.setLayout(self.canvas)

        self.right_menu = QWidget()
        self.right_menu.setStyleSheet('background: #515151')
        self.right_menu.setLayout(self.menu)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.screen_widget, 9)
        self.layout.addWidget(self.right_menu, 2)

        self.setWindowTitle('Приложение для рисования "Paint"')
        self.setStyleSheet('background-color:#444444')
        self.setLayout(self.layout)

    def change_tool(self, tool):
        global dictionary
        if tool == 'brush':
            dictionary['tool'] = 'brush'
        if tool == 'sprayer':
            dictionary['tool'] = 'sprayer'
        if tool == 'eraser':
            dictionary['tool'] = 'eraser'
        if tool == 'fill':
            dictionary['tool'] = 'fill'
        if tool == 'beam':
            dictionary['tool'] = 'beam'

    def change_color(self):
        self.dialog = QColorDialog()
        self.clicked_ok = self.dialog.exec()
        if self.clicked_ok == 1:
            global BrColor
            BrColor.setNamedColor(self.dialog.currentColor().name())
            global dictionary
            dictionary['BrColor'] = f'{BrColor.name()}'

    def change_size(self):
        global dictionary
        dictionary['BrSize'] = self.slider.value()

extra = {
    'density_scale': '1',
}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme=directory + f'/theme/dark_user.xml', invert_secondary=True,
                     css_file=directory + f'/theme/custom.css', extra=extra)
    window = MainWindow()
    window.showMaximized()
    window.show()
    sys.exit(app.exec())
