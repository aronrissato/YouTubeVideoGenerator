"""
Interface de configuração interativa para o gerador de vídeos
"""
from .config import video_config

class ConfigUI:
    """Interface de usuário para configurações"""
    
    def __init__(self):
        self.config = video_config
    
    def show_main_menu(self):
        """Mostra menu principal de configurações"""
        while True:
            print("\n" + "=" * 60)
            print("CONFIGURAÇÕES DO GERADOR DE VÍDEOS")
            print("=" * 60)
            
            # Mostrar configurações atuais
            self.show_current_config()
            
            print("\nOpções:")
            print("1. Configurar assunto do vídeo")
            print("2. Configurar duração do vídeo")
            print("3. Configurar idioma")
            print("4. Configurar velocidade da voz")
            print("5. Configurar volume da voz")
            print("6. Configurar qualidade de vídeo")
            print("7. Configurar estilo do vídeo")
            print("8. Configurar música de fundo")
            print("9. Configurações avançadas")
            print("10. Reset para padrões")
            print("11. Salvar e sair")
            print("0. Sair sem salvar")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == '1':
                self.configure_subject()
            elif choice == '2':
                self.configure_duration()
            elif choice == '3':
                self.configure_language()
            elif choice == '4':
                self.configure_voice_speed()
            elif choice == '5':
                self.configure_voice_volume()
            elif choice == '6':
                self.configure_video_quality()
            elif choice == '7':
                self.configure_video_style()
            elif choice == '8':
                self.configure_background_music()
            elif choice == '9':
                self.configure_advanced()
            elif choice == '10':
                self.reset_to_default()
            elif choice == '11':
                self.save_and_exit()
                break
            elif choice == '0':
                if self.confirm_exit():
                    break
            else:
                print("Opção inválida. Tente novamente.")
    
    def show_current_config(self):
        """Mostra configurações atuais"""
        print("\nConfigurações atuais:")
        print("-" * 40)
        
        subject_options = self.config.get_subject_options()
        language_options = self.config.get_language_options()
        voice_options = self.config.get_voice_options()
        quality_options = self.config.get_quality_options()
        style_options = self.config.get_style_options()
        
        print(f"Assunto: {subject_options.get(self.config.get('subject'), 'Desconhecido')}")
        
        duration = self.config.get('duration')
        if duration == 'auto':
            print("Duração: Automática (baseada no conteúdo)")
        else:
            print(f"Duração: {duration} minutos")
        
        print(f"Idioma: {language_options.get(self.config.get('language'), 'Desconhecido')}")
        print(f"Velocidade da voz: {self.config.get('voice_speed')}x")
        print(f"Volume da voz: {int(self.config.get('voice_volume', 1.0) * 100)}%")
        print(f"Gênero da voz: {voice_options.get(self.config.get('voice_gender'), 'Desconhecido')}")
        print(f"Qualidade: {quality_options.get(self.config.get('video_quality'), 'Desconhecido')}")
        print(f"Estilo do vídeo: {style_options['video_style'].get(self.config.get('video_style'), 'Desconhecido')}")
        print(f"Música de fundo: {'Sim' if self.config.get('background_music') else 'Não'}")
        
        if self.config.get('background_music'):
            print(f"Volume da música: {int(self.config.get('background_music_volume', 0.3) * 100)}%")
    
    def configure_subject(self):
        """Configura assunto do vídeo"""
        print("\n" + "-" * 40)
        print("CONFIGURAR ASSUNTO DO VÍDEO")
        print("-" * 40)
        
        options = self.config.get_subject_options()
        
        print("Opções disponíveis:")
        for i, (key, description) in enumerate(options.items(), 1):
            print(f"{i}. {description}")
        
        while True:
            choice = input(f"\nEscolha uma opção (1-{len(options)}): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected_key = list(options.keys())[choice_num - 1]
                    self.config.set('subject', selected_key)
                    print(f"Assunto configurado: {options[selected_key]}")
                    break
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("Digite um número válido.")
    
    def configure_duration(self):
        """Configura duração do vídeo"""
        print("\n" + "-" * 40)
        print("CONFIGURAR DURAÇÃO DO VÍDEO")
        print("-" * 40)
        
        print("Opções:")
        print("1. Automática (baseada no conteúdo)")
        print("2. Personalizada (em minutos)")
        
        while True:
            choice = input("Escolha uma opção (1-2): ").strip()
            
            if choice == '1':
                self.config.set('duration', 'auto')
                print("Duração configurada: Automática")
                break
            elif choice == '2':
                while True:
                    try:
                        duration = float(input("Digite a duração em minutos (1-180): "))
                        if 1 <= duration <= 180:
                            self.config.set('duration', duration)
                            print(f"Duração configurada: {duration} minutos")
                            break
                        else:
                            print("Duração deve estar entre 1 e 180 minutos.")
                    except ValueError:
                        print("Digite um número válido.")
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def configure_language(self):
        """Configura idioma"""
        print("\n" + "-" * 40)
        print("CONFIGURAR IDIOMA")
        print("-" * 40)
        
        options = self.config.get_language_options()
        
        print("Idiomas disponíveis:")
        for i, (key, description) in enumerate(options.items(), 1):
            print(f"{i}. {description}")
        
        while True:
            choice = input(f"\nEscolha um idioma (1-{len(options)}): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected_key = list(options.keys())[choice_num - 1]
                    self.config.set('language', selected_key)
                    print(f"Idioma configurado: {options[selected_key]}")
                    break
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("Digite um número válido.")
    
    def configure_voice_speed(self):
        """Configura velocidade da voz"""
        print("\n" + "-" * 40)
        print("CONFIGURAR VELOCIDADE DA VOZ")
        print("-" * 40)
        
        print("Opções rápidas:")
        print("1. Muito lenta (0.5x)")
        print("2. Lenta (0.7x)")
        print("3. Normal (1.0x) - Padrão")
        print("4. Rápida (1.3x)")
        print("5. Muito rápida (1.6x)")
        print("6. Personalizada")
        
        while True:
            choice = input("Escolha uma opção (1-6): ").strip()
            
            if choice == '1':
                self.config.set('voice_speed', 0.5)
                print("Velocidade configurada: Muito lenta (0.5x)")
                break
            elif choice == '2':
                self.config.set('voice_speed', 0.7)
                print("Velocidade configurada: Lenta (0.7x)")
                break
            elif choice == '3':
                self.config.set('voice_speed', 1.0)
                print("Velocidade configurada: Normal (1.0x)")
                break
            elif choice == '4':
                self.config.set('voice_speed', 1.3)
                print("Velocidade configurada: Rápida (1.3x)")
                break
            elif choice == '5':
                self.config.set('voice_speed', 1.6)
                print("Velocidade configurada: Muito rápida (1.6x)")
                break
            elif choice == '6':
                while True:
                    try:
                        speed = float(input("Digite a velocidade (0.5-3.0): "))
                        if 0.5 <= speed <= 3.0:
                            self.config.set('voice_speed', speed)
                            print(f"Velocidade configurada: {speed}x")
                            break
                        else:
                            print("Velocidade deve estar entre 0.5 e 3.0.")
                    except ValueError:
                        print("Digite um número válido.")
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def configure_voice_volume(self):
        """Configura volume da voz"""
        print("\n" + "-" * 40)
        print("CONFIGURAR VOLUME DA VOZ")
        print("-" * 40)
        
        print("Opções rápidas:")
        print("1. Muito baixo (25%)")
        print("2. Baixo (50%)")
        print("3. Normal (100%) - Padrão")
        print("4. Alto (125%)")
        print("5. Muito alto (150%)")
        print("6. Personalizado")
        
        while True:
            choice = input("Escolha uma opção (1-6): ").strip()
            
            if choice == '1':
                self.config.set('voice_volume', 0.25)
                print("Volume configurado: Muito baixo (25%)")
                break
            elif choice == '2':
                self.config.set('voice_volume', 0.5)
                print("Volume configurado: Baixo (50%)")
                break
            elif choice == '3':
                self.config.set('voice_volume', 1.0)
                print("Volume configurado: Normal (100%)")
                break
            elif choice == '4':
                self.config.set('voice_volume', 1.25)
                print("Volume configurado: Alto (125%)")
                break
            elif choice == '5':
                self.config.set('voice_volume', 1.5)
                print("Volume configurado: Muito alto (150%)")
                break
            elif choice == '6':
                while True:
                    try:
                        volume = float(input("Digite o volume (0.0-2.0): "))
                        if 0.0 <= volume <= 2.0:
                            self.config.set('voice_volume', volume)
                            print(f"Volume configurado: {int(volume * 100)}%")
                            break
                        else:
                            print("Volume deve estar entre 0.0 e 2.0.")
                    except ValueError:
                        print("Digite um número válido.")
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def configure_video_quality(self):
        """Configura qualidade do vídeo"""
        print("\n" + "-" * 40)
        print("CONFIGURAR QUALIDADE DO VÍDEO")
        print("-" * 40)
        
        options = self.config.get_quality_options()
        
        print("Qualidades disponíveis:")
        for i, (key, description) in enumerate(options.items(), 1):
            print(f"{i}. {description}")
        
        while True:
            choice = input(f"\nEscolha uma qualidade (1-{len(options)}): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected_key = list(options.keys())[choice_num - 1]
                    self.config.set('video_quality', selected_key)
                    print(f"Qualidade configurada: {options[selected_key]}")
                    break
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("Digite um número válido.")
    
    def configure_video_style(self):
        """Configura estilo do vídeo"""
        print("\n" + "-" * 40)
        print("CONFIGURAR ESTILO DO VÍDEO")
        print("-" * 40)
        
        options = self.config.get_style_options()['video_style']
        
        print("Estilos disponíveis:")
        for i, (key, description) in enumerate(options.items(), 1):
            print(f"{i}. {description}")
        
        while True:
            choice = input(f"\nEscolha um estilo (1-{len(options)}): ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected_key = list(options.keys())[choice_num - 1]
                    self.config.set('video_style', selected_key)
                    print(f"Estilo configurado: {options[selected_key]}")
                    break
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("Digite um número válido.")
    
    def configure_background_music(self):
        """Configura música de fundo"""
        print("\n" + "-" * 40)
        print("CONFIGURAR MÚSICA DE FUNDO")
        print("-" * 40)
        
        print("1. Ativar música de fundo")
        print("2. Desativar música de fundo")
        print("3. Ajustar volume")
        
        while True:
            choice = input("Escolha uma opção (1-3): ").strip()
            
            if choice == '1':
                self.config.set('background_music', True)
                print("Música de fundo: Ativada")
                break
            elif choice == '2':
                self.config.set('background_music', False)
                print("Música de fundo: Desativada")
                break
            elif choice == '3':
                while True:
                    try:
                        volume = float(input("Digite o volume (0.0-1.0): "))
                        if 0.0 <= volume <= 1.0:
                            self.config.set('background_music_volume', volume)
                            print(f"Volume configurado: {int(volume * 100)}%")
                            break
                        else:
                            print("Volume deve estar entre 0.0 e 1.0.")
                    except ValueError:
                        print("Digite um número válido.")
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def configure_advanced(self):
        """Configurações avançadas"""
        print("\n" + "-" * 40)
        print("CONFIGURAÇÕES AVANÇADAS")
        print("-" * 40)
        
        print("1. Configurar gênero da voz")
        print("2. Adicionar queries personalizadas")
        print("3. Configurar YouTube")
        print("4. Voltar")
        
        while True:
            choice = input("Escolha uma opção (1-4): ").strip()
            
            if choice == '1':
                self.configure_voice_gender()
            elif choice == '2':
                self.configure_custom_queries()
            elif choice == '3':
                self.configure_youtube()
            elif choice == '4':
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def configure_voice_gender(self):
        """Configura gênero da voz"""
        print("\nConfigurar gênero da voz:")
        options = self.config.get_voice_options()
        
        for i, (key, description) in enumerate(options.items(), 1):
            print(f"{i}. {description}")
        
        while True:
            choice = input("Escolha uma opção: ").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    selected_key = list(options.keys())[choice_num - 1]
                    self.config.set('voice_gender', selected_key)
                    print(f"Gênero configurado: {options[selected_key]}")
                    break
                else:
                    print("Opção inválida. Tente novamente.")
            else:
                print("Digite um número válido.")
    
    def configure_custom_queries(self):
        """Configura queries personalizadas"""
        print("\nConfigurar queries personalizadas:")
        print("(Queries são termos de busca para vídeos no Pexels)")
        
        current_queries = self.config.get('custom_queries', [])
        
        if current_queries:
            print("\nQueries atuais:")
            for i, query in enumerate(current_queries, 1):
                print(f"{i}. {query}")
        
        print("\nOpções:")
        print("1. Adicionar query")
        print("2. Remover query")
        print("3. Limpar todas")
        print("4. Voltar")
        
        while True:
            choice = input("Escolha uma opção (1-4): ").strip()
            
            if choice == '1':
                query = input("Digite a nova query: ").strip()
                if query:
                    current_queries.append(query)
                    self.config.set('custom_queries', current_queries)
                    print(f"Query adicionada: {query}")
            elif choice == '2':
                if current_queries:
                    try:
                        index = int(input("Digite o número da query a remover: ")) - 1
                        if 0 <= index < len(current_queries):
                            removed = current_queries.pop(index)
                            self.config.set('custom_queries', current_queries)
                            print(f"Query removida: {removed}")
                        else:
                            print("Número inválido.")
                    except ValueError:
                        print("Digite um número válido.")
                else:
                    print("Não há queries para remover.")
            elif choice == '3':
                if current_queries:
                    if input("Tem certeza? (s/n): ").lower() == 's':
                        self.config.set('custom_queries', [])
                        current_queries = []
                        print("Todas as queries foram removidas.")
                else:
                    print("Não há queries para limpar.")
            elif choice == '4':
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def configure_youtube(self):
        """Configura YouTube"""
        print("\nConfigurar YouTube:")
        
        youtube_settings = self.config.get('youtube_settings', {})
        
        print("1. Configurar privacidade")
        print("2. Configurar categoria")
        print("3. Auto-publicação")
        print("4. Voltar")
        
        while True:
            choice = input("Escolha uma opção (1-4): ").strip()
            
            if choice == '1':
                print("\nOpções de privacidade:")
                print("1. Privado")
                print("2. Não listado")
                print("3. Público")
                
                privacy_choice = input("Escolha (1-3): ").strip()
                
                if privacy_choice == '1':
                    youtube_settings['privacy'] = 'private'
                elif privacy_choice == '2':
                    youtube_settings['privacy'] = 'unlisted'
                elif privacy_choice == '3':
                    youtube_settings['privacy'] = 'public'
                
                self.config.set('youtube_settings', youtube_settings)
                print(f"Privacidade configurada: {youtube_settings['privacy']}")
                
            elif choice == '2':
                category = input("Digite o ID da categoria (22 = People & Blogs): ").strip()
                if category.isdigit():
                    youtube_settings['category'] = category
                    self.config.set('youtube_settings', youtube_settings)
                    print(f"Categoria configurada: {category}")
                else:
                    print("Digite um número válido.")
                    
            elif choice == '3':
                auto_publish = input("Auto-publicar? (s/n): ").lower() == 's'
                youtube_settings['auto_publish'] = auto_publish
                self.config.set('youtube_settings', youtube_settings)
                print(f"Auto-publicação: {'Ativada' if auto_publish else 'Desativada'}")
                
            elif choice == '4':
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def reset_to_default(self):
        """Reset para configurações padrão"""
        print("\n" + "-" * 40)
        print("RESET PARA CONFIGURAÇÕES PADRÃO")
        print("-" * 40)
        
        if input("Tem certeza que deseja resetar todas as configurações? (s/n): ").lower() == 's':
            self.config.reset_to_default()
            print("Configurações resetadas para os valores padrão.")
        else:
            print("Operação cancelada.")
    
    def save_and_exit(self):
        """Salva configurações e sai"""
        # Validar configurações
        errors = self.config.validate_config()
        
        if errors:
            print("\nErros encontrados nas configurações:")
            for error in errors:
                print(f"- {error}")
            
            if input("\nDeseja corrigir os erros? (s/n): ").lower() != 's':
                print("Configurações salvas com erros.")
        
        self.config.save_config()
        print("\nConfigurações salvas com sucesso!")
    
    def confirm_exit(self):
        """Confirma saída sem salvar"""
        return input("\nTem certeza que deseja sair sem salvar? (s/n): ").lower() == 's'

def main():
    """Função principal"""
    config_ui = ConfigUI()
    config_ui.show_main_menu()

if __name__ == "__main__":
    main()
