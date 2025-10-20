#!/usr/bin/env python3
"""
Validador automático do sistema em português
"""
import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_config():
    """Verifica configuração do sistema"""
    print("1️⃣ Verificando configuração...")
    
    try:
        with open('video_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            language = config.get('language', 'not set')
            
            if language in ['pt', 'pt-BR']:
                print(f"   ✅ Idioma configurado: {language}")
                return True
            else:
                print(f"   ⚠️  Idioma atual: {language}")
                print(f"   💡 Configure para 'pt' ou 'pt-BR' em video_config.json")
                return False
    except:
        print("   ❌ Erro ao ler video_config.json")
        return False

def check_portuguese_books():
    """Verifica livros em português disponíveis"""
    print("\n2️⃣ Verificando livros em português...")
    
    count = 0
    books = []
    
    try:
        for filename in os.listdir('bible_data'):
            if filename.endswith('.json') and not filename.endswith('_backup.json'):
                filepath = os.path.join('bible_data', filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('language') == 'pt':
                        count += 1
                        books.append(filename.replace('.json', ''))
        
        if count > 0:
            print(f"   ✅ {count} livros em português disponíveis")
            print(f"   📚 Exemplos: {', '.join(sorted(books)[:5])}")
            if count < 66:
                print(f"   💡 Baixe mais livros com: python manage_bible_books.py")
            return True
        else:
            print(f"   ⚠️  Nenhum livro em português encontrado")
            print(f"   💡 Baixe livros com: python manage_bible_books.py")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def check_text_generator():
    """Verifica gerador de texto"""
    print("\n3️⃣ Verificando gerador de texto...")
    
    try:
        from text.bible_text_generator import BibleTextGenerator
        
        gen = BibleTextGenerator('pt')
        print(f"   ✅ BibleTextGenerator inicializado")
        
        # Testar normalização
        normalized = gen._normalize_language('pt-BR')
        if normalized == 'pt':
            print(f"   ✅ Normalização funciona: pt-BR → pt")
            return True
        else:
            print(f"   ⚠️  Normalização: pt-BR → {normalized}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def check_audio_generator():
    """Verifica gerador de áudio"""
    print("\n4️⃣ Verificando gerador de áudio...")
    
    try:
        from audio.audio_generator import AudioGenerator
        
        audio_gen = AudioGenerator(language='pt-BR', speed=1.0)
        print(f"   ✅ AudioGenerator inicializado")
        
        # Verificar voz Edge TTS
        voice = audio_gen._get_edge_voice_name()
        if 'pt-BR' in voice:
            print(f"   ✅ Voz Edge TTS: {voice}")
            return True
        else:
            print(f"   ⚠️  Voz: {voice}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        return False

def test_full_flow():
    """Testa fluxo completo com um livro"""
    print("\n5️⃣ Testando fluxo completo...")
    
    try:
        from text.bible_text_generator import BibleTextGenerator
        
        gen = BibleTextGenerator('pt')
        
        # Verificar se Jonas está disponível em português
        books = gen.get_available_books()
        if 'jonah' in books:
            # Tentar obter texto
            text = gen.get_chapter_text('Jonah', 1)
            if text:
                # Verificar se está em português
                portuguese_words = ['jonas', 'senhor', 'disse', 'palavra']
                text_lower = text.lower()
                found = any(word in text_lower for word in portuguese_words)
                
                if found:
                    print(f"   ✅ Texto de Jonas em português!")
                    print(f"   📖 Amostra: {text[:80]}...")
                    return True
                else:
                    print(f"   ⚠️  Texto parece estar em inglês")
                    print(f"   💡 Baixe Jonas em PT: python bible_data/download_portuguese_bible_v2.py jonah")
                    return False
            else:
                print(f"   ⚠️  Não conseguiu obter texto")
                return False
        else:
            print(f"   ⚠️  Jonas não disponível")
            print(f"   💡 Baixe Jonas: python bible_data/download_portuguese_bible_v2.py jonah")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar todos os testes"""
    print("=" * 70)
    print("🔍 VALIDADOR DO SISTEMA EM PORTUGUÊS")
    print("=" * 70)
    
    results = []
    
    results.append(("Configuração", check_config()))
    results.append(("Livros em português", check_portuguese_books()))
    results.append(("Gerador de texto", check_text_generator()))
    results.append(("Gerador de áudio", check_audio_generator()))
    results.append(("Fluxo completo", test_full_flow()))
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO DA VALIDAÇÃO")
    print("=" * 70)
    
    all_pass = True
    for name, passed in results:
        status = "✅ OK" if passed else "⚠️  Atenção"
        print(f"{name:30s} {status}")
        if not passed:
            all_pass = False
    
    print("=" * 70)
    
    if all_pass:
        print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        print("\nVocê pode gerar vídeos em português:")
        print("   python run.py")
    else:
        print("\n⚠️  ALGUNS ITENS PRECISAM DE ATENÇÃO")
        print("\nSiga as sugestões acima (💡) para resolver.")
    
    print("\nPara mais ajuda:")
    print("   • python manage_bible_books.py (gerenciar livros)")
    print("   • Consulte: SOLUCAO_PORTUGUES.md")
    print("=" * 70)

if __name__ == "__main__":
    main()


