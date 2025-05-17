import pygame
from utils import load_audio

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}  # Dicionário para armazenar os sons carregados
        self.volume = 0.7  # Volume padrão

    def load_sound(self, sound_name, file_path):
        """Carrega um arquivo de áudio e armazena com um nome identificador"""
        try:
            sound = pygame.mixer.Sound(load_audio(file_path))
            sound.set_volume(self.volume)
            self.sounds[sound_name] = sound
            print(f"Áudio '{sound_name}' carregado com sucesso!")
            return True
        except Exception as e:
            print(f"[ERRO] Não foi possível carregar {file_path}: {e}")
            return False

    def play(self, sound_name, loops=0, maxtime=0, fade_ms=0):
        """
        Reproduz um áudio carregado
        Parâmetros:
            sound_name: Nome do áudio pré-carregado
            loops: Número de repetições (-1 para infinito)
            maxtime: Tempo máximo de reprodução em ms
            fade_ms: Tempo de fade-in em ms
        """
        if sound_name not in self.sounds:
            print(f"[ERRO] Áudio '{sound_name}' não foi carregado")
            return

        self.sounds[sound_name].play(loops=loops, maxtime=maxtime, fade_ms=fade_ms)

    def set_volume(self, volume):
        """Ajusta o volume para todos os sons (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

# Instância global pronta para uso
audio = AudioPlayer()