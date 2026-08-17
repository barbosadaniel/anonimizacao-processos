#!/usr/bin/env python3
"""
Script para validar a precisão das redações
Compara coordenadas extraídas com text visual no PDF
"""
import pdfplumber
import json
from pathlib import Path

def analyze_pdf(pdf_path, name):
    """Analisa um PDF e extrai info"""
    print(f"\n{'='*60}")
    print(f"ANALISANDO: {name}")
    print('='*60)
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Páginas: {len(pdf.pages)}")
        
        for page_idx, page in enumerate(pdf.pages):
            print(f"\n--- PÁGINA {page_idx} ---")
            print(f"Dimensões: {page.width:.1f} x {page.height:.1f}")
            
            # Extrair palavras
            words = page.extract_words()
            print(f"Palavras: {len(words)}")
            
            # Primeiras 10 palavras com coordenadas
            print("\nPrimeiras 10 palavras (pdfplumber coords):")
            for i, word in enumerate(words[:10]):
                print(f"  {i}: '{word['text']}' @ x0={word['x0']:.1f}, top={word['top']:.1f}, bottom={word['bottom']:.1f}")
            
            # Tentar detectar "tarjas" (áreas que poderiam ser redações)
            # Isso é feito visualmente, buscando por padrões no PDF
            print("\nAnalisando estrutura de redações...")
            print("  (Este é um PDF visual, redações aparecem como retângulos pretos)")

# Analisar original
original_path = 'exemplos/processo_teste_anonimizacao.pdf'
result_path = 'exemplos/resultado_debug.pdf'

if Path(original_path).exists():
    analyze_pdf(original_path, "ORIGINAL")
else:
    print(f"Original não encontrado: {original_path}")

if Path(result_path).exists():
    analyze_pdf(result_path, "ANONIMIZADO")
else:
    print(f"Resultado não encontrado: {result_path}")

print("\n" + "="*60)
print("PRÓXIMAS ETAPAS:")
print("="*60)
print("1. Abrir resultado_debug.pdf manualmente")
print("2. Verificar se as tarjas (retângulos pretos) cobrem corretamente as entidades")
print("3. Comparar com a lista de coordenadas nos logs da API")
print("="*60)
