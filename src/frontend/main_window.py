"""
AI弹窗项目主窗口
提供图形化用户界面用于人脸合成与视频处理
"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QFileDialog, QComboBox, QTextEdit, QGroupBox,
                             QProgressBar, QTabWidget, QListWidget, QSplitter,
                             QSizePolicy, QMessageBox, QToolBar, QAction,
                             QStatusBar, QFrame, QGridLayout, QCheckBox,
                             QButtonGroup, QRadioButton, QLineEdit, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
import cv2
import json
import os


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI弹窗项目 - 智能人脸合成与视频处理平台")
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(800, 600)
        
        # 加载配置
        self.config = self.load_config()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化变量
        self.current_file = None
        self.current_file_type = None
        self.selected_ai_model = None
        self.processing_mode = "simple"  # simple or advanced
        
    def load_config(self):
        """加载前端配置"""
        try:
            with open("src/frontend/frontend_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 默认配置
            return {
                "ui": {
                    "theme": {
                        "colors": {
                            "primary": "#007bff",
                            "background": "#1a1a1a",
                            "surface": "#2d2d2d",
                            "text": "#ffffff"
                        }
                    }
                }
            }
    
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题
        self.create_title_bar(main_layout)
        
        # 创建主内容区域
        self.create_main_content(main_layout)
        
        # 创建状态栏
        self.create_status_bar()
        
        # 应用样式
        self.apply_styles()
    
    def create_title_bar(self, layout):
        """创建标题栏"""
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QHBoxLayout(title_frame)

        title_label = QLabel("AI弹窗项目")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # 主题切换按钮
        self.theme_button = QPushButton("🌙")
        self.theme_button.setFixedSize(30, 30)
        self.theme_button.setToolTip("切换主题")
        self.theme_button.clicked.connect(self.toggle_theme)

        # 自然语言输入框
        self.nlu_input = QLineEdit()
        self.nlu_input.setPlaceholderText("输入自然语言命令，例如：'把这张照片的脸换到视频里'")
        self.nlu_input.returnPressed.connect(self.process_nlu_input)

        send_button = QPushButton("发送")
        send_button.clicked.connect(self.process_nlu_input)

        nlu_layout = QHBoxLayout()
        nlu_layout.addWidget(self.nlu_input)
        nlu_layout.addWidget(send_button)

        title_layout.addWidget(title_label)
        title_layout.addWidget(self.theme_button)
        title_layout.addLayout(nlu_layout)
        title_layout.addStretch()

        layout.addWidget(title_frame)
    
    def create_main_content(self, layout):
        """创建主内容区域"""
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建左侧主功能区
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)
        
        # 创建右侧反馈区
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([800, 400])
        
        layout.addWidget(splitter)
    
    def create_left_panel(self):
        """创建左侧主功能面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 主体结构标签页
        main_structure_tab = self.create_main_structure_tab()
        tab_widget.addTab(main_structure_tab, "主体结构")
        
        # AI学习标签页
        ai_learning_tab = self.create_ai_learning_tab()
        tab_widget.addTab(ai_learning_tab, "AI学习")
        
        # 任务部署标签页
        task_deployment_tab = self.create_task_deployment_tab()
        tab_widget.addTab(task_deployment_tab, "任务部署")
        
        left_layout.addWidget(tab_widget)
        
        return left_widget
    
    def create_main_structure_tab(self):
        """创建主体结构标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件类型选择区域
        file_selection_group = QGroupBox("选择主要合成文件类型")
        file_layout = QVBoxLayout(file_selection_group)
        
        # 文件类型按钮组
        file_type_layout = QHBoxLayout()
        self.file_type_group = QButtonGroup()
        
        self.image_button = QPushButton("图片")
        self.image_button.setCheckable(True)
        self.video_button = QPushButton("视频")
        self.video_button.setCheckable(True)
        self.camera_button = QPushButton("摄像头")
        self.camera_button.setCheckable(True)
        
        self.file_type_group.addButton(self.image_button, 0)
        self.file_type_group.addButton(self.video_button, 1)
        self.file_type_group.addButton(self.camera_button, 2)
        
        file_type_layout.addWidget(self.image_button)
        file_type_layout.addWidget(self.video_button)
        file_type_layout.addWidget(self.camera_button)
        file_type_layout.addStretch()
        
        # 连接信号
        self.image_button.clicked.connect(lambda: self.on_file_type_selected("image"))
        self.video_button.clicked.connect(lambda: self.on_file_type_selected("video"))
        self.camera_button.clicked.connect(lambda: self.on_file_type_selected("camera"))
        
        file_layout.addLayout(file_type_layout)
        
        # 文件选择区域
        self.file_selection_area = QFrame()
        self.file_selection_area.setObjectName("fileSelectionArea")
        file_selection_layout = QVBoxLayout(self.file_selection_area)
        
        self.file_info_label = QLabel("请选择文件类型")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("color: #94a3b8;")
        
        select_file_button = QPushButton("选择文件")
        select_file_button.clicked.connect(self.select_file)
        
        file_selection_layout.addWidget(self.file_info_label)
        file_selection_layout.addWidget(select_file_button)
        file_selection_layout.addStretch()
        
        file_layout.addWidget(self.file_selection_area)
        
        # 参数展示区域
        params_group = QGroupBox("文件参数")
        params_layout = QVBoxLayout(params_group)
        
        self.params_text = QTextEdit()
        self.params_text.setReadOnly(True)
        self.params_text.setMaximumHeight(150)
        self.params_text.setPlaceholderText("文件参数将在此显示...")
        
        params_layout.addWidget(self.params_text)
        
        layout.addWidget(file_selection_group)
        layout.addWidget(params_group)
        layout.addStretch()
        
        return widget
    
    def create_ai_learning_tab(self):
        """创建AI学习标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI模型选择区域
        ai_model_group = QGroupBox("本地AI模型")
        ai_model_layout = QVBoxLayout(ai_model_group)
        
        # 模型列表
        self.model_list = QListWidget()
        self.model_list.addItems([
            "llama3.2:3b (本地)",
            "mistral:7b (本地)",
            "phi3:3.8b (本地)",
            "gpt-4 (云端)"
        ])
        self.model_list.currentTextChanged.connect(self.on_model_selected)
        
        # 模型操作按钮
        model_buttons_layout = QHBoxLayout()
        self.download_button = QPushButton("下载")
        self.download_button.clicked.connect(self.download_model)
        
        self.info_button = QPushButton("信息")
        self.info_button.clicked.connect(self.show_model_info)
        
        model_buttons_layout.addWidget(self.download_button)
        model_buttons_layout.addWidget(self.info_button)
        model_buttons_layout.addStretch()
        
        ai_model_layout.addWidget(self.model_list)
        ai_model_layout.addLayout(model_buttons_layout)
        
        # 学习说明区域
        learning_group = QGroupBox("学习说明")
        learning_layout = QVBoxLayout(learning_group)
        
        self.learning_text = QTextEdit()
        self.learning_text.setReadOnly(True)
        self.learning_text.setPlaceholderText("选择模型后显示学习说明...")
        
        learning_layout.addWidget(self.learning_text)
        
        # 学习进度区域
        progress_group = QGroupBox("学习进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.learning_progress = QProgressBar()
        self.learning_progress.setRange(0, 100)
        self.learning_progress.setValue(0)
        
        self.progress_label = QLabel("未开始学习")
        self.progress_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.learning_progress)
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(ai_model_group)
        layout.addWidget(learning_group)
        layout.addWidget(progress_group)
        layout.addStretch()
        
        return widget
    
    def create_task_deployment_tab(self):
        """创建任务部署标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 模式选择
        mode_group = QGroupBox("部署模式")
        mode_layout = QHBoxLayout(mode_group)
        
        self.simple_mode_radio = QRadioButton("简单模式")
        self.advanced_mode_radio = QRadioButton("高级模式")
        self.advanced_mode_radio.setChecked(True)
        
        mode_layout.addWidget(self.simple_mode_radio)
        mode_layout.addWidget(self.advanced_mode_radio)
        mode_layout.addStretch()
        
        # 连接模式切换信号
        self.simple_mode_radio.toggled.connect(self.on_mode_changed)
        self.advanced_mode_radio.toggled.connect(self.on_mode_changed)
        
        # 简单模式区域
        self.simple_mode_widget = self.create_simple_mode_widget()
        
        # 高级模式区域
        self.advanced_mode_widget = self.create_advanced_mode_widget()
        
        layout.addWidget(mode_group)
        layout.addWidget(self.simple_mode_widget)
        layout.addWidget(self.advanced_mode_widget)
        
        # 初始化模式显示
        self.on_mode_changed()
        
        # 开始处理按钮
        self.start_button = QPushButton("开始处理")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
        
        layout.addWidget(self.start_button)
        layout.addStretch()
        
        return widget
    
    def create_simple_mode_widget(self):
        """创建简单模式组件"""
        widget = QFrame()
        widget.setObjectName("simpleModeWidget")
        layout = QVBoxLayout(widget)
        
        # 次要文件选择
        secondary_group = QGroupBox("次要合成文件")
        secondary_layout = QVBoxLayout(secondary_group)
        
        self.secondary_file_label = QLabel("未选择次要文件")
        select_secondary_button = QPushButton("选择次要文件")
        select_secondary_button.clicked.connect(self.select_secondary_file)
        
        secondary_layout.addWidget(self.secondary_file_label)
        secondary_layout.addWidget(select_secondary_button)
        
        # 合成类型选择
        synthesis_group = QGroupBox("合成类型")
        synthesis_layout = QVBoxLayout(synthesis_group)
        
        self.synthesis_combo = QComboBox()
        self.synthesis_combo.addItems([
            "图片 → 图片",
            "图片 → 视频",
            "图片 → 实时摄像头"
        ])
        
        synthesis_layout.addWidget(self.synthesis_combo)
        
        # 处理引擎选择
        engine_group = QGroupBox("处理引擎")
        engine_layout = QVBoxLayout(engine_group)
        
        self.engine_combo = QComboBox()
        self.engine_combo.addItems([
            "Deep-Live-Cam",
            "FaceFusion",
            "iRoop"
        ])
        
        engine_layout.addWidget(self.engine_combo)
        
        layout.addWidget(secondary_group)
        layout.addWidget(synthesis_group)
        layout.addWidget(engine_group)
        
        return widget
    
    def create_advanced_mode_widget(self):
        """创建高级模式组件"""
        widget = QFrame()
        widget.setObjectName("advancedModeWidget")
        layout = QVBoxLayout(widget)
        
        # 自然语言输入区域
        nlu_group = QGroupBox("自然语言处理需求")
        nlu_layout = QVBoxLayout(nlu_group)
        
        self.advanced_input = QTextEdit()
        self.advanced_input.setPlaceholderText(
            "请输入处理需求，例如：\n"
            "- '把这张照片的脸换到视频里'\n"
            "- '开始实时摄像头换脸'\n"
            "- '处理批量图片'"
        )
        self.advanced_input.setMaximumHeight(100)
        
        send_nlu_button = QPushButton("分析意图")
        send_nlu_button.clicked.connect(self.process_advanced_nlu)
        
        nlu_layout.addWidget(self.advanced_input)
        nlu_layout.addWidget(send_nlu_button)
        
        # 意图识别结果
        intent_group = QGroupBox("AI意图识别结果")
        intent_layout = QVBoxLayout(intent_group)
        
        self.intent_result = QTextEdit()
        self.intent_result.setReadOnly(True)
        self.intent_result.setPlaceholderText("AI分析结果将在此显示...")
        self.intent_result.setMaximumHeight(150)
        
        intent_layout.addWidget(self.intent_result)
        
        # 参数确认区域
        params_confirm_group = QGroupBox("处理参数确认")
        params_confirm_layout = QVBoxLayout(params_confirm_group)
        
        self.params_confirm_text = QTextEdit()
        self.params_confirm_text.setPlaceholderText("确认的参数将在此显示...")
        self.params_confirm_text.setMaximumHeight(100)
        
        self.confirm_checkbox = QCheckBox("我已确认以上参数")
        
        params_confirm_layout.addWidget(self.params_confirm_text)
        params_confirm_layout.addWidget(self.confirm_checkbox)
        
        layout.addWidget(nlu_group)
        layout.addWidget(intent_group)
        layout.addWidget(params_confirm_group)
        
        return widget
    
    def create_right_panel(self):
        """创建右侧反馈面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 反馈区域标题
        feedback_label = QLabel("反馈区域")
        feedback_font = QFont()
        feedback_font.setPointSize(12)
        feedback_font.setBold(True)
        feedback_label.setFont(feedback_font)
        
        right_layout.addWidget(feedback_label)
        
        # 创建标签页
        feedback_tabs = QTabWidget()
        
        # 预览标签页
        preview_tab = self.create_preview_tab()
        feedback_tabs.addTab(preview_tab, "预览")
        
        # 进度标签页
        progress_tab = self.create_progress_tab()
        feedback_tabs.addTab(progress_tab, "进度")
        
        # 历史标签页
        history_tab = self.create_history_tab()
        feedback_tabs.addTab(history_tab, "历史")
        
        right_layout.addWidget(feedback_tabs)
        
        return right_widget
    
    def create_preview_tab(self):
        """创建预览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 预览图像
        self.preview_label = QLabel("处理结果预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #444444;
                border-radius: 8px;
                min-height: 200px;
                color: #94a3b8;
            }
        """)
        
        layout.addWidget(self.preview_label)
        
        # 预览控制按钮
        preview_controls = QHBoxLayout()
        self.prev_button = QPushButton("上一个")
        self.next_button = QPushButton("下一个")
        self.refresh_button = QPushButton("刷新")
        
        preview_controls.addWidget(self.prev_button)
        preview_controls.addWidget(self.next_button)
        preview_controls.addWidget(self.refresh_button)
        preview_controls.addStretch()
        
        layout.addLayout(preview_controls)
        
        return widget
    
    def create_progress_tab(self):
        """创建进度标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 进度条
        self.feedback_progress = QProgressBar()
        self.feedback_progress.setRange(0, 100)
        self.feedback_progress.setValue(0)
        
        # 进度信息
        self.progress_info = QTextEdit()
        self.progress_info.setReadOnly(True)
        self.progress_info.setPlaceholderText("处理进度信息将在此显示...")
        
        layout.addWidget(self.feedback_progress)
        layout.addWidget(self.progress_info)
        
        return widget
    
    def create_history_tab(self):
        """创建历史标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 历史记录列表
        self.history_list = QListWidget()
        self.history_list.addItems([
            "2026-01-16 14:30 - 图片合成完成",
            "2026-01-16 13:45 - 视频处理完成",
            "2026-01-16 12:15 - 实时摄像头测试完成"
        ])
        
        # 历史操作按钮
        history_buttons = QHBoxLayout()
        self.clear_history_button = QPushButton("清空历史")
        self.export_history_button = QPushButton("导出历史")
        
        history_buttons.addWidget(self.clear_history_button)
        history_buttons.addWidget(self.export_history_button)
        history_buttons.addStretch()
        
        layout.addWidget(self.history_list)
        layout.addLayout(history_buttons)
        
        return widget
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态信息
        self.status_label = QLabel("准备就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.status_progress = QProgressBar()
        self.status_progress.setRange(0, 0)  # Indeterminate progress
        self.status_progress.setVisible(False)
        self.status_progress.setMaximumWidth(200)
        self.status_bar.addWidget(self.status_progress)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.config['ui']['theme']['background']};
                color: {self.config['ui']['theme']['text']};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #444444;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subline-offset: -10px;
                padding: 0 5px;
            }}
            
            QPushButton {{
                background-color: {self.config['ui']['theme']['surface']};
                color: {self.config['ui']['theme']['text']};
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            
            QPushButton:hover {{
                background-color: #3d3d3d;
            }}
            
            QPushButton:checked {{
                background-color: {self.config['ui']['theme']['primary']};
                color: white;
            }}
            
            QTextEdit, QListWidget {{
                background-color: {self.config['ui']['theme']['surface']};
                border: 1px solid #444444;
                border-radius: 4px;
                color: {self.config['ui']['theme']['text']};
            }}
            
            QComboBox {{
                background-color: {self.config['ui']['theme']['surface']};
                border: 1px solid #444444;
                border-radius: 4px;
                color: {self.config['ui']['theme']['text']};
                padding: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {self.config['ui']['theme']['surface']};
                color: {self.config['ui']['theme']['text']};
                selection-background-color: {self.config['ui']['theme']['primary']};
            }}
            
            QProgressBar {{
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                background-color: {self.config['ui']['theme']['surface']};
            }}
            
            QProgressBar::chunk {{
                background-color: {self.config['ui']['theme']['primary']};
                border-radius: 4px;
            }}
            
            #titleFrame {{
                background-color: #252526;
                border-bottom: 1px solid #444444;
                padding: 10px;
            }}
            
            #fileSelectionArea {{
                background-color: #252526;
                border: 1px dashed #444444;
                border-radius: 8px;
                padding: 20px;
            }}
            
            #simpleModeWidget, #advancedModeWidget {{
                background-color: #252526;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
    
    # 事件处理方法
    def on_file_type_selected(self, file_type):
        """处理文件类型选择"""
        self.current_file_type = file_type
        self.file_info_label.setText(f"已选择 {file_type} 类型，请选择具体文件")
        
        # 更新状态栏
        self.status_label.setText(f"已选择 {file_type} 类型")
    
    def select_file(self):
        """选择文件"""
        if not self.current_file_type:
            QMessageBox.warning(self, "警告", "请先选择文件类型")
            return
        
        if self.current_file_type == "image":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        elif self.current_file_type == "video":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择视频", "", "Videos (*.mp4 *.avi *.mov)")
        elif self.current_file_type == "camera":
            # 对于摄像头，我们只是启动预览
            file_path = "CAMERA"
        
        if file_path:
            self.current_file = file_path
            self.file_info_label.setText(f"已选择文件: {os.path.basename(file_path)}")
            
            # 分析文件参数
            self.analyze_file_parameters(file_path)
            
            # 更新状态栏
            self.status_label.setText(f"已选择文件: {os.path.basename(file_path)}")
    
    def analyze_file_parameters(self, file_path):
        """分析文件参数"""
        if not file_path:
            return
        
        try:
            # 这里应该调用实际的参数分析函数
            # 暂时使用模拟数据
            if self.current_file_type == "image":
                params = {
                    "类型": "图片",
                    "尺寸": "1920x1080",
                    "格式": "JPEG",
                    "大小": "2.4 MB",
                    "人脸数量": "1",
                    "推荐引擎": "FaceFusion"
                }
            elif self.current_file_type == "video":
                params = {
                    "类型": "视频",
                    "尺寸": "1920x1080",
                    "格式": "MP4",
                    "时长": "00:02:30",
                    "帧率": "30 fps",
                    "人脸数量": "2",
                    "推荐引擎": "Deep-Live-Cam"
                }
            elif self.current_file_type == "camera":
                params = {
                    "类型": "摄像头",
                    "分辨率": "1280x720",
                    "帧率": "30 fps",
                    "推荐引擎": "Deep-Live-Cam"
                }
            
            # 显示参数
            params_text = "\n".join([f"{k}: {v}" for k, v in params.items()])
            self.params_text.setPlainText(params_text)
            
            # 更新引擎选择
            if "推荐引擎" in params:
                recommended_engine = params["推荐引擎"]
                index = self.engine_combo.findText(recommended_engine)
                if index >= 0:
                    self.engine_combo.setCurrentIndex(index)
            
            self.status_label.setText("文件参数分析完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"参数分析失败: {str(e)}")
    
    def on_model_selected(self, model_name):
        """处理模型选择"""
        if model_name:
            self.selected_ai_model = model_name
            self.learning_text.setPlainText(f"模型: {model_name}\n\n这是一个强大的AI模型，适用于复杂的人脸合成任务。")
            self.status_label.setText(f"已选择模型: {model_name}")
    
    def download_model(self):
        """下载模型"""
        if not self.selected_ai_model:
            QMessageBox.warning(self, "警告", "请先选择要下载的模型")
            return
        
        reply = QMessageBox.question(
            self, "确认下载", 
            f"确定要下载模型 {self.selected_ai_model} 吗？这可能需要一些时间。",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 模拟下载过程
            self.progress_label.setText("正在下载...")
            self.learning_progress.setValue(30)
            
            # 模拟下载完成
            QTimer.singleShot(2000, self.on_download_complete)
    
    def on_download_complete(self):
        """下载完成处理"""
        self.learning_progress.setValue(100)
        self.progress_label.setText("下载完成")
        self.status_label.setText(f"模型 {self.selected_ai_model} 下载完成")
        
        QMessageBox.information(self, "下载完成", f"模型 {self.selected_ai_model} 已成功下载")
    
    def show_model_info(self):
        """显示模型信息"""
        if not self.selected_ai_model:
            QMessageBox.warning(self, "警告", "请先选择模型")
            return
        
        info_text = f"""模型信息: {self.selected_ai_model}

参数量: 30亿
精度: FP16
适用场景: 人脸合成、图像处理
推荐显存: 4GB+
下载大小: 1.8GB

说明:
这是一个专门为图像处理优化的AI模型，
支持高质量的人脸合成和视频处理任务。
        """
        
        QMessageBox.information(self, "模型信息", info_text)
    
    def on_mode_changed(self):
        """处理模式切换"""
        if self.simple_mode_radio.isChecked():
            self.simple_mode_widget.setVisible(True)
            self.advanced_mode_widget.setVisible(False)
            self.processing_mode = "simple"
        else:
            self.simple_mode_widget.setVisible(False)
            self.advanced_mode_widget.setVisible(True)
            self.processing_mode = "advanced"
        
        self.status_label.setText(f"切换到{self.processing_mode}模式")
    
    def select_secondary_file(self):
        """选择次要文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择次要文件", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        
        if file_path:
            self.secondary_file_label.setText(f"已选择: {os.path.basename(file_path)}")
            self.status_label.setText(f"已选择次要文件: {os.path.basename(file_path)}")
    
    def process_advanced_nlu(self):
        """处理高级模式的自然语言输入"""
        user_input = self.advanced_input.toPlainText()
        if not user_input:
            QMessageBox.warning(self, "警告", "请输入处理需求")
            return
        
        # 模拟AI处理
        self.intent_result.setPlainText(f"用户输入: {user_input}\n\n分析结果:\n- 意图类型: 人脸合成\n- 目标文件: 视频\n- 源文件: 图片\n- 处理引擎: FaceFusion\n- 参数设置: 高质量模式")
        
        self.params_confirm_text.setPlainText("确认参数:\n- 合成类型: 图片到视频\n- 引擎: FaceFusion\n- 质量: 高\n- 输出格式: MP4")
        
        self.status_label.setText("AI意图分析完成")
    
    def process_nlu_input(self):
        """处理自然语言输入"""
        user_input = self.nlu_input.text()
        if not user_input:
            return
        
        # 模拟AI处理
        QMessageBox.information(self, "AI响应", f"已理解您的命令: {user_input}\n\n将执行相应的操作。")
        
        # 清空输入框
        self.nlu_input.clear()
        
        self.status_label.setText("已处理自然语言命令")
    
    def start_processing(self):
        """开始处理"""
        if not self.current_file:
            QMessageBox.warning(self, "警告", "请先选择主文件")
            return
        
        if self.processing_mode == "simple":
            if self.secondary_file_label.text() == "未选择次要文件":
                QMessageBox.warning(self, "警告", "请先选择次要文件")
                return
            
            synthesis_type = self.synthesis_combo.currentText()
            engine = self.engine_combo.currentText()
            
            message = f"开始简单模式处理:\n主文件: {os.path.basename(self.current_file)}\n合成类型: {synthesis_type}\n处理引擎: {engine}"
            
        else:  # 高级模式
            if not self.confirm_checkbox.isChecked():
                QMessageBox.warning(self, "警告", "请先确认处理参数")
                return
            
            message = f"开始高级模式处理:\n主文件: {os.path.basename(self.current_file)}\n处理需求: {self.advanced_input.toPlainText()}"
        
        reply = QMessageBox.question(
            self, "确认处理", 
            f"{message}\n\n确定要开始处理吗？",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # 显示处理进度
            self.show_processing_dialog()
    
    def show_processing_dialog(self):
        """显示处理进度对话框"""
        # 模拟处理过程
        self.status_progress.setVisible(True)
        self.status_label.setText("正在处理...")
        
        # 模拟处理完成
        QTimer.singleShot(3000, self.on_processing_complete)
    
    def on_processing_complete(self):
        """处理完成"""
        self.status_progress.setVisible(False)
        self.status_label.setText("处理完成")

        # 添加到历史记录
        from datetime import datetime
        history_item = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - 处理完成"
        self.history_list.insertItem(0, history_item)

        QMessageBox.information(self, "处理完成", "文件处理已完成，结果已在预览区域显示。")

        # 显示预览（模拟）
        self.preview_label.setText("处理结果预览\n[图像/视频预览区域]")

    def toggle_theme(self):
        """切换主题"""
        current_theme = self.config['ui']['theme']['current']
        if current_theme == 'dark':
            new_theme = 'light'
            self.theme_button.setText("☀️")
            # 切换到亮色主题
            self.config['ui']['theme']['current'] = 'light'
            self.config['ui']['theme']['colors']['background'] = '#ffffff'
            self.config['ui']['theme']['colors']['surface'] = '#f8f9fa'
            self.config['ui']['theme']['colors']['text'] = '#212529'
        else:
            new_theme = 'dark'
            self.theme_button.setText("🌙")
            # 切换到暗色主题
            self.config['ui']['theme']['current'] = 'dark'
            self.config['ui']['theme']['colors']['background'] = '#1a1a1a'
            self.config['ui']['theme']['colors']['surface'] = '#2d2d2d'
            self.config['ui']['theme']['colors']['text'] = '#ffffff'

        # 重新应用样式
        self.apply_styles()
        self.status_label.setText(f"已切换到{new_theme}主题")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("AI弹窗项目")
    app.setApplicationVersion("1.0.0")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
