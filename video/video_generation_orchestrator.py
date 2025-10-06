"""
Orquestrador principal para geração de vídeos bíblicos
Centraliza o fluxo de execução e aplica princípios SOLID
"""
import sys
import os
from typing import Optional
from .bible_video_generator import BibleVideoGenerator
from config.config_ui import ConfigUI
from config.config import video_config


class VideoGenerationOrchestrator:
    """Orquestra todo o processo de geração de vídeos bíblicos"""
    
    def __init__(self):
        self.generator = BibleVideoGenerator()
        self.config_ui = ConfigUI()
        self.current_book_name = None
    
    def execute(self):
        """Executa o fluxo principal do sistema"""
        try:
            self._display_welcome_message()
            
            if self._has_command_line_arguments():
                self._handle_command_line_execution()
            else:
                self._handle_interactive_execution()
                
        except KeyboardInterrupt:
            self._handle_interruption()
        except Exception as e:
            self._handle_unexpected_error(e)
    
    def _display_welcome_message(self):
        """Exibe mensagem de boas-vindas"""
        print("GERADOR DE VIDEOS BIBLICOS")
        print("=" * 50)
    
    def _has_command_line_arguments(self) -> bool:
        """Verifica se há argumentos na linha de comando"""
        return len(sys.argv) > 1
    
    def _handle_command_line_execution(self):
        """Gerencia execução via linha de comando"""
        command = sys.argv[1].lower()
        
        if command == 'config':
            self._open_configuration_interface()
        elif command == 'help':
            self._show_help()
        else:
            self._execute_single_book_generation(command)
    
    def _handle_interactive_execution(self):
        """Gerencia execução interativa completa"""
        self._show_interactive_menu()
    
    def _open_configuration_interface(self):
        """Abre interface de configuração"""
        self.config_ui.show_main_menu()
    
    def _show_help(self):
        """Exibe ajuda do sistema"""
        self._display_help_content()
    
    def _show_interactive_menu(self):
        """Exibe menu interativo e processa escolhas"""
        self._display_menu_options()
        choice = self._get_menu_choice()
        self._process_menu_choice(choice)
    
    def _display_menu_options(self):
        """Exibe opções do menu interativo"""
        print("Opções disponíveis:")
        print("1. Gerar vídeo")
        print("2. Configurar opções")
        print("3. Ver ajuda")
    
    def _get_menu_choice(self) -> str:
        """Obtém escolha do usuário no menu"""
        return input("\nEscolha uma opção (1-3): ").strip()
    
    def _process_menu_choice(self, choice: str):
        """Processa escolha do menu"""
        if choice == '2':
            self._open_configuration_interface()
        elif choice == '3':
            self._show_help()
        else:
            if choice != '1':
                print("Opção inválida. Executando geração de vídeo...")
            self._execute_interactive_generation()
    
    def _execute_single_book_generation(self, book_name: str):
        """Executa geração de vídeo para um livro específico"""
        self.current_book_name = book_name
        
        if not self._validate_book_exists(book_name):
            return
        
        self._display_generation_info(book_name)
        self._show_current_settings()
        
        if not self._validate_pexels_api_key():
            return
        
        publish_decision = self._get_publish_decision()
        
        result = self._generate_video(book_name, publish_decision)
        self._handle_generation_result(result, book_name)
    
    def _execute_interactive_generation(self):
        """Executa geração interativa completa"""
        self.generator.list_available_books()
        print("\n" + "=" * 50)
        
        book_name = self._select_book_interactively()
        if not book_name:
            return
        
        self.current_book_name = book_name
        
        self._display_generation_info(book_name)
        self._show_current_settings()
        
        pexels_key = self._get_pexels_api_key_interactively()
        if not pexels_key:
            return
        
        publish_decision = self._get_publish_decision()
        result = self._generate_video(book_name, publish_decision, pexels_key)
        self._handle_generation_result(result, book_name)
    
    def _calculate_estimated_duration(self, book_name: str) -> tuple:
        """
        Calcula a duração estimada do vídeo baseada no número de caracteres do texto
        Retorna (duração_em_minutos, caracteres, palavras_por_minuto)
        """
        try:
            # Obter texto do livro
            text = self.generator.text_generator.get_full_book_text(book_name)
            
            if not text:
                return (0, 0, 0)
            
            # Contar caracteres (sem espaços em branco extras)
            char_count = len(text.strip())
            
            # Configurações de velocidade da voz
            voice_speed = video_config.get('voice_speed', 1.0)
            
            # Palavras por minuto baseadas no idioma e velocidade
            language = video_config.get('language', 'en')
            
            # Palavras por minuto padrão por idioma (velocidade 1.0x)
            base_wpm = {
                'pt': 150, 'pt-BR': 150, 'pt-pt': 150,
                'en': 160, 'en-US': 160, 'en-GB': 160,
                'es': 155, 'fr': 150, 'de': 150, 'it': 150
            }
            
            words_per_minute = base_wpm.get(language, 160) * voice_speed
            
            # Estimar palavras baseado em caracteres (aproximadamente 5 caracteres por palavra)
            estimated_words = char_count / 5
            
            # Calcular duração em minutos
            duration_minutes = estimated_words / words_per_minute
            
            return (duration_minutes, char_count, words_per_minute)
            
        except Exception as e:
            print(f"Erro ao calcular duração estimada: {str(e)}")
            return (0, 0, 0)
    
    def _show_estimated_duration(self, book_name: str):
        """Exibe a duração estimada do vídeo no console"""
        print(f"\nCALCULANDO DURAÇÃO ESTIMADA PARA {book_name.upper()}")
        print("-" * 50)
        
        duration_minutes, char_count, wpm = self._calculate_estimated_duration(book_name)
        
        if duration_minutes > 0:
            hours = int(duration_minutes // 60)
            minutes = int(duration_minutes % 60)
            seconds = int((duration_minutes % 1) * 60)
            
            print(f"Caracteres no texto: {char_count:,}")
            print(f"Velocidade da voz: {video_config.get('voice_speed', 1.0)}x")
            print(f"Palavras por minuto: {wpm:.0f}")
            print(f"Duração estimada: {duration_minutes:.1f} minutos")
            
            if hours > 0:
                print(f"   ({hours}h {minutes:02d}m {seconds:02d}s)")
            else:
                print(f"   ({minutes}m {seconds:02d}s)")
            
            # Avisos baseados na duração
            if duration_minutes > 60:
                print("AVISO: Vídeo muito longo (>1h). Considere dividir em partes.")
            elif duration_minutes > 30:
                print("INFO: Vídeo longo (>30min). Pode levar mais tempo para processar.")
            elif duration_minutes < 5:
                print("INFO: Vídeo curto (<5min). Processamento será mais rápido.")
            
            print("-" * 50)
        else:
            print("Erro ao calcular duração estimada")
            print("-" * 50)
    
    def _validate_book_exists(self, book_name: str) -> bool:
        """Valida se o livro existe"""
        available_books = self.generator.text_generator.get_available_books()
        
        if book_name not in available_books:
            self._display_book_not_found_error(book_name, available_books)
            return False
        
        return True
    
    def _display_book_not_found_error(self, book_name: str, available_books: list):
        """Exibe erro de livro não encontrado"""
        print(f"ERRO: Livro '{book_name}' não encontrado.")
        print("Livros disponíveis:")
        for book in available_books[:10]:
            print(f"   - {book}")
        print("   ... (use 'python run.py' para ver todos)")
    
    def _display_generation_info(self, book_name: str):
        """Exibe informações sobre a geração"""
        print(f"Gerando vídeo para: {book_name.upper()}")
    
    def _show_current_settings(self):
        """Exibe configurações atuais"""
        print("\nConfigurações atuais:")
        print(f"- Assunto: {self._get_subject_description()}")
        print(f"- Idioma: {self._get_language_description()}")
        print(f"- Velocidade da voz: {video_config.get('voice_speed')}x")
        print(f"- Duração: {self._get_duration_description()}")
    
    def _get_subject_description(self) -> str:
        """Obtém descrição do assunto configurado"""
        return video_config.get_subject_options().get(video_config.get('subject'), 'Desconhecido')
    
    def _get_language_description(self) -> str:
        """Obtém descrição do idioma configurado"""
        return video_config.get_language_options().get(video_config.get('language'), 'Desconhecido')
    
    def _get_duration_description(self) -> str:
        """Obtém descrição da duração configurada"""
        duration = video_config.get('duration')
        return duration if duration != 'auto' else 'Automática'
    
    def _validate_pexels_api_key(self) -> bool:
        """Valida chave da API do Pexels"""
        pexels_key = os.getenv('PEXELS_API_KEY')
        if not pexels_key:
            self._display_pexels_key_error()
            return False
        return True
    
    def _display_pexels_key_error(self):
        """Exibe erro de chave do Pexels não configurada"""
        print("ERRO: PEXELS_API_KEY não configurada no arquivo .env")
        print("Configure a chave da API no arquivo .env ou passe como parâmetro")
    
    def _get_publish_decision(self) -> bool:
        """Obtém decisão de publicação no YouTube"""
        youtube_settings = video_config.get('youtube_settings', {})
        auto_publish = youtube_settings.get('auto_publish', False)
        
        if auto_publish:
            print("Auto-publicação ativada - vídeo será publicado automaticamente")
            return True
        else:
            return input("Publicar no YouTube? (s/n): ").strip().lower() == 's'
    
    def _generate_video(self, book_name: str, publish: bool, pexels_key: str = None) -> Optional[str]:
        """Gera o vídeo"""
        if not pexels_key:
            pexels_key = os.getenv('PEXELS_API_KEY')
        
        print(f"\nIniciando geração do vídeo...")
        return self.generator.generate_full_video(book_name, pexels_key, publish)
    
    def _handle_generation_result(self, result: Optional[str], book_name: str):
        """Processa resultado da geração"""
        if result:
            self._display_success_message(result)
            self._cleanup_after_success(book_name)
        else:
            self._display_failure_message()
            self._cleanup_after_failure(book_name)
    
    def _display_success_message(self, result: str):
        """Exibe mensagem de sucesso"""
        print(f"\nSUCESSO! Vídeo: {result}")
    
    def _display_failure_message(self):
        """Exibe mensagem de falha"""
        print("\nFALHA na geração do vídeo.")
    
    def _cleanup_after_success(self, book_name: str):
        """Executa limpeza após sucesso"""
        print("\nLimpando arquivos temporários...")
        self.generator._cleanup_temp_files(book_name)
    
    def _cleanup_after_failure(self, book_name: str):
        """Executa limpeza após falha"""
        print("Limpando arquivos temporários devido à falha...")
        self.generator._cleanup_temp_files(book_name)
    
    def _select_book_interactively(self) -> Optional[str]:
        """Seleciona livro de forma interativa"""
        while True:
            choice = input("\nDigite o número do livro ou o nome: ").strip()
            
            if choice.isdigit():
                book_name = self._select_book_by_number(choice)
                if book_name:
                    return book_name
            else:
                book_name = self._select_book_by_name(choice)
                if book_name:
                    return book_name
    
    def _select_book_by_number(self, choice: str) -> Optional[str]:
        """Seleciona livro pelo número"""
        try:
            books = self.generator.text_generator.get_available_books()
            return books[int(choice) - 1]
        except (ValueError, IndexError):
            print("ERRO: Número inválido. Tente novamente.")
            return None
    
    def _select_book_by_name(self, choice: str) -> Optional[str]:
        """Seleciona livro pelo nome"""
        book_name = choice.lower().replace(' ', '-')
        books = self.generator.text_generator.get_available_books()
        
        if book_name in books:
            return book_name
        else:
            print(f"ERRO: Livro '{book_name}' não encontrado. Tente novamente.")
            return None
    
    def _get_pexels_api_key_interactively(self) -> Optional[str]:
        """Obtém chave do Pexels de forma interativa"""
        pexels_key = os.getenv('PEXELS_API_KEY')
        
        if not pexels_key:
            print("AVISO: PEXELS_API_KEY não configurada no arquivo .env")
            pexels_key = input("Digite sua API Key do Pexels: ").strip()
            
            if not pexels_key:
                print("ERRO: API Key do Pexels é obrigatória para funcionamento completo")
                return None
        
        return pexels_key
    
    def _display_help_content(self):
        """Exibe conteúdo da ajuda"""
        print("\n" + "=" * 60)
        print("AJUDA - GERADOR DE VÍDEOS BÍBLICOS")
        print("=" * 60)
        
        print("\nCOMANDOS DISPONÍVEIS:")
        print("python run.py                    - Execução interativa completa")
        print("python run.py [nome-do-livro]    - Gerar vídeo de um livro específico")
        print("python run.py config             - Abrir configurações")
        print("python run.py help               - Mostrar esta ajuda")
        
        print("\nEXEMPLOS:")
        print("python run.py genesis            - Gerar vídeo do livro de Gênesis")
        print("python run.py salmos             - Gerar vídeo do livro de Salmos")
        print("python run.py config             - Configurar opções do sistema")
        
        print("\nCONFIGURAÇÕES DISPONÍVEIS:")
        print("- Assunto do vídeo (livro completo, capítulo, versículo, etc.)")
        print("- Duração do vídeo (automática ou personalizada)")
        print("- Idioma da narração (português, inglês, espanhol, etc.)")
        print("- Velocidade da voz (0.5x a 3.0x)")
        print("- Gênero da voz (masculina ou feminina)")
        print("- Qualidade do vídeo (720p, 1080p, 4K)")
        print("- Estilo do vídeo (dinâmico, calmo, dramático)")
        print("- Música de fundo (ativar/desativar e volume)")
        print("- Estilo das legendas (clássico, moderno, minimalista)")
        print("- Configurações do YouTube (privacidade, categoria, auto-publicação)")
        
        print("\nARQUIVOS DE CONFIGURAÇÃO:")
        print("- .env                     - Chaves de API (PEXELS_API_KEY, etc.)")
        print("- video_config.json        - Configurações personalizadas do vídeo")
        print("- client_secret.json       - Credenciais do YouTube")
        
        print("\nPASTAS DO PROJETO:")
        print("- output/                  - Vídeos finais gerados")
        print("- audio/                   - Arquivos de áudio da narração")
        print("- subtitles/               - Arquivos de legendas (.srt)")
        print("- pexels_videos/           - Vídeos baixados do Pexels")
        print("- temp/                    - Arquivos temporários")
        
        print("\nPARA MAIS INFORMAÇÕES:")
        print("Execute 'python run.py config' para configurar todas as opções")
    
    def _handle_interruption(self):
        """Gerencia interrupção pelo usuário"""
        print("\n\nProcesso interrompido pelo usuário.")
        self._perform_cleanup_on_interruption()
    
    def _handle_unexpected_error(self, error: Exception):
        """Gerencia erro inesperado"""
        print(f"\nErro inesperado: {str(error)}")
        import traceback
        traceback.print_exc()
        self._perform_cleanup_on_error()
    
    def _perform_cleanup_on_interruption(self):
        """Executa limpeza em caso de interrupção"""
        if self.current_book_name:
            print("Realizando limpeza devido à interrupção...")
            self.generator._cleanup_temp_files(self.current_book_name)
    
    def _perform_cleanup_on_error(self):
        """Executa limpeza em caso de erro"""
        if self.current_book_name:
            print("Realizando limpeza devido ao erro...")
            self.generator._cleanup_temp_files(self.current_book_name)
