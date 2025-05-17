import os
import pygame

def load_asset(filename, subfolder="assets"):
    """Carrega um asset da pasta assets com tratamento de erros"""
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, subfolder, filename)
        return pygame.image.load(full_path)
    except Exception as e:
        print(f"Erro ao carregar asset {filename}: {e}")
        return None
    
def load_audio(filename, subfolder="assets"):
    """Carrega um arquivo de áudio da pasta assets com tratamento de erros"""
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, subfolder, filename)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {full_path}")
            
        sound = pygame.mixer.Sound(full_path)
        print(f"Áudio carregado com sucesso: {filename}")
        return sound
        
    except Exception as e:
        print(f"ERRO ao carregar áudio {filename}: {str(e)}")
        return None