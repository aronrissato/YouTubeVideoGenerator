#!/usr/bin/env python3
"""
Script de execução principal simplificado
Utiliza o padrão de orquestração para seguir princípios SOLID
"""
import os
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video.video_generation_orchestrator import VideoGenerationOrchestrator


def main():
    """Executa o gerador de vídeos bíblicos usando orquestração"""
    orchestrator = VideoGenerationOrchestrator()
    orchestrator.execute()


if __name__ == "__main__":
    main()
