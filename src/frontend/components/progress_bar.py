"""
进度条组件模块
提供自定义进度条组件
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QProgressBar, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
import time


class ProgressBar(QProgressBar):
    """自定义进度条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d3f;
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 6px;
            }
        """)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(0)


class ProgressPanel(QWidget):
    """进度面板组件"""
    
    progress_updated = pyqtSignal(float)
    status_changed = pyqtSignal(str)
    task_completed = pyqtSignal(dict)
    task_failed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
        self._current_task = None
        self._start_time = None
        self._total_steps = 0
        self._completed_steps = 0
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        self.title_label = QLabel("处理进度")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #f8fafc;
            }
        """)
        
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #94a3b8;
            }
        """)
        
        self.progress_bar = ProgressBar()
        self.progress_bar.setMinimumHeight(20)
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #6366f1;
            }
        """)
        self.percentage_label.setAlignment(Qt.AlignCenter)
        
        self.info_frame = QFrame()
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d3f;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setSpacing(8)
        
        self.info_label = QLabel("等待任务开始...")
        self.info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #94a3b8;
                font-family: monospace;
            }
        """)
        info_layout.addWidget(self.info_label)
        
        self.time_label = QLabel("")
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #64748b;
            }
        """)
        info_layout.addWidget(self.time_label)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.percentage_label)
        layout.addWidget(self.info_frame)
        layout.addWidget(self.time_label)
        
        layout.addStretch()
    
    def _connect_signals(self):
        self.progress_bar.valueChanged.connect(self._on_progress_changed)
    
    def _on_progress_changed(self, value: int):
        self.percentage_label.setText(f"{value}%")
        self.progress_updated.emit(value)
    
    def start_task(self, task_name: str, total_steps: int = 100):
        self._current_task = task_name
        self._total_steps = total_steps
        self._completed_steps = 0
        self._start_time = time.time()
        
        self.status_label.setText(f"正在处理: {task_name}")
        self.info_label.setText("任务已开始...")
        self.progress_bar.setValue(0)
        self.time_label.setText("")
        
        self.status_changed.emit("running")
    
    def update_progress(self, current: int, total: int = None, info: str = ""):
        if total is not None:
            self._total_steps = total
        
        if self._total_steps > 0:
            percentage = int((current / self._total_steps) * 100)
            self.progress_bar.setValue(percentage)
            self._completed_steps = current
        
        if info:
            self.info_label.setText(info)
        
        if self._start_time:
            elapsed = time.time() - self._start_time
            if self._completed_steps > 0:
                rate = self._completed_steps / elapsed
                remaining = (self._total_steps - self._completed_steps) / rate
                self.time_label.setText(f"已用时: {elapsed:.1f}s | 预计剩余: {remaining:.1f}s")
    
    def set_info(self, info: str):
        self.info_label.setText(info)
    
    def complete_task(self, result: dict = None):
        self.progress_bar.setValue(100)
        self.status_label.setText("处理完成")
        self.info_label.setText("任务已成功完成")
        
        if self._start_time:
            total_time = time.time() - self._start_time
            self.time_label.setText(f"总用时: {total_time:.1f}秒")
        
        self.status_changed.emit("completed")
        self.task_completed.emit(result if result else {})
    
    def fail_task(self, error: str):
        self.status_label.setText("处理失败")
        self.info_label.setText(f"错误: {error}")
        self.progress_bar.setValue(0)
        self.time_label.setText("失败")
        
        self.status_changed.emit("failed")
        self.task_failed.emit(error)
    
    def reset(self):
        self._current_task = None
        self._completed_steps = 0
        self._total_steps = 0
        self._start_time = None
        
        self.status_label.setText("准备就绪")
        self.info_label.setText("等待任务开始...")
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.time_label.setText("")


class CircularProgress(QWidget):
    """圆形进度条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._max_value = 100
        self._progress_color = QColor(99, 102, 241)
        self._background_color = QColor(45, 45, 63)
        self._line_width = 8
        
        self.setMinimumSize(100, 100)
    
    def setValue(self, value: int):
        self._value = max(0, min(value, self._max_value))
        self.update()
    
    def value(self) -> int:
        return self._value
    
    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - self._line_width
        
        painter.setPen(QPen(self._background_color, self._line_width))
        painter.drawEllipse(center, radius, radius)
        
        if self._value > 0:
            painter.setPen(QPen(self._progress_color, self._line_width))
            angle = 360 * self._value / self._max_value
            start_angle = 90 * 16
            span_angle = -int(angle * 16)
            
            painter.drawArc(
                center.x() - radius,
                center.y() - radius,
                radius * 2,
                radius * 2,
                start_angle,
                span_angle
            )
        
        percentage = int(self._value * 100 / self._max_value)
        painter.setPen(self._progress_color)
        font = painter.font()
        font.setPointSize(max(12, min(self.width(), self.height()) // 5))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            f"{percentage}%"
        )

