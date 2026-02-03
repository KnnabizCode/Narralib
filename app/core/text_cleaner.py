import re

# Esta función limpia el texto para quitar cosas que no nos sirven, como espacios extra o caracteres raros.
def clean_text(texto):
    if not texto:
        return ""

    # Quitamos espacios extra al principio y al final
    texto = texto.strip()
    
    # Reemplazamos saltos de línea múltiples por un solo espacio, para que no haga pausas raras
    # \s+ significa "uno o más espacios en blanco (incluyendo enter)"
    texto = re.sub(r'\s+', ' ', texto)
    
    # Aquí podríamos quitar números de página o encabezados si tuviéramos un patrón claro,
    # pero por ahora haremos una limpieza básica.
    
    return texto
