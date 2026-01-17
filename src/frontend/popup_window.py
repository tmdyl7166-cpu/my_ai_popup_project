"""
弹窗窗口模块
提供临时性的用户交互界面
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QProgressBar, QFrame,
                             QApplication, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
import sys
import os


class PopupWindow(QDialog):
    """弹窗窗口类"""
    
    # 定义信号
    user_confirmed = pyqtSignal()
    user_cancelled = pyqtSignal()
    progress_updated = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI弹窗项目")
        self.setModal(True)  # 模态对话框
        self.resize(400, 300)
        
        # 初始化UI
        self.init_ui()
        
        # 应用样式
        self.apply_styles()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        self.title_label = QLabel("处理通知")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 内容区域
        self.content_label = QLabel("正在处理您的请求...")
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setWordWrap(True)
        
        # 详细信息区域
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        self.details_text.setVisible(False)  # 默认隐藏
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  # 默认隐藏
        
        # 进度百分比
        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setVisible(False)  # 默认隐藏
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.details_button = QPushButton("详细信息")
        self.details_button.clicked.connect(self.toggle_details)
        self.details_button.setVisible(False)  # 默认隐藏
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.on_cancel)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.on_confirm)
        self.ok_button.setVisible(False)  # 默认隐藏
        
        button_layout.addWidget(self.details_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # 添加到主布局
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)
        layout.addWidget(self.details_text)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        layout.addLayout(button_layout)
        
        # 连接进度信号
        self.progress_updated.connect(self.update_progress)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d3f;
                color: #f8fafc;
                border-radius: 10px;
            }
            
            QLabel {
                color: #f8fafc;
            }
            
            QPushButton {
                background-color: #444455;
                color: #f8fafc;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #555566;
            }
            
            QPushButton:pressed {
                background-color: #666677;
            }
            
            QTextEdit {
                background-color: #3d3d4f;
                border: 1px solid #555566;
                border-radius: 6px;
                color: #f8fafc;
                padding: 10px;
            }
            
            QProgressBar {
                border: 1px solid #555566;
                border-radius: 6px;
                text-align: center;
                background-color: #3d3d4f;
            }
            
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 6px;
            }
        """)
    
    def set_title(self, title):
        """设置标题"""
        self.title_label.setText(title)
    
    def set_content(self, content):
        """设置内容"""
        self.content_label.setText(content)
    
    def set_details(self, details):
        """设置详细信息"""
        self.details_text.setPlainText(details)
        self.details_button.setVisible(True)
    
    def show_progress(self, show=True):
        """显示或隐藏进度条"""
        self.progress_bar.setVisible(show)
        self.progress_label.setVisible(show)
    
    def update_progress(self, value):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{value}%")
        
        # 如果进度完成，显示确定按钮
        if value >= 100:
            self.show_completion()
    
    def toggle_details(self):
        """切换详细信息显示"""
        self.details_text.setVisible(not self.details_text.isVisible())
        if self.details_text.isVisible():
            self.details_button.setText("隐藏详细信息")
            self.resize(400, 400)
        else:
            self.details_button.setText("详细信息")
            self.resize(400, 300)
    
    def show_completion(self):
        """显示完成状态"""
        self.cancel_button.setVisible(False)
        self.ok_button.setVisible(True)
        self.content_label.setText("处理完成！")
        self.progress_label.setText("100%")
    
    def show_error(self, error_message):
        """显示错误状态"""
        self.title_label.setText("处理失败")
        self.content_label.setText("处理过程中发生错误")
        self.details_text.setPlainText(error_message)
        self.details_button.setVisible(True)
        self.show_progress(False)
        self.cancel_button.setVisible(False)
        self.ok_button.setVisible(True)
    
    def on_confirm(self):
        """确认按钮点击"""
        self.user_confirmed.emit()
        self.accept()
    
    def on_cancel(self):
        """取消按钮点击"""
        self.user_cancelled.emit()
        self.reject()


class NotificationPopup(PopupWindow):
    """通知弹窗"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.set_title(title)
        self.set_content(message)
        self.show_progress(False)
        self.ok_button.setVisible(True)
        self.cancel_button.setVisible(False)


class ProgressPopup(PopupWindow):
    """进度弹窗"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.set_title(title)
        self.set_content("正在处理中...")
        self.show_progress(True)
        self.cancel_button.setVisible(True)
        self.ok_button.setVisible(False)


class ConfirmationPopup(PopupWindow):
    """确认弹窗"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.set_title(title)
        self.set_content(message)
        self.show_progress(False)
        self.ok_button.setVisible(True)
        self.cancel_button.setVisible(True)


def main():
    """测试函数"""
    app = QApplication(sys.argv)
    
    # 创建测试弹窗
    def test_notification():
        popup = NotificationPopup("测试通知", "这是一个测试通知弹窗")
        popup.exec_()
    
    def test_progress():
        popup = ProgressPopup("处理进度")
        
        # 模拟进度更新
        def update_progress():
            current = getattr(update_progress, 'current', 0)
            current += 10
            update_progress.current = current
            popup.update_progress(current)
            
            if current < 100:
                QTimer.singleShot(500, update_progress)
            else:
                popup.show_completion()
        
        QTimer.singleShot(500, update_progress)
        popup.exec_()
    
    def test_confirmation():
        popup = ConfirmationPopup("确认操作", "您确定要执行此操作吗？")
        result = popup.exec_()
        if result == QDialog.Accepted:
            print("用户确认")
        else:
            print("用户取消")
    
    # 测试不同类型弹窗
    test_notification()
    # test_progress()
    # test_confirmation()
    
    sys.exit(0)


if __name__ == "__main__":
    main()
