#!/usr/bin/env python3
"""
Script de teste para verificar a extração de texto de Philippians
"""

from text.bible_text_generator import BibleTextGenerator

# Criar gerador
gen = BibleTextGenerator(language='en')

# Testar extração do texto completo
print("=" * 80)
print("TESTE DE EXTRAÇÃO DE TEXTO - PHILIPPIANS")
print("=" * 80)
print()

text = gen.get_full_book_text('philippians')

print()
print("=" * 80)
print("RESULTADO:")
print(f"Total de caracteres: {len(text):,}")
print(f"Total de palavras (aprox): {len(text.split()):,}")
print()
print("Primeiros 300 caracteres:")
print(text[:300])
print()
print("..." * 20)
print()
print("Últimos 300 caracteres:")
print(text[-300:])
print()
print("=" * 80)

# Verificar se contém todos os capítulos
has_chapter_1 = "Paul and Timothy, servants" in text
has_chapter_2 = "Therefore if there is any" in text or "Let nothing be done" in text
has_chapter_3 = "Finally, my brothers" in text or "Beware of the dogs" in text
has_chapter_4 = "Therefore, my brothers, beloved and longed for" in text or "Rejoice in the Lord always" in text

print("VERIFICAÇÃO DE CAPÍTULOS:")
print(f"  Capítulo 1: {'✓ PRESENTE' if has_chapter_1 else '✗ AUSENTE'}")
print(f"  Capítulo 2: {'✓ PRESENTE' if has_chapter_2 else '✗ AUSENTE'}")
print(f"  Capítulo 3: {'✓ PRESENTE' if has_chapter_3 else '✗ AUSENTE'}")
print(f"  Capítulo 4: {'✓ PRESENTE' if has_chapter_4 else '✗ AUSENTE'}")
print()
print("=" * 80)

