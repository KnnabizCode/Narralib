from PySide6.QtCore import QThread, Signal
from app.core.pdf_reader import extract_text_from_pdf
from app.core.text_cleaner import clean_text
from app.core.tts_engine import TTSEngine
import os

# Este es el trabajador que hace las tareas pesadas en segundo plano
# para que la ventana no se congele.
class ConversionWorker(QThread):
    # Definimos las señales para comunicarnos con la ventana principal
    update_progress = Signal(int) # Para la barra de progreso
    update_status = Signal(str)   # Para el texto de estado
    finished_task = Signal(bool, str) # Cuando termina (éxito/fracaso, mensaje)
    
    def __init__(self, pdf_path, voice, speed, output_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.voice = voice
        self.speed = speed
        self.output_path = output_path
        self._is_running = True

    def run(self):
        try:
            self.update_progress.emit(10)
            self.update_status.emit("Leyendo PDF...")
            
            # Paso 1: Leer el PDF
            raw_text = extract_text_from_pdf(self.pdf_path)
            if not raw_text:
                self.finished_task.emit(False, "No se pudo leer el texto del PDF.")
                return

            if not self._is_running: return

            self.update_progress.emit(30)
            self.update_status.emit("Limpiando texto...")
            
            # Paso 2: Limpiar texto
            clean_txt = clean_text(raw_text)
            
            if not self._is_running: return
            
            self.update_progress.emit(50)
            self.update_status.emit("Generando audio (esto puede tardar)...")
            
            # Paso 3: Convertir a audio
            tts = TTSEngine()
            success = tts.generate_audio(clean_txt, self.output_path, self.voice, self.speed)
            
            if success:
                self.update_progress.emit(100)
                self.update_status.emit("¡Completado!")
                self.finished_task.emit(True, f"Audio guardado en: {self.output_path}")
            else:
                self.finished_task.emit(False, "Error al generar el audio con el servicio TTS.")
                
        except Exception as e:
            self.finished_task.emit(False, f"Ocurrió un error inesperado: {str(e)}")

    def stop(self):
        self._is_running = False
