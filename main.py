import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

# Este es el punto de entrada, el archivo que inica todo.
def main():
    # Creamos la aplicación Qt
    app = QApplication(sys.argv)
    
    # Creamos y mostramos la ventana principal
    window = MainWindow()
    window.show()
    
    # Iniciamos el bucle de eventos, que mantiene la ventana abierta y respondiendo
    sys.exit(app.exec())

# Ejecución principal
if __name__ == "__main__":
    main()
