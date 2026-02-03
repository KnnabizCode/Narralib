import edge_tts
import asyncio

# Esta clase se encarga de convertir el texto a voz usando el servicio de Edge.
class TTSEngine:
    def __init__(self):
        self.voice = "es-ES-AlvaroNeural" # Voz por defecto
        self.rate = "+0%" # Velocidad normal

    async def _generate_audio_async(self, text, output_file):
        openai_tts = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await openai_tts.save(output_file)

    def generate_audio(self, text, output_file, voice=None, rate=None):
        if voice:
            self.voice = voice
        if rate:
            self.rate = rate
            
        try:
            # Creamos un bucle para ejecutar la tarea asíncrona y esperamos a que termine
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_audio_async(text, output_file))
            loop.close()
            return True
        except Exception as e:
            print(f"Error al generar audio: {e}")
            return False

    async def get_voices_async(self):
        voices = await edge_tts.list_voices()
        # Filtramos solo las voces en español para que sea más fácil
        spanish_voices = [v for v in voices if "es-" in v["ShortName"]]
        return spanish_voices

    def get_voices(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        voces = loop.run_until_complete(self.get_voices_async())
        loop.close()
        return voces
