import sys
import os

# Esta función ayuda a encontrar archivos cuando el programa ya está convertido en un ejecutable (exe).
# Si estamos probando el código, busca en la carpeta normal.
# Pero si es un exe, busca en una carpeta temporal especial donde Nuitka pone las cosas.
def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta de un recurso, compatible con desarrollo y Nuitka (onefile).
    """
    if hasattr(sys, 'frozen'):
        # Estamos corriendo como un ejecutable (creado con Nuitka o PyInstaller)
        # sys._MEIPASS es usado por PyInstaller, pero Nuitka suele usar el directorio del ejecutable o temp.
        # Para Nuitka --onefile, a menudo se extrae en un temp, pero sys.executable está donde el exe.
        # Sin embargo, la forma estándar segura suele ser confiar en relative paths desde el root descomprimido.
        # Vamos a asumir que los recursos están junto al ejecutable o en el temp base.
        base_path = os.path.dirname(sys.executable)
    else:
        # Estamos corriendo en modo desarrollo (desde el código fuente)
        # La ruta base es la carpeta superior a 'utils', que es la raíz del proyecto
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)
