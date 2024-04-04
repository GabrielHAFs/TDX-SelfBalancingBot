import sys
import json
import random

from PySide2.QtGui import QPainter, QColor, QPen
from PySide2.QtCore import Qt, QUrl, QTimer, QPoint, QRectF, QSize, QPointF, Slot
from PySide2.QtWidgets import QApplication, QWidget, QPushButton
from PySide2.QtWebSockets import QWebSocket

from math import sin, cos

test_mode = False

class FaceWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setupFaceParameters()

        self.setWindowTitle('Expression Changer')
        self.resize(self.sceen_width, self.sceen_height)

        self.left_pupil_offset  = QPoint(0, 0)  # Initial offset for left eye
        self.right_pupil_offset = QPoint(0, 0)  # Initial offset for right eye

        self.button1 = QPushButton('Eyelid' , self)
        self.button2 = QPushButton('Mouth ' , self)
        self.button3 = QPushButton('Eyebrow', self)
        self.button4 = QPushButton('Eye', self)
        self.button5 = QPushButton('Maluco', self)

        self.button1.setGeometry(0, 0, 80, 20)
        self.button2.setGeometry(0, 40, 80, 20)
        self.button3.setGeometry(0, 80, 80, 20)
        self.button4.setGeometry(0, 120, 80, 20)
        self.button5.setGeometry(0, 160, 80, 20)

        self.button1.clicked.connect(self.changeEyelid)
        self.button2.clicked.connect(self.changeExpression)
        self.button3.clicked.connect(self.changeEyebrow)
        self.button4.clicked.connect(self.changeEyePosition)
        self.button5.clicked.connect(self.goMaluco)


        self.button1.setStyleSheet("background-color: transparent; border: 0px solid black; font-size: 5px;")
        self.button2.setStyleSheet("background-color: transparent; border: 0px solid black; font-size: 5px;")
        self.button3.setStyleSheet("background-color: transparent; border: 0px solid black; font-size: 5px;")
        self.button4.setStyleSheet("background-color: transparent; border: 0px solid black; font-size: 5px;")
        self.button5.setStyleSheet("background-color: transparent; border: 0px solid black; font-size: 5px;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateScreen)
        self.timer.start(100)

        self.timer_eye = QTimer(self)
        self.timer_eye.timeout.connect(self.updateEyePositions)
        self.timer_eye.start(100)

        self.websocket = QWebSocket()
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_message_received)

    def startConnection(self, url):
        print(f"Connecting to WebSocket server: {url}")
        self.websocket.open(QUrl(url))

    @Slot(str)
    def send_message(self, message):
        self.websocket.sendTextMessage(message)

    @Slot()
    def on_connected(self):
        print("WebSocket connected")

    @Slot()
    def on_disconnected(self):
        print("WebSocket disconnected")

    @Slot(str)
    def on_message_received(self, message):
        try:
            telemetry_dict = json.loads(message)

            if "velocity" in telemetry_dict.keys():
                velocity = telemetry_dict.get("velocity")
                print(f"Received velocity: {velocity}")

                if velocity > 5:
                    self.maluco = True

                else:
                    self.maluco = False
                    
            elif "message" in telemetry_dict.keys():
                print(telemetry_dict["message"])

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def setupFaceParameters(self):

        # Set screen Resolution
        self.sceen_width       = 1024
        self.sceen_height      = 600

        # Set colors
        self.eye_color_sclera  = QColor(255, 255, 255)  # White color for sclera
        self.iris_color        = QColor(40, 84, 144)    # Toradex Blue color for iris
        self.pupil_color       = QColor(255, 255, 255)  # White color for pupil
        self.eyelid_color      = QColor(240, 240, 240)  # Light gray (background) color for eyelid
        self.nose_color        = QColor(148, 204, 52)   # Red color for nose
        self.mouth_color       = QColor(40, 84, 144)    # Toradex Blue color for mouth
        self.eyebrow_color     = QColor(148, 204, 52)   # Toradex Green for eyebrow

        # eye parameters
        self.eye_radius        = round(self.sceen_height * 0.20)
        self.max_offset        = round(self.sceen_height * 10 / 100)  # Maximum offset for eye movement
        self.o1                = self.max_offset * 0.33
        self.o2                = self.max_offset * 0.64

        self.left_eye_center   = QPoint(self.sceen_width // 2 - self.sceen_width // 7, round(self.sceen_height * 0.3))
        self.right_eye_center  = QPoint(self.sceen_width // 2 + self.sceen_width // 7, round(self.sceen_height * 0.3))

        self.brow_length       = round(self.sceen_width * 20 / 100)
        self.brow_thickness    = round(self.sceen_width * 2 / 100)

        # nose parameters
        self.nose_size         = QSize(round(self.sceen_height * 9 / 100), round(self.sceen_height * 9 / 100))
        self.nose_center       = QPoint(round(self.sceen_width * 0.50), round(self.sceen_height * 0.6))
        self.nose_t            = self.sceen_width * (4 / 1000)

        # mouth parameters
        self.mouth_xpos        = round(self.sceen_width * 0.45)
        self.mouth_w           = round(self.sceen_width / 9)
        self.mouth_h           = round(self.sceen_height * 8 / 60)
        self.mouth_t           = self.sceen_width * (5 / 1000)

        # movement parameters
        self.blink_state       = 0
        self.blink_positions   = [
            (-self.eye_radius, self.eye_radius * -1, True),
            (self.eye_radius - self.eye_radius, self.eye_radius - self.eye_radius // 3, True),
            (self.eye_radius + self.eye_radius * 0.70, self.eye_radius * 0.35, True),
            (self.eye_radius + self.eye_radius * 0.7, self.eye_radius * -0.4, True),
            (self.eye_radius + self.eye_radius * 2, self.eye_radius * 0.25, False),
        ]

        o1 = self.o1
        o2 = self.o2
        self.eye_state         = 0
        self.eye_positions     = [
            (0, 0, 0, 0),
            (o1, o1, o1, o1),
            
            (o1, o1, o1, -o1),
            (o1, o1, -o1, o1),
            (o1, -o1, o1, o1),
            (-o1, o1, o1, o1),
            
            (o1, o1, -o1, -o1),
            (o1, -o1, o1, -o1),
            (-o1, o1, o1, -o1),
            (o1, -o1, -o1, o1),
            (-o1, o1,-o1, o1),
            (-o1, -o1, o1, o1),

            (o1, -o1, -o1, -o1),
            (-o1, o1, -o1, -o1),
            (-o1, -o1, o1, -o1),
            (-o1, -o1, -o1, o1),

            (-o1, -o1, -o1, -o1),

            (o2, o2, o2, o2),
            
            (o2, o2, o2, -o2),
            (o2, o2, -o2, o2),
            (o2, -o2, o2, o2),
            (-o2, o2, o2, o2),
            
            (o2, o2, -o2, -o2),
            (o2, -o2, o2, -o2),
            (-o2, o2, o2, -o2),
            (o2, -o2, -o2, o2),
            (-o2, o2,-o2, o2),
            (-o2, -o2, o2, o2),

            (o2, -o2, -o2, -o2),
            (-o2, o2, -o2, -o2),
            (-o2, -o2, o2, -o2),
            (-o2, -o2, -o2, o2),

            (-o2, -o2, -o2, -o2),
            ]

        self.pupil_state       = 0
        self.pupil_sizes       = [round(self.eye_radius * 0.15), round(self.eye_radius * 0.25)]

        self.mouth_state       = 0
        self.mouth_positions   = [
            # (start_angle1, span_angle1, start_angle2, span_angle2, height1, height2)
            ( 30,  50,  80,   50, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            ( 30,  60,  90,   60, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            (  0,  60,  60,   60, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            (  0, 180,  180, 180, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            (-30, -50,  -80, -50, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            (-30, -60,  -90, -60, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            (  0, -60,  -60, -60, round(self.sceen_height * 47 / 60), round(self.sceen_height * 47 / 60)),
            (-30, -60, -210, -60, round(self.sceen_height * 52 / 60), round(self.sceen_height * 44 / 60)),
            ( 30,  60,  210,  60, round(self.sceen_height * 44 / 60), round(self.sceen_height * 52 / 60)),
        ]

        self.is_happy          = True
        self.frown             = True
        self.maluco            = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.drawFace(painter)

    def drawFace(self, painter):
        blink_up, blink_down, blink1 = self.blink_positions[self.blink_state]

        self.drawEye(painter, self.left_eye_center , self.left_pupil_offset )
        self.drawEye(painter, self.right_eye_center, self.right_pupil_offset)

        if blink1:
            self.drawEyelid(painter, self.left_eye_center, blink_up, blink_down)
        self.drawEyelid(painter, self.right_eye_center, blink_up, blink_down)

        self.drawEyebrow(painter, self.left_eye_center ,     self.frown)
        self.drawEyebrow(painter, self.right_eye_center, not self.frown)

        self.drawNose(painter)
        self.drawMouth(painter)

    def drawEye(self, painter, eye_center, pupil_offset):
        if self.maluco:
            self.pupil_state = random.choice([0, 1])

        # Draw eye whites (sclera)
        painter.setBrush(self.eye_color_sclera)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(eye_center, self.eye_radius, self.eye_radius)

        # Draw eye iris
        painter.setBrush(self.iris_color)
        painter.drawEllipse(eye_center, self.eye_radius * 0.75, self.eye_radius * 0.75)

        # Calculate pupil position
        pupil_center = eye_center + pupil_offset

        # Draw pupil
        painter.setBrush(self.pupil_color)
        pupil_rect = QRectF(pupil_center - QPoint(self.pupil_sizes[self.pupil_state], self.pupil_sizes[self.pupil_state]),
                            pupil_center + QPoint(self.pupil_sizes[self.pupil_state], self.pupil_sizes[self.pupil_state]))
        painter.drawEllipse(pupil_rect)

    def drawNose(self, painter):
        painter.setBrush(self.nose_color)
        painter.setPen(QPen(QPen(self.mouth_color, self.nose_t, Qt.SolidLine)))
        painter.drawEllipse(self.nose_center, self.nose_size.width(), self.nose_size.height())

    def drawMouth(self, painter):
        if self.maluco:
            self.mouth_state = random.choice([len(self.mouth_positions) - 1, len(self.mouth_positions) - 2])

        a1, a2, a3, a4, h1, h2 = self.mouth_positions[self.mouth_state]

        half_rect1 = QRectF(self.mouth_xpos, h1 , self.mouth_w, self.mouth_h)
        half_rect2 = QRectF(self.mouth_xpos, h2 , self.mouth_w, self.mouth_h)
        
        orientation = -16

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.mouth_color, self.mouth_t, Qt.SolidLine))
        painter.drawArc(half_rect1, a1 * orientation, a2 * orientation)
        painter.drawArc(half_rect2, a3 * orientation, a4 * orientation)

    def drawEyebrow(self, painter, eye_center, frown):
        if self.maluco:
            frown = random.choice([True, False])

        brow_angle = -15 if frown else 15  # Adjust angle based on expression

        brow_start = QPoint(eye_center.x() - self.brow_length // 2, eye_center.y() - self.eye_radius)
        brow_end   = QPoint(eye_center.x() + self.brow_length // 2, eye_center.y() - self.eye_radius)

        # Calculate rotated points for eyebrow
        angle_rad = brow_angle * 3.14 / 180.0
        rot_start = QPoint(
            int((brow_start.x() - eye_center.x()) * round(cos(angle_rad), 2)) - (brow_start.y() - eye_center.y()) * round(sin(angle_rad), 2) + eye_center.x(),
            int((brow_start.x() - eye_center.x()) * round(sin(angle_rad), 2)) + (brow_start.y() - eye_center.y()) * round(cos(angle_rad), 2) + eye_center.y()
        )
        rot_end = QPoint(
            int((brow_end.x() - eye_center.x()) * round(cos(angle_rad), 2)) - (brow_end.y() - eye_center.y()) * round(sin(angle_rad), 2) + eye_center.x(),
            int((brow_end.x() - eye_center.x()) * round(sin(angle_rad), 2)) + (brow_end.y() - eye_center.y()) * round(cos(angle_rad), 2) + eye_center.y()
        )

        # Draw rotated eyebrows
        painter.setPen(QPen(self.eyebrow_color, self.brow_thickness))
        painter.drawLine(rot_start, rot_end)

    def drawEyelid(self, painter, eye_center, blink_up, blink_down):
        eyelid_rect_top = QRectF(eye_center.x() - self.eye_radius - self.eye_radius * 0.25, 
                                 eye_center.y() - self.eye_radius - self.eye_radius * 0.25,
                                 (self.eye_radius * 1.2) * 2, 
                                 self.eye_radius + blink_up)
        
        eyelid_rect_bot = QRectF(eye_center.x() - self.eye_radius - self.eye_radius * 0.25, 
                                 eye_center.y() - self.eye_radius + self.eye_radius * 0.75,
                                 (self.eye_radius * 1.2) * 2, 
                                 self.eye_radius + blink_down)

        start_angle = 0   * 16
        span_angle  = 180 * 16

        painter.setBrush(self.eyelid_color)
        if test_mode:
            painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawChord(eyelid_rect_top, start_angle, span_angle)
        painter.drawChord(eyelid_rect_bot, -start_angle, -span_angle)

    def updateEyePositions(self):
        if not self.maluco:
            x_left, y_left, x_right, y_right = self.eye_positions[self.eye_state]

        else:
            x_left  = random.randint(-self.max_offset, self.max_offset)
            y_left  = random.randint(-self.max_offset, self.max_offset)
            y_right = random.randint(-self.max_offset, self.max_offset)
            x_right = random.randint(-self.max_offset, self.max_offset)

        self.left_pupil_offset.setX(x_left)
        self.left_pupil_offset.setY(y_left)
        self.right_pupil_offset.setX(x_right)
        self.right_pupil_offset.setY(y_right)

    def updateScreen(self):
        self.update()  # Update widget to trigger paintEvent

    @Slot()
    def changeExpression(self):
        self.mouth_state += 1

        if self.mouth_state == len(self.mouth_positions):
            self.mouth_state = 0
            self.is_happy = not self.is_happy

    @Slot()
    def goMaluco(self):
        self.maluco = not self.maluco
        self.frown  = not self.frown

    @Slot()
    def changeEyebrow(self):
        self.frown = not self.frown

    @Slot()
    def changeEyelid(self):
        self.blink_state += 1
        if self.blink_state == len(self.blink_positions):
            self.blink_state = 0

    @Slot()
    def changeEyePosition(self):
        self.eye_state += 1
        if self.eye_state == len(self.eye_positions):
            self.eye_state = 0

if __name__ == "__main__":
    app = QApplication(sys.argv)
    face_widget = FaceWidget()
    if test_mode:
        face_widget.show()
    else:
        face_widget.showFullScreen()
    sys.exit(app.exec_())