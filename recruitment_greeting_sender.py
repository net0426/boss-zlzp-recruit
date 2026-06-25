import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFrame, QGridLayout, QScrollArea, QMessageBox,
                               QTextEdit, QSizePolicy, QComboBox
                               )
from PySide6.QtCore import Qt, QThread, QTimer,Signal
from PySide6.QtGui import QFont, QPixmap, QPainterPath, QRegion

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


def load_env_config():
    """加载.env配置文件"""
    config = {
        'TARGET_JOB_NAME': '',
        'TARGET_REGION': '',
        'WORK_EXPERIENCE': '',
        'DEGREE_REQUIREMENT': '',
        'DETAIL_DESC': '',
        'CONFIG_PARAM': ''
    }

    try:
        env_path = Path('.env')
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key in config:
                            config[key] = value

        for key in config:
            env_value = os.environ.get(key)
            if env_value and not config[key]:
                config[key] = env_value

    except Exception as e:
        print(f"读取配置文件出错: {e}")

    return config


class LoginWorker(QThread):
    """登录验证工作线程"""
    login_result = Signal(bool, str, str)  # 成功/失败, 软件名, 消息/图片路径

    def __init__(self, form_data):
        super().__init__()
        self.form_data = form_data

    def run(self):
        """模拟登录验证过程"""
        import time
        time.sleep(2)

        from pages.login_manager import BrowserManager

        browser_manager = BrowserManager()

        # ========== BOSS直聘登录 ==========
        try:
            boss = browser_manager.get_boss_page()
            qrcode_path = boss.get_qrcode()

            if qrcode_path == '登录成功':
                self.login_result.emit(True, "软件A", "登录成功")
            elif qrcode_path in ['申请次数太多请等待', '未找到二维码元素', '页面加载异常', '获取二维码失败']:
                self.login_result.emit(False, "软件A", qrcode_path)
            else:
                self.login_result.emit(False, "软件A", qrcode_path)
        except Exception as e:
            print(f"BOSS直聘登录异常: {e}")
            self.login_result.emit(False, "软件A", f"登录异常: {str(e)}")

        time.sleep(1)

        # ========== 智联招聘登录 ==========
        try:
            zlzp = browser_manager.get_zlzp_page()
            qrcode_path = zlzp.get_qrcode()

            if qrcode_path == '登录成功':
                self.login_result.emit(True, "软件B", "登录成功")
            elif qrcode_path in ['申请次数太多请等待', '未找到二维码元素', '页面加载异常', '获取二维码失败']:
                self.login_result.emit(False, "软件B", qrcode_path)
            else:
                self.login_result.emit(False, "软件B", qrcode_path)
        except Exception as e:
            print(f"智联招聘登录异常: {e}")
            self.login_result.emit(False, "软件B", f"登录异常: {str(e)}")


class SoftwareStatusWidget(QFrame):
    """软件状态显示组件 - 二维码展示"""

    def __init__(self, software_name, parent=None):
        super().__init__(parent)
        self.software_name = software_name
        self.is_logged_in = False
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # 软件名称标签
        name_label = QLabel(software_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                background-color: transparent;
            }
        """)

        # 状态标签
        self.status_label = QLabel("未登录")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ef4444;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 6px 8px;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
            }
        """)

        # 二维码显示区域
        self.qrcode_label = QLabel()
        self.qrcode_label.setFixedSize(200, 200)
        self.qrcode_label.setAlignment(Qt.AlignCenter)
        self.qrcode_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                color: #9ca3af;
                font-size: 13px;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
        """)
        self.qrcode_label.setText("📱\n等待二维码")
        self.qrcode_label.setCursor(Qt.PointingHandCursor)

        # 提示文字
        self.hint_label = QLabel("点击刷新二维码")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 11px;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                background-color: transparent;
            }
        """)

        layout.addWidget(name_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.qrcode_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.hint_label)

    def setLoading(self):
        """设置加载状态"""
        self.status_label.setText("验证中...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #667eea;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 6px 8px;
                background-color: #eef2ff;
                border: 1px solid #c7d2fe;
                border-radius: 6px;
            }
        """)

        self.qrcode_label.setText("⏳\n加载中...")
        self.qrcode_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 2px solid #667eea;
                border-radius: 8px;
                color: #667eea;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
        """)

        self.hint_label.setText("请稍候...")

    def setSuccess(self, message="登录成功"):
        """设置成功状态"""
        self.is_logged_in = True
        self.status_label.setText("✅ 已登录")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #16a34a;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 6px 8px;
                background-color: #f0fdf4;
                border: 1px solid #bbf7d0;
                border-radius: 6px;
            }
        """)

        self.qrcode_label.setText("✅\n登录成功")
        self.qrcode_label.setStyleSheet("""
            QLabel {
                background-color: #f0fdf4;
                border: 2px solid #bbf7d0;
                border-radius: 8px;
                color: #16a34a;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
        """)

        self.hint_label.setText("可以启动系统")

    def setFailed(self, image_path=None):
        """设置失败状态"""
        self.is_logged_in = False
        self.status_label.setText("❌ 请扫码登录")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #dc2626;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 6px 8px;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
            }
        """)

        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.qrcode_label.setPixmap(scaled_pixmap)
                self.qrcode_label.setStyleSheet("""
                    QLabel {
                        background-color: #ffffff;
                        border: 2px solid #e5e7eb;
                        border-radius: 8px;
                    }
                """)
                self.hint_label.setText("请使用APP扫描二维码")
                return

        self.qrcode_label.setText("📱\n扫描二维码登录")
        self.qrcode_label.setStyleSheet("""
            QLabel {
                background-color: #fef2f2;
                border: 2px solid #fecaca;
                border-radius: 8px;
                color: #dc2626;
                font-size: 13px;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
        """)

        self.hint_label.setText("等待二维码生成...")

    def reset(self):
        """重置为初始状态"""
        self.is_logged_in = False
        self.status_label.setText("等待确认登录")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ef4444;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 6px 8px;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
            }
        """)

        self.qrcode_label.setText("📱\n等待二维码")
        self.qrcode_label.setStyleSheet("""
            QLabel {
                background-color: #f9fafb;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                color: #9ca3af;
                font-size: 13px;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
        """)

        self.hint_label.setText("点击刷新二维码")

    def mousePressEvent(self, event):
        """点击事件手动刷新二维码或检查登录状态"""
        if self.is_logged_in:
            super().mousePressEvent(event)
            return
        from pages.login_manager import BrowserManager
        browser_manager = BrowserManager()

        main_win = self.window()

        if 'boss直聘' in self.software_name:
            boss_page = browser_manager.get_boss_page()
            if boss_page.driver is None:
                boss_page.get_qrcode()
            qrcode_path = boss_page.refresh_qrcode()
            print(f"BOSS刷新结果: {qrcode_path}")

            if qrcode_path == '登录成功':
                self.setSuccess()
                main_win = self.window()
                main_win.software_logged_in["软件A" if 'boss' in self.software_name else "软件B"] = True
                main_win.update_start_button_state()
                return

            if qrcode_path and os.path.exists(qrcode_path):
                pixmap = QPixmap(qrcode_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.qrcode_label.setPixmap(scaled_pixmap)
                    self.qrcode_label.setStyleSheet("""
                        QLabel {
                            background-color: #ffffff;
                            border: 2px solid #e5e7eb;
                            border-radius: 8px;
                        }
                    """)
                    self.hint_label.setText("请使用APP扫描二维码")
            else:
                print("刷新二维码失败，尝试重新获取")
                qrcode_path = boss_page.get_qrcode()
                if qrcode_path and os.path.exists(qrcode_path):
                    pass

        elif '智联招聘' in self.software_name:
            zlzp_page = browser_manager.get_zlzp_page()
            if zlzp_page.driver is None:
                zlzp_page.get_qrcode()
            qrcode_path = zlzp_page.refresh_qrcode()
            print(f"智联刷新结果: {qrcode_path}")

            if qrcode_path == '登录成功':
                self.setSuccess()
                main_win = self.window()
                main_win.software_logged_in["软件A" if 'boss' in self.software_name else "软件B"] = True
                main_win.update_start_button_state()
                return

            if qrcode_path and os.path.exists(qrcode_path):
                pixmap = QPixmap(qrcode_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.qrcode_label.setPixmap(scaled_pixmap)
                    self.qrcode_label.setStyleSheet("""
                        QLabel {
                            background-color: #ffffff;
                            border: 2px solid #e5e7eb;
                            border-radius: 8px;
                        }
                    """)
                    self.hint_label.setText("请使用APP扫描二维码")
            else:
                qrcode_path = zlzp_page.get_qrcode()
        super().mousePressEvent(event)


class LoginSoftware(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_env_config()
        # 不使用 Qt.WindowStaysOnTopHint，避免窗口创建时的问题
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._is_stay_on_top = True
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(700, 750)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.round_frame = QFrame()
        self.round_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 24px;
            }
        """)

        round_layout = QVBoxLayout(self.round_frame)
        round_layout.setContentsMargins(0, 0, 0, 0)
        round_layout.setSpacing(0)

        self.create_custom_title_bar(round_layout)

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")

        old_layout = QVBoxLayout(content_widget)
        old_layout.setSpacing(8)
        old_layout.setContentsMargins(15, 10, 15, 12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #d1d5db;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9ca3af;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(8)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        self.create_header(scroll_layout)
        self.create_basic_info(scroll_layout)
        self.create_software_status(scroll_layout)
        self.create_detail_info(scroll_layout)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        old_layout.addWidget(scroll_area)

        self.create_buttons(old_layout)
        main_layout.addWidget(self.round_frame)
        round_layout.addWidget(content_widget)

        self.login_worker = None
        self.software_logged_in = {
            "软件A": False,
            "软件B": False
        }
        self._login_browser_closed = False

        # 业务线程相关
        self._business_thread = None
        self._stop_event = None
        self._is_business_running = False
        self._initial_topmost_set = False

    def showEvent(self, event):
        """窗口显示事件 - 设置初始置顶状态"""
        super().showEvent(event)
        if not self._initial_topmost_set and self._is_stay_on_top:
            try:
                import win32gui
                import win32con
                hwnd = int(self.winId())
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            except ImportError:
                pass
            self._initial_topmost_set = True

    def closeEvent(self, event):
        """窗口关闭时触发：直接清理资源并退出（无弹窗）"""
        # 1. 强制停止 AI（无论是否业务运行）
        try:
            from pages.start_copaw import stop_ai
            stop_ai()
            print("AI 已停止")
        except Exception as e:
            print(f"停止 AI 失败: {e}")

        # 2. 如果业务正在运行，设置中断标志
        if self._is_business_running and self._stop_event:
            self._stop_event.set()

        # 3. 保存提示词
        if hasattr(self, 'text_desc'):
            self._save_to_file(BASE_DIR / "prompt" / "promp.txt", self.text_desc.toPlainText())
        if hasattr(self, 'text_conf'):
            self._save_to_file(BASE_DIR / "prompt" / "prompt.txt", self.text_conf.toPlainText())

        # 4. 关闭浏览器驱动（使用与业务相同的 DriverManager）
        try:
            from pages.get_web import DriverManager
            DriverManager.close_driver()
            print("浏览器驱动已关闭")
        except Exception as e:
            print(f"关闭驱动失败: {e}")

        # 5. 清理二维码图片
        self.cleanup_images()

        # 6. 终止登录线程（如果还在运行）
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.terminate()
            self.login_worker.wait()

        event.accept()

    def cleanup_images(self):
        """删除 img 目录下的二维码图片"""
        img_dir = BASE_DIR / "img"
        if img_dir.exists() and img_dir.is_dir():
            try:
                for file in img_dir.glob("*.*"):
                    if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                        os.remove(file)
                        print(f"已清理图片: {file.name}")
            except Exception as e:
                print(f"清理图片时出错: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def create_custom_title_bar(self, parent_layout):
        title_bar = QFrame()
        title_bar.setFixedHeight(40)

        title_bar.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-top-left-radius: 24px;
                    border-top-right-radius: 24px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                }
            """)

        h_layout = QHBoxLayout(title_bar)
        h_layout.setContentsMargins(15, 0, 8, 0)
        h_layout.setSpacing(6)

        icon_label = QLabel("💼")
        icon_label.setStyleSheet("color: #333333; font-size: 18px; background: transparent;")
        h_layout.addWidget(icon_label)

        title_label = QLabel("可视岗位管理程序")
        title_label.setStyleSheet("""
            color: #333333;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
        """)
        h_layout.addWidget(title_label)
        h_layout.addStretch()

        # 添加固定最上层按钮（默认激活状态）
        self.btn_pin = QPushButton("📌")
        self.btn_pin.setFixedSize(30, 30)
        self.btn_pin.setCheckable(True)
        self.btn_pin.setChecked(True)  # 默认选中
        # 使用与登录按钮相同的紫色渐变
        self.btn_pin.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                font-size: 14px;
                border-radius: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd6, stop:1 #6a4198);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c5ec9, stop:1 #5a3587);
            }
            QPushButton:!checked {
                background: transparent;
                color: #333333;
            }
            QPushButton:!checked:hover {
                background: #e5e7eb;
            }
        """)
        self.btn_pin.clicked.connect(self.toggle_stay_on_top)
        h_layout.addWidget(self.btn_pin)

        btn_min = QPushButton("─")
        btn_min.setFixedSize(30, 30)
        btn_min.setStyleSheet("""
            QPushButton {
                background: transparent; color: #333333; border: none; font-size: 18px;
                border-radius: 14px;
            }
            QPushButton:hover { background: #e5e7eb; }
        """)
        btn_min.clicked.connect(self.showMinimized)
        h_layout.addWidget(btn_min)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent; color: #333333; border: none; font-size: 18px;
                border-radius: 15px;
            }
            QPushButton:hover { background: #e81123; color: white; }
        """)
        btn_close.clicked.connect(self.close)
        h_layout.addWidget(btn_close)

        parent_layout.addWidget(title_bar)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.position().y() <= 40:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if hasattr(self, '_drag_pos'):
            del self._drag_pos
        super().mouseReleaseEvent(event)

    def toggle_stay_on_top(self):
        """切换窗口固定最上层状态（使用 Windows API，无闪烁）"""
        # 切换状态
        self._is_stay_on_top = not self._is_stay_on_top

        # 更新按钮的 checked 状态（样式表会自动处理样式变化）
        self.btn_pin.setChecked(self._is_stay_on_top)

        # 使用 Windows API 来设置置顶，避免窗口重新创建导致的闪烁
        try:
            import win32gui
            import win32con

            # 获取窗口句柄
            hwnd = int(self.winId())

            if self._is_stay_on_top:
                # 设置窗口为最顶层
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            else:
                # 取消最顶层，恢复正常
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        except ImportError:
            # 如果没有 pywin32 库，回退到原来的方法
            current_flags = self.windowFlags()
            if self._is_stay_on_top:
                self.setWindowFlags(current_flags | Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(current_flags & ~Qt.WindowStaysOnTopHint)
            self.show()

    def update_start_button_state(self):
        """检查所有软件是否都已登录，并更新启动按钮和登录按钮的文字状态"""
        if self._is_business_running:
            # 业务运行中，不改变启动按钮样式（此时它是中断按钮）
            return

        if all(self.software_logged_in.values()):
            self.start_button.setEnabled(True)
            self.login_button.setText("全部已登录 ✓")
            self.login_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #10b981, stop:1 #059669);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                    letter-spacing: 2px;
                }
            """)
            if not self._login_browser_closed:
                try:
                    from pages.login_manager import BrowserCloser
                    BrowserCloser().close_browser()
                except Exception as e:
                    print(f"关闭浏览器时出错: {e}")
                self._login_browser_closed = True
        else:
            self.start_button.setEnabled(False)

    def create_header(self, parent_layout):
        """创建头部区域"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                min-height: 70px;
                max-height: 70px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 8, 20, 8)

        title_label = QLabel("可视岗位管理程序")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("管理系统")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 11px;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                background-color: transparent;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)

        parent_layout.addWidget(header_frame)

    def create_basic_info(self, parent_layout):
        """创建基本信息区域 - 共用（岗位/城市输入框，经验/学历下拉框）"""
        basic_frame = QFrame()
        basic_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)

        basic_layout = QVBoxLayout(basic_frame)
        basic_layout.setSpacing(10)
        basic_layout.setContentsMargins(15, 15, 15, 15)

        section_label = QLabel("基本信息")
        section_label.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 2px;
                background-color: transparent;
            }
        """)
        basic_layout.addWidget(section_label)

        hint_label = QLabel("以下信息两个软件共用")
        hint_label.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 11px;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 0px 2px;
                background-color: transparent;
            }
        """)
        basic_layout.addWidget(hint_label)

        inputs_grid = QGridLayout()
        inputs_grid.setSpacing(10)

        # 将四个字段放入网格
        # 岗位（输入框）
        self._create_field_with_label(inputs_grid, 0, 0, "岗位 ※", "岗位名称",
                                      self.config['TARGET_JOB_NAME'], is_combo=False)
        # 城市（输入框）
        self._create_field_with_label(inputs_grid, 0, 1, "城市", "工作城市",
                                      self.config['TARGET_REGION'], is_combo=False)
        # 经验（下拉框）
        self._create_field_with_label(inputs_grid, 1, 0, "经验", "工作经验",
                                      self.config['WORK_EXPERIENCE'], is_combo=True,
                                      items=["" , "在校生", "应届生" , "1年", "1-3年", "3-5年", "5-10年", "10年以上"])
        # 学历（下拉框）
        self._create_field_with_label(inputs_grid, 1, 1, "学历", "学历要求",
                                      self.config['DEGREE_REQUIREMENT'], is_combo=True,
                                      items=["","初中及以下" , "中专/中技" , "高中" , "大专", "本科", "硕士", "博士"])

        basic_layout.addLayout(inputs_grid)

        # 自动保存定时器（500ms防抖）
        self._timer_basic = QTimer()
        self._timer_basic.setSingleShot(True)
        self._timer_basic.setInterval(500)
        self._timer_basic.timeout.connect(self._auto_save_basic)

        # 为所有输入控件连接信号，触发自动保存
        self.job_input.textChanged.connect(lambda: self._timer_basic.start())
        self.city_input.textChanged.connect(lambda: self._timer_basic.start())
        self.combo_experience.currentTextChanged.connect(lambda: self._timer_basic.start())
        self.combo_degree.currentTextChanged.connect(lambda: self._timer_basic.start())

        parent_layout.addWidget(basic_frame)

    def _create_field_with_label(self, grid, row, col, label, placeholder, default_value,
                                 is_combo=False, items=None):
        """辅助方法：创建带标签的输入控件（QLineEdit 或 QComboBox）"""
        container = QFrame()
        container.setStyleSheet("background-color: transparent; border: none;")
        field_layout = QVBoxLayout(container)
        field_layout.setSpacing(4)
        field_layout.setContentsMargins(0, 0, 0, 0)

        field_label = QLabel(label)
        field_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 12px;
                font-weight: 500;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 0px 2px;
                background-color: transparent;
            }
        """)
        field_layout.addWidget(field_label)

        if is_combo:
            widget = QComboBox()
            if items:
                widget.addItems(items)
            # 设置初始值
            if default_value and default_value in items:
                widget.setCurrentText(default_value)
            elif default_value and default_value not in items:
                # 如果配置值不在列表中，添加并选中（保留原值）
                widget.addItem(default_value)
                widget.setCurrentText(default_value)
            widget.setStyleSheet("""
                QComboBox {
                    border: 1.5px solid #e5e7eb;
                    border-radius: 6px;
                    padding: 8px 10px;
                    padding-right: 25px;
                    font-size: 13px;
                    background-color: #f9fafb;
                    color: #374151;
                    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                    combobox-popup: 0;   /* 强制向下弹出 */
                }
                QComboBox:hover { border-color: #d1d5db; }
                QComboBox:focus { border-color: #667eea; background-color: #ffffff; }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    width: 20px;
                    border: none;
                    background: transparent;
                }
                QComboBox::down-arrow {
                    border: none;
                    width: 0;
                    height: 0;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 6px solid #788ac2;
                    background: transparent;
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    background-color: #ffffff;
                    color: #374151;
                    outline: none;
                    selection-background-color: #667eea;
                    selection-color: #ffffff;
                    padding: 4px;
                }
                QComboBox QAbstractItemView::item {
                    min-height: 28px;
                    padding: 4px 8px;
                    border-radius: 4px;
                    background-color: transparent;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #667eea;
                    color: white;
                }
            """)
        else:
            widget = QLineEdit()
            widget.setPlaceholderText(placeholder)
            if default_value:
                widget.setText(default_value)
            widget.setStyleSheet("""
                QLineEdit {
                    border: 1.5px solid #e5e7eb;
                    border-radius: 6px;
                    padding: 8px 10px;
                    font-size: 13px;
                    background-color: #f9fafb;
                    color: #374151;
                    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                }
                QLineEdit:focus {
                    border-color: #667eea;
                    background-color: #ffffff;
                }
                QLineEdit:hover {
                    border-color: #d1d5db;
                }
            """)

        field_layout.addWidget(widget)
        grid.addWidget(container, row, col)

        # 保存控件引用
        if label.startswith("岗位"):
            self.job_input = widget
        elif label == "城市":
            self.city_input = widget
        elif label == "经验":
            self.combo_experience = widget
        elif label == "学历":
            self.combo_degree = widget

    def _auto_save_basic(self):
        """基础信息自动保存（岗位为空时不保存，避免弹框）"""
        job = self.job_input.text().strip()
        if job:
            self._save_config(silent=True)

    def _save_config(self, silent=False):
        """实际执行保存配置到 .env 文件（仅保存基础字段，不含 AI 提示词）"""
        job = self.job_input.text().strip()
        if not job:
            if not silent:
                QMessageBox.warning(self, "保存失败", "岗位名称不能为空，请填写后再保存。")
            return

        updates = {
            'TARGET_JOB_NAME': self.job_input.text(),
            'TARGET_REGION': self.city_input.text(),
            'WORK_EXPERIENCE': self.combo_experience.currentText(),
            'DEGREE_REQUIREMENT': self.combo_degree.currentText(),
        }
        # 不再包含 DETAIL_DESC 和 CONFIG_PARAM

        env_path = Path('.env')
        if not env_path.exists():
            lines = []
        else:
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        updated_keys = set()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                new_lines.append(line)
                continue

            if '=' in stripped:
                key, _ = stripped.split('=', 1)
                key = key.strip()
                if key in updates:
                    new_lines.append(f"{key}={updates[key]}\n")
                    updated_keys.add(key)
                    continue

            new_lines.append(line)

        for key, value in updates.items():
            if key not in updated_keys and value:
                new_lines.append(f"{key}={value}\n")

        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print("配置已保存到 .env:", {k: v for k, v in updates.items() if v})

    def on_save_config(self):
        """手动保存按钮点击（要求岗位非空）"""
        self._save_config(silent=False)

    def create_software_status(self, parent_layout):
        """创建软件状态显示区域 - 无标题"""
        qrcode_layout = QHBoxLayout()
        qrcode_layout.setSpacing(15)

        self.software_a_widget = SoftwareStatusWidget("boss直聘")
        qrcode_layout.addWidget(self.software_a_widget)

        self.software_b_widget = SoftwareStatusWidget("智联招聘")
        qrcode_layout.addWidget(self.software_b_widget)

        parent_layout.addLayout(qrcode_layout)

    def create_detail_info(self, parent_layout):
        """创建详细信息区域"""
        detail_frame = QFrame()
        detail_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
        """)

        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setSpacing(10)
        detail_layout.setContentsMargins(15, 15, 15, 15)

        section_label = QLabel("AI 提示词")
        section_label.setStyleSheet("""
            QLabel {
                color: #4b5563;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                padding: 2px;
                background-color: transparent;
            }
        """)
        detail_layout.addWidget(section_label)

        prompt_dir = BASE_DIR / "prompt"
        prompt_dir.mkdir(parents=True, exist_ok=True)
        file_desc = prompt_dir / "promp.txt"
        file_conf = prompt_dir / "prompt.txt"

        def load_text(path):
            try:
                if path.exists():
                    return path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"读取文件失败 {path}: {e}")
            return ""

        self.text_desc = QTextEdit()
        self.text_desc.setPlaceholderText("请输入打招呼提示词...")
        self.text_desc.setPlainText(load_text(file_desc))
        self.text_desc.setStyleSheet(self._text_edit_style())
        self.text_desc.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_desc.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_desc.setFixedHeight(200)
        detail_layout.addWidget(self.text_desc)

        self.text_conf = QTextEdit()
        self.text_conf.setPlaceholderText("请输入筛选岗位提示词...")
        self.text_conf.setPlainText(load_text(file_conf))
        self.text_conf.setStyleSheet(self._text_edit_style())
        self.text_conf.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_conf.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_conf.setFixedHeight(200)
        detail_layout.addWidget(self.text_conf)

        self._timer_desc = QTimer()
        self._timer_desc.setSingleShot(True)
        self._timer_desc.setInterval(500)
        self._timer_desc.timeout.connect(
            lambda: self._save_to_file(file_desc, self.text_desc.toPlainText())
        )
        self.text_desc.textChanged.connect(lambda: self._timer_desc.start())

        self._timer_conf = QTimer()
        self._timer_conf.setSingleShot(True)
        self._timer_conf.setInterval(500)
        self._timer_conf.timeout.connect(
            lambda: self._save_to_file(file_conf, self.text_conf.toPlainText())
        )
        self.text_conf.textChanged.connect(lambda: self._timer_conf.start())

        save_btn = QPushButton("💾 保存配置到 .env")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
                color: #374151;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
        """)
        save_btn.clicked.connect(self.on_save_config)
        detail_layout.addWidget(save_btn)

        parent_layout.addWidget(detail_frame)

    def _text_edit_style(self):
        return """
            QTextEdit {
                border: 1.5px solid #e5e7eb;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                background-color: #f9fafb;
                color: #374151;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: #ffffff;
            }
            QTextEdit:hover {
                border-color: #d1d5db;
            }
        """

    def _input_style(self):
        return """
            QLineEdit {
                border: 1.5px solid #e5e7eb;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                background-color: #f9fafb;
                color: #374151;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                min-height: 55px;
                max-height: 55px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #d1d5db;
            }
        """

    def _save_to_file(self, filepath, text):
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(text, encoding='utf-8')
        except Exception as e:
            print(f"写入文件失败 {filepath}: {e}")

    def create_buttons(self, parent_layout):
        """创建固定在底部的按钮区域"""
        button_widget = QFrame()
        button_widget.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)

        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 5, 0, 0)

        self.login_button = QPushButton("检查登录")
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd6, stop:1 #6a4198);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4c5ec9, stop:1 #5a3587);
            }
            QPushButton:disabled {
                background: #d1d5db;
                color: #9ca3af;
            }
        """)
        self.login_button.clicked.connect(self.on_login_clicked)

        self.start_button = QPushButton("启    动")
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48bb78, stop:1 #38a169);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3ca569, stop:1 #2d8a56);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #31915a, stop:1 #247048);
            }
            QPushButton:disabled {
                background: #d1d5db;
                color: #9ca3af;
            }
        """)
        self.start_button.clicked.connect(self.on_start_clicked)
        self.start_button.setEnabled(False)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.start_button)

        parent_layout.addWidget(button_widget)

    def get_form_data(self):
        """获取表单数据"""
        return {
            '岗位': self.job_input.text(),
            '城市': self.city_input.text(),
            '经验': self.combo_experience.currentText(),
            '学历': self.combo_degree.currentText(),
            '描述信息': self.text_desc.toPlainText(),
            '配置参数': self.text_conf.toPlainText()
        }

    def on_login_clicked(self):
        """登录按钮点击事件"""
        if all(self.software_logged_in.values()):
            print("所有软件已登录")
            self.update_start_button_state()
            return

        self._login_browser_closed = False

        self.login_button.setEnabled(False)
        self.login_button.setText("登录中...")
        self.software_a_widget.setLoading()
        self.software_b_widget.setLoading()

        form_data = self.get_form_data()
        self.login_worker = LoginWorker(form_data)
        self.login_worker.login_result.connect(self.on_login_result)
        self.login_worker.start()

    def on_login_result(self, success, software, message):
        """处理登录结果"""
        if software == "软件A":
            if success:
                self.software_a_widget.setSuccess(f"{message}")
                self.software_logged_in["软件A"] = True
            else:
                self.software_a_widget.setFailed(message)
                self.software_logged_in["软件A"] = False
        elif software == "软件B":
            if success:
                self.software_b_widget.setSuccess(f"{message}")
                self.software_logged_in["软件B"] = True
            else:
                self.software_b_widget.setFailed(message)
                self.software_logged_in["软件B"] = False

        self.update_start_button_state()
        if all(self.software_logged_in.values()):
            self.login_button.setEnabled(True)

    def _set_button_to_interrupt(self):
        """将启动按钮设置为中断按钮样式"""
        self.start_button.setText("中断程序")
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b91c1c, stop:1 #991b1b);
            }
        """)
        try:
            self.start_button.clicked.disconnect(self.on_start_clicked)
        except Exception:
            pass
        self.start_button.clicked.connect(self.on_interrupt_clicked)

    def _set_button_to_start(self):
        """将按钮恢复为启动按钮样式"""
        self.start_button.setText("启    动")
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48bb78, stop:1 #38a169);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3ca569, stop:1 #2d8a56);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #31915a, stop:1 #247048);
            }
            QPushButton:disabled {
                background: #d1d5db;
                color: #9ca3af;
            }
        """)
        try:
            self.start_button.clicked.disconnect(self.on_interrupt_clicked)
        except Exception:
            pass
        self.start_button.clicked.connect(self.on_start_clicked)

    def on_start_clicked(self):
        """启动按钮点击事件"""
        if not all(self.software_logged_in.values()):
            print("请确保所有软件都已登录")
            return

        self.login_button.setEnabled(False)

        print("启动所有软件")
        args = self.parse_args()

        self._stop_event = threading.Event()
        self._business_thread = BusinessThread(
            platform=args.platform,
            job=args.job,
            region=args.region,
            stop_event=self._stop_event,
            on_finished=self._on_business_finished
        )
        self._is_business_running = True
        self._business_thread.start()
        self._set_button_to_interrupt()

    def on_interrupt_clicked(self):
        """立即中断：停止AI、关闭浏览器、退出程序（无弹窗）"""
        if self._stop_event:
            self._stop_event.set()

        try:
            from pages.start_copaw import stop_ai
            stop_ai()
            print("AI 服务已停止")
        except Exception as e:
            print(f"停止 AI 失败: {e}")

        try:
            from pages.get_web import DriverManager
            DriverManager.close_driver()
            print("浏览器驱动已通过 DriverManager 关闭")
        except Exception as e:
            print(f"关闭驱动失败: {e}")

        self.close()

    def _on_business_finished(self):
        """业务线程结束后的回调"""
        self._is_business_running = False
        self._set_button_to_start()
        self.login_button.setEnabled(True)
        self.update_start_button_state()
        print("业务线程已结束，界面已恢复")


    def parse_args(self):
        import argparse
        parser = argparse.ArgumentParser(description="招聘岗位智能筛选系统")
        parser.add_argument("--platform", choices=["boss", "zlzp", "all"], default="all",
                            help="指定爬取平台（boss/zlzp/all）")
        parser.add_argument("--job", type=str, default=None, help="指定目标岗位（覆盖.env中的TARGET_JOB_NAME）")
        parser.add_argument("--region", type=str, default=None, help="指定目标地区（覆盖.env中的TARGET_REGION）")
        return parser.parse_args()


def create_env_file():
    """创建示例.env文件"""
    env_content = """# 系统配置文件
            # 岗位名称
            TARGET_JOB_NAME=Python开发工程师

            # 目标地区
            TARGET_REGION=北京

            # 工作经验
            WORK_EXPERIENCE=3-5年

            # 学历要求
            DEGREE_REQUIREMENT=本科"""

    env_path = Path('.env')
    if not env_path.exists():
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"已创建示例配置文件: {env_path}")


import threading
import traceback


class BusinessThread(QThread):
    finished_signal = Signal()

    def __init__(self, platform, job, region, stop_event, on_finished=None):
        super().__init__()
        self.platform = platform
        self.job = job
        self.region = region
        self.stop_event = stop_event
        self._on_finished = on_finished   # ✅ 关键：保存回调
        if self._on_finished:
            self.finished_signal.connect(self._on_finished)

    def run(self):
        try:
            import os
            from business.recruit_business import RecruitBusiness
            from pages.get_web import DriverManager
            from pages.email_page import send_email

            if self.job:
                os.environ['TARGET_JOB_NAME'] = self.job
            if self.region:
                os.environ['TARGET_REGION'] = self.region

            if self.stop_event.is_set():
                print("业务被中断，停止执行。")
                return

            app = RecruitBusiness(headless=False)

            # ✅ 与 main.py 同步：根据平台执行并发送邮件
            if self.platform in ["boss", "all"]:
                if self.stop_event.is_set():
                    print("中断：跳过BOSS处理。")
                    return
                aip = app.boss_ints()
                if aip:
                    send_email('BOSS运行结束', ','.join(aip) if isinstance(aip, list) else aip)
                else:
                    send_email('BOSS运行失败', '未登录')

            if self.platform in ["zlzp", "all"]:
                if self.stop_event.is_set():
                    print("中断：跳过智联处理。")
                    return
                aip = app.zlzp_ints()
                if aip:
                    send_email('智联招聘运行结束', ','.join(aip) if isinstance(aip, list) else aip)
                else:
                    send_email('智联招聘运行失败', '未登录')

            DriverManager.close_driver()
            print("业务执行完成")
        except Exception as e:
            print(f"业务异常：{e}")
            traceback.print_exc()
        finally:
            # 发射信号，确保在主线程中调用回调
            self.finished_signal.emit()


def main():
    create_env_file()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = LoginSoftware()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


