import pygame
import time
from utils import load_audio

AUDIO_FILE = load_audio("caueta_voice.mp3")
VOLUME = 0.7 
PLAY_TIMES = 3  
INTERVAL_SEC = 1.0

pygame.mixer.init()
sound = None

def _load_sound():
    """Carrega o arquivo de áudio (chamado automaticamente)"""
    global sound
    try:
        sound = pygame.mixer.Sound(AUDIO_FILE)
        sound.set_volume(VOLUME)
        return True
    except Exception as e:
        print(f"[ERRO] Não foi possível carregar {AUDIO_FILE}: {e}")
        return False

# Tenta carregar o som ao importar
if _load_sound():
    print(f"Áudio {AUDIO_FILE} carregado com sucesso!")
else:
    print(f"Falha ao carregar {AUDIO_FILE}. Verifique se o arquivo existe.")

def playVoice():
    if sound is None:
        print("[ERRO] Áudio não carregado. Verifique o arquivo ou caminho.")
        return
    sound.play()