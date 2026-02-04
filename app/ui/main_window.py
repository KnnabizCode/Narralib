from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFileDialog, QProgressBar, 
                               QComboBox, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize, QUrl, QEvent
from PySide6.QtGui import QIcon, QMouseEvent, QEnterEvent, QDesktopServices
from app.core.task_manager import ConversionWorker
from app.core.tts_engine import TTSEngine
from app.utils.paths import get_resource_path
from app.core.config_manager import ConfigManager
from app.core.updater import check_for_updates
import os

# Etiqueta clickeable que actúa como un hipervínculo
class WebLinkLabel(QLabel):
    def __init__(self, text: str, url: str, parent: None = None) -> None:
        super().__init__(text, parent)
        self.url = url
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        # Abre la URL en el navegador predeterminado
        QDesktopServices.openUrl(QUrl(self.url))
        
    def enterEvent(self, event: QEnterEvent) -> None:
        # Resalta el texto al pasar el mouse por encima
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        super().enterEvent(event)
        
    def leaveEvent(self, event: QEvent) -> None:
        # Restaura el estilo original al salir el mouse
        font = self.font()
        font.setBold(False)
        self.setFont(font)
        super().leaveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        
        self.setWindowTitle("Narralib")
        self.setMinimumSize(600, 450)
        
        # Intentamos cargar el icono
        icon_path = get_resource_path("icons/icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setup_ui()
        self.load_voices()
        self.apply_theme()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Encabezado y Tema
        header_layout = QHBoxLayout()
        title_label = QLabel("Narralib")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #89b4fa;")
        
        # Botón de Actualización
        self.update_btn = QPushButton("🔄")
        self.update_btn.setFixedSize(46, 46)
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setToolTip("Buscar Actualizaciones")
        self.update_btn.clicked.connect(self.manual_update_check)
        
        # Botón de Tema
        self.theme_btn = QPushButton("☀️")
        self.theme_btn.setFixedSize(46, 46)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.update_btn)
        header_layout.addWidget(self.theme_btn)
        main_layout.addLayout(header_layout)
        
        # Selección de Archivo
        self.file_frame = QFrame()
        # El estilo se define en apply_theme
        file_layout = QHBoxLayout(self.file_frame)
        
        self.file_label = QLabel("Selecciona un archivo PDF para empezar")
        self.file_label.setStyleSheet("background: transparent;")
        select_btn = QPushButton("Abrir PDF")
        select_btn.clicked.connect(self.select_pdf)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(select_btn)
        main_layout.addWidget(self.file_frame)
        
        # Opciones
        options_layout = QHBoxLayout()
        
        # Voz
        voice_layout = QVBoxLayout()
        voice_label = QLabel("Voz:")
        self.voice_combo = QComboBox()
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        
        # Velocidad
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Velocidad:")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["-20%", "-10%", "+0%", "+10%", "+20%"])
        self.speed_combo.setCurrentText("+0%")
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_combo)
        
        options_layout.addLayout(voice_layout, stretch=2)
        options_layout.addLayout(speed_layout, stretch=1)
        main_layout.addLayout(options_layout)
        
        # Progreso y Acción
        progress_layout = QVBoxLayout()
        self.status_label = QLabel("Listo")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        self.start_btn = QPushButton("Convertir a Audio")
        self.start_btn.setMinimumHeight(45)
        # El color del botón principal se gestiona en apply_theme preferiblemente, 
        # pero mantenemos el color de acento azul original.
        self.start_btn.setStyleSheet("background-color: #89b4fa; color: #1e1e2e; font-size: 16px;")
        self.start_btn.clicked.connect(self.start_conversion)
        self.start_btn.setEnabled(False) # Desactivado hasta que haya archivo
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addSpacing(10)
        progress_layout.addWidget(self.start_btn)
        
        main_layout.addStretch()
        main_layout.addLayout(progress_layout)

        # Enlace del pie de página
        self.footer_link = WebLinkLabel("Web: knnabiz.vip", "https://knnabiz.vip")
        main_layout.addWidget(self.footer_link)
        
        self.selected_pdf = None

    def apply_theme(self):
        # Aplica los colores y estilos CSS basados en el tema seleccionado (Adaptado de Reference)
        current_theme = str(self.config.get("theme", "dark"))
        
        if current_theme == "dark":
            # Colores oscuros (#1e1e2e)
            bg_color = "#1e1e2e"
            text_color = "#ffffff"
            btn_bg = "#313244"
            btn_text = "#cdd6f4"
            btn_hover = "#45475a"
            
            # Estilo frame archivo
            self.file_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); border-radius: 8px;")
            
            theme_btn_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: 1px solid {btn_hover};
                    border-radius: 23px;
                    font-size: 16px;
                    padding: 0px;
                    margin: 0px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                    border-color: {text_color};
                }}
            """
            
            # Estilo del footer link para modo oscuro
            self.footer_link.setStyleSheet(f"color: {text_color}; margin-top: 10px; font-size: 12px;")

        else:
            # Modo Claro - Paleta Profesional
            bg_color = "#FAFAFA" # Blanco roto para reducir fatiga visual
            text_color = "#1F2937" # Gris muy oscuro para alto contraste
            btn_bg = "#FFFFFF" # Superficie blanca
            btn_text = "#374151" # Gris oscuro
            btn_hover = "#F3F4F6" # Gris muy claro para hover
            
            # Estilo del frame de archivo con un borde sutil en lugar de contraste fuerte
            self.file_frame.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 8px;
                }
            """)
            
            theme_btn_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: 1px solid #D1D5DB;
                    border-radius: 23px;
                    font-size: 16px;
                    padding: 0px;
                    margin: 0px;
                }}
                QPushButton:hover {{
                    background-color: #E5E7EB;
                    border-color: {text_color};
                }}
                QPushButton:pressed {{
                    background-color: #D1D5DB;
                }}
            """
            
            # Estilo del footer link para modo claro
            self.footer_link.setStyleSheet(f"color: {text_color}; margin-top: 10px; font-size: 12px;")

        self.theme_btn.setText("🌙" if current_theme == "light" else "☀️")
        self.theme_btn.setStyleSheet(theme_btn_style)
        self.update_btn.setStyleSheet(theme_btn_style)
        
        # Configuración global de estilos
        if current_theme == "dark":
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: {bg_color}; }}
                QWidget {{ font-family: 'Segoe UI', sans-serif; color: {text_color}; }}
                QLabel {{ color: {text_color}; font-size: 14px; }}
                QPushButton {{ 
                    background-color: {btn_bg}; 
                    color: {btn_text}; 
                    border: none; 
                    padding: 8px 16px; 
                    border-radius: 4px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {btn_hover}; }}
                QPushButton:pressed {{ background-color: #585b70; }}
                QPushButton:disabled {{ background-color: #1e1e2e; color: #585b70; border: 1px solid #313244; }}
                
                QComboBox {{ 
                    background-color: {btn_bg}; 
                    color: {btn_text}; 
                    border: 1px solid {btn_hover}; 
                    padding: 5px; 
                    border-radius: 4px;
                }}
                QComboBox::drop-down {{ border: none; }}
                QComboBox QAbstractItemView {{
                    border: 1px solid {btn_hover};
                    selection-background-color: {btn_hover};
                    selection-color: {text_color};
                    background-color: {btn_bg};
                    color: {text_color};
                    outline: none;
                }}
                
                QProgressBar {{ 
                    border: 1px solid {btn_hover}; 
                    border-radius: 4px; 
                    text-align: center; 
                    color: {btn_text};
                }}
                QProgressBar::chunk {{ background-color: #89b4fa; border-radius: 3px; }}
                QFrame {{ border: none; }}
            """)
        else:
            # Aplicacion de estilos QSS para Modo Claro
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {bg_color};
                }}
                QWidget {{
                    font-family: 'Segoe UI', sans-serif;
                    color: {text_color};
                }}
                QLabel {{
                    color: {text_color};
                    font-size: 14px;
                }}
                QPushButton {{
                    background-color: {btn_bg};
                    color: {btn_text};
                    border: 1px solid #E5E7EB; /* Borde sutil */
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                    border: 1px solid #D1D5DB;
                }}
                QPushButton:pressed {{
                    background-color: #E5E7EB;
                    border: 1px solid #9CA3AF;
                }}
                QPushButton:disabled {{
                    background-color: #F9FAFB;
                    color: #9CA3AF;
                    border: 1px solid #E5E7EB;
                }}
                
                QComboBox {{
                    background-color: {btn_bg};
                    color: {text_color};
                    border: 1px solid #D1D5DB;
                    padding: 5px 10px;
                    border-radius: 4px;
                }}
                QComboBox:hover {{
                    border: 1px solid #9CA3AF;
                    background-color: {btn_hover};
                }}
                QComboBox::drop-down {{
                    border: none;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {btn_bg};
                    color: {text_color};
                    border: 1px solid #D1D5DB;
                    selection-background-color: #F3F4F6;
                    selection-color: #111827;
                    outline: none;
                }}
                
                QProgressBar {{
                    border: 1px solid #D1D5DB;
                    background-color: #E5E7EB;
                    border-radius: 4px;
                    text-align: center;
                    color: #374151;
                    font-weight: bold;
                }}
                QProgressBar::chunk {{
                    background-color: #3B82F6; /* Azul vibrante */
                    border-radius: 3px;
                }}
                /* El frame se estiliza especificamente arriba, esto es reset general */
                QFrame {{
                    border: none;
                }}
            """)
            
    def toggle_theme(self):
        current = str(self.config.get("theme", "dark"))
        new_theme = "light" if current == "dark" else "dark"
        self.config.set("theme", new_theme)
        self.apply_theme()

    def load_voices(self):
        tts = TTSEngine()
        voices = tts.get_voices()
        for v in voices:
            friendly_name = f"{v['ShortName'].split('-')[-1]} ({v['Gender']})"
            self.voice_combo.addItem(friendly_name, v['ShortName'])

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar PDF", "", "Archivos PDF (*.pdf)")
        if file_path:
            self.selected_pdf = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.start_btn.setEnabled(True)

    def start_conversion(self):
        if not self.selected_pdf:
            return
            
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar Audio", "", "Audio MP3 (*.mp3)")
        if not save_path:
            return
            
        if not save_path.lower().endswith('.mp3'):
            save_path += '.mp3'
            
        self.start_btn.setEnabled(False)
        self.theme_btn.setEnabled(False)
        self.update_btn.setEnabled(False)
        self.file_label.setEnabled(False)
        self.progress_bar.setValue(0)
        
        voice = self.voice_combo.currentData()
        speed = self.speed_combo.currentText()
        
        self.worker = ConversionWorker(self.selected_pdf, voice, speed, save_path)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_status.connect(self.update_status)
        self.worker.finished_task.connect(self.on_finished)
        
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, text):
        self.status_label.setText(text)

    def on_finished(self, success, message):
        self.start_btn.setEnabled(True)
        self.theme_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.file_label.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Éxito", message)
            self.status_label.setText("Listo")
            self.progress_bar.setValue(100)
        else:
            QMessageBox.critical(self, "Error", message)
            self.status_label.setText("Error")
            self.progress_bar.setValue(0)

    def manual_update_check(self):
        check_for_updates(self, force=True)
