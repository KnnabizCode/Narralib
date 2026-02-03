from pydub import AudioSegment
import os

# Este módulo se encarga de trabajar con los archivos de audio, como unirlos si es necesario.
class AudioBuilder:
    def combine_mp3(self, file_list, output_file):
        if not file_list:
            return False
            
        combined = AudioSegment.empty()
        
        try:
            for file in file_list:
                # Cargamos cada audio
                audio = AudioSegment.from_mp3(file)
                combined += audio
                
            # Guardamos el resultado final
            combined.export(output_file, format="mp3")
            return True
        except Exception as e:
            print(f"Error al unir audios: {e}")
            return False

    def check_audio_exists(self, path):
        return os.path.exists(path) and os.path.getsize(path) > 0
