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