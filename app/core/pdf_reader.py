import fitz

# Esta función se encarga de leer el archivo PDF y sacar todo el texto que tiene adentro.
def extract_text_from_pdf(pdf_path):
    texto_completo = ""
    
    try:
        # Abrimos el documento PDF usando la herramienta fitz
        documento = fitz.open(pdf_path)
        
        # Vamos página por página para leer lo que dice
        for pagina in documento:
            # Extraemos las palabras de la página actual
            texto_completo += pagina.get_text() + "\n"
            
        documento.close()
        return texto_completo
        
    except Exception as e:
        print(f"Hubo un error al leer el PDF: {e}")
        return ""
