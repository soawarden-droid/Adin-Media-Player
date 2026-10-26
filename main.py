import sys
import vlc

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class AdinMedia(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Adin Media")
        self.resize(1200, 750)

        # -----------------------------
        # VLC video engine
        # -----------------------------
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        # -----------------------------
        # Main window
        # -----------------------------
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0b10;
            }

            QWidget {
                color: #f5f5f7;
                font-family: "Inter", "Segoe UI", sans-serif;
            }

            QPushButton {
                background-color: #171720;
                border: 1px solid #282833;
                border-radius: 10px;
                padding: 10px 16px;
                color: #f5f5f7;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #22222d;
                border-color: #7c3aed;
            }

            QPushButton:pressed {
                background-color: #2d2145;
            }

            QSlider::groove:horizontal {
                height: 5px;
                background: #292933;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                width: 14px;
                margin: -5px 0;
                background: #8b5cf6;
                border-radius: 7px;
            }

            QSlider::sub-page:horizontal {
                background: #8b5cf6;
                border-radius: 2px;
            }
        """)

        # -----------------------------
        # Central widget
        # -----------------------------
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 18)
        main_layout.setSpacing(14)

        # -----------------------------
        # Top bar
        # -----------------------------
        top_bar = QHBoxLayout()

        logo = QLabel("Adin")
        logo.setFont(QFont("Arial", 24, QFont.Bold))

        dot = QLabel(".")
        dot.setFont(QFont("Arial", 24, QFont.Bold))
        dot.setStyleSheet("color: #8b5cf6;")

        media_text = QLabel("MEDIA")
        media_text.setStyleSheet("""
            color: #777784;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
        """)

        top_bar.addWidget(logo)
        top_bar.addWidget(dot)
        top_bar.addWidget(media_text)
        top_bar.addStretch()

        self.file_name = QLabel("No video loaded")
        self.file_name.setStyleSheet("""
            color: #8f8f9d;
            font-size: 13px;
        """)

        top_bar.addWidget(self.file_name)

        main_layout.addLayout(top_bar)

        # -----------------------------
        # Video area
        # -----------------------------
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("""
            QFrame {
                background-color: #050507;
                border: 1px solid #202027;
                border-radius: 16px;
            }
        """)

        self.video_frame.setMinimumHeight(500)

        video_layout = QVBoxLayout(self.video_frame)
        video_layout.setContentsMargins(0, 0, 0, 0)

        self.video_widget = QWidget()
        self.video_widget.setStyleSheet(
            "background-color: #050507; border-radius: 16px;"
        )

        video_layout.addWidget(self.video_widget)

        main_layout.addWidget(self.video_frame, 1)

        # -----------------------------
        # Time information
        # -----------------------------
        time_layout = QHBoxLayout()

        self.current_time = QLabel("00:00")
        self.current_time.setStyleSheet("color: #9b9ba8;")

        self.total_time = QLabel("00:00")
        self.total_time.setStyleSheet("color: #9b9ba8;")

        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time)

        main_layout.addLayout(time_layout)

        # -----------------------------
        # Timeline
        # -----------------------------
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.setRange(0, 1000)
        self.timeline.sliderMoved.connect(self.seek_video)

        main_layout.addWidget(self.timeline)

        # -----------------------------
        # Controls
        # -----------------------------
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.open_button = QPushButton("＋  Open")
        self.open_button.clicked.connect(self.open_video)

        self.back_button = QPushButton("↶  10s")
        self.back_button.clicked.connect(self.backward)

        self.play_button = QPushButton("▶  Play")
        self.play_button.clicked.connect(self.play_pause)

        self.forward_button = QPushButton("10s  ↷")
        self.forward_button.clicked.connect(self.forward)

        self.stop_button = QPushButton("■  Stop")
        self.stop_button.clicked.connect(self.stop)

        controls.addWidget(self.open_button)
        controls.addWidget(self.back_button)
        controls.addWidget(self.play_button)
        controls.addWidget(self.forward_button)
        controls.addWidget(self.stop_button)

        controls.addStretch()

        volume_label = QLabel("Volume")
        volume_label.setStyleSheet("color: #888895;")

        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(80)
        self.volume.setFixedWidth(130)
        self.volume.valueChanged.connect(self.change_volume)

        self.fullscreen_button = QPushButton("⛶")
        self.fullscreen_button.setToolTip("Fullscreen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        controls.addWidget(volume_label)
        controls.addWidget(self.volume)
        controls.addWidget(self.fullscreen_button)

        main_layout.addLayout(controls)

        # -----------------------------
        # Status
        # -----------------------------
        self.status = QLabel("Ready")
        self.status.setStyleSheet("""
            color: #62626d;
            font-size: 12px;
        """)

        main_layout.addWidget(self.status)

        # -----------------------------
        # Update timer
        # -----------------------------
        self.timer = QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_player)
        self.timer.start()

        self.player.audio_set_volume(80)

    # =================================
    # OPEN VIDEO
    # =================================

    def open_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            """
            Video Files
            (*.mp4 *.mkv *.avi *.mov *.webm *.flv *.wmv *.m4v)
            ;;All Files (*)
            """,
        )

        if not file_path:
            return

        media = self.vlc_instance.media_new(file_path)

        self.player.set_media(media)

        # Linux video window
        self.player.set_xwindow(self.video_widget.winId())

        self.file_name.setText(file_path.split("/")[-1])
        self.status.setText("Playing")

        self.player.play()

        self.play_button.setText("⏸  Pause")

    # =================================
    # PLAY / PAUSE
    # =================================

    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()

            self.play_button.setText("▶  Play")
            self.status.setText("Paused")

        else:
            self.player.play()

            self.play_button.setText("⏸  Pause")
            self.status.setText("Playing")

    # =================================
    # STOP
    # =================================

    def stop(self):
        self.player.stop()

        self.play_button.setText("▶  Play")
        self.status.setText("Stopped")

        self.timeline.setValue(0)
        self.current_time.setText("00:00")

    # =================================
    # SEEK
    # =================================

    def seek_video(self, value):
        position = value / 1000
        self.player.set_position(position)

    # =================================
    # BACKWARD
    # =================================

    def backward(self):
        current = self.player.get_time()

        if current > 0:
            self.player.set_time(max(0, current - 10000))

    # =================================
    # FORWARD
    # =================================

    def forward(self):
        current = self.player.get_time()
        length = self.player.get_length()

        if length > 0:
            self.player.set_time(min(length, current + 10000))

    # =================================
    # VOLUME
    # =================================

    def change_volume(self, value):
        self.player.audio_set_volume(value)

    # =================================
    # FULLSCREEN
    # =================================

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # =================================
    # UPDATE PLAYER
    # =================================

    def update_player(self):
        length = self.player.get_length()
        current = self.player.get_time()

        if length > 0:
            position = current / length

            self.timeline.blockSignals(True)
            self.timeline.setValue(int(position * 1000))
            self.timeline.blockSignals(False)

            self.current_time.setText(
                self.format_time(current)
            )

            self.total_time.setText(
                self.format_time(length)
            )

    # =================================
    # TIME FORMAT
    # =================================

    @staticmethod
    def format_time(milliseconds):
        seconds = max(0, milliseconds // 1000)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return f"{minutes:02d}:{seconds:02d}"

    # =================================
    # CLOSE
    # =================================

    def closeEvent(self, event):
        self.player.stop()
        event.accept()


# =====================================
# START APPLICATION
# =====================================

app = QApplication(sys.argv)

window = AdinMedia()
window.show()

sys.exit(app.exec())
