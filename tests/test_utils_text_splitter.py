"""
test_utils_text_splitter.py – Pruebas para el módulo text_splitter.py

Cubrimos:
  1. Estrategias "by_chars", "by_separator", "by_tokens".
  2. Verificación de overlap.
  3. Casos de texto vacío.
  4. Manejo de excepciones y logs.
"""

import pytest
from utils.text_splitter import TextSplitter

def test_by_chars_basic():
    splitter = TextSplitter(chunk_size=5, overlap=0, strategy="by_chars")
    text = "abcdefghijk"
    chunks = splitter.split_text(text)
    # 5 chars + 5 chars + 1 char => 3 chunks
    assert chunks == ["abcde", "fghij", "k"]

def test_by_chars_with_overlap():
    splitter = TextSplitter(chunk_size=5, overlap=2, strategy="by_chars")
    text = "abcdefghij"
    chunks = splitter.split_text(text)
    # primer chunk: abcde
    # segundo chunk: cdefg (empieza en pos 3 -> indices: 2..6)
    # tercero chunk: efghi
    # cuarto chunk: ghi (pos 6..10) => "ij"? Revisamos concretamente
    # En pos 0..5 => 'abcde'
    #   next start=5-2=3 -> pos 3..8 => 'defgh'
    #   next start=8-2=6 -> pos 6..11 => 'ghij' (aunque string length=10 => 'ghij' son 4 chars)
    #   next start=10-2=8 => 8..13 => 'ij' 
    # Revisar que se cree 4 chunks
    assert len(chunks) == 4
    assert chunks[0] == "abcde"
    assert chunks[1] == "defgh"  # f->pos4 => chunk 3..8 => 'defgh'
    assert chunks[2] == "ghij"
    assert chunks[3] == "ij"

def test_by_separator():
    text = "Line1\n\nLine2\n\nLine3 large large line"
    # Separador = "\n\n" (defecto)
    # chunk_size=15, overlap=3
    splitter = TextSplitter(chunk_size=15, overlap=3, strategy="by_separator")
    chunks = splitter.split_text(text)
    # parted => ["Line1", "Line2", "Line3 large large line"]
    # Reagrupado => cada chunk no excede 15 chars
    #  "Line1" => len=5 => se mete en chunk1
    #  Agregar "\n\n" + "Line2" => (5+2+5=12) => OK, sigue <15 => "Line1\n\nLine2" (len=12)
    #  Next => sumamos "\n\n" + "Line3 large large line" => 12+2+21=35 => se excede => chunk1 se cierra.
    #   chunk1 => "Line1\n\nLine2"
    #   Overlap => 3 chars del final => 'ine2' ? => actually last 3 => 'e2'
    #   chunk2 => "e2Line3 large large line"? => ver la concatenación real 
    # El test confirmará la segmentación final.
    assert len(chunks) == 2
    # Verificar algo puntual
    assert "Line1\n\nLine2" in chunks[0]
    assert "Line3 large" in chunks[1]

def test_by_tokens_no_counter():
    # Falta custom_token_counter => ValueError
    with pytest.raises(ValueError, match="Se requiere una función custom_token_counter"):
        TextSplitter(strategy="by_tokens")

def dummy_token_counter(_):
    # Solo un placeholder, no se llama en esta implementación porque
    # en el split actual no reenviamos la sum a custom_token_counter.
    return 10

def test_by_tokens_basic():
    # chunk_size=3 => tres tokens x chunk, overlap=1 => 1 token se solapa
    # El splitter internamente hace un parse heurístico
    splitter = TextSplitter(chunk_size=3, overlap=1, strategy="by_tokens", custom_token_counter=dummy_token_counter)
    text = "uno dos tres cuatro cinco seis"
    chunks = splitter.split_text(text)
    # Tokens heurísticos => ["uno","dos","tres","cuatro","cinco","seis"]
    # chunk1 => tokens[0..3] => ["uno","dos","tres"]
    # chunk2 => tokens[2..5] => ["tres","cuatro","cinco"]
    # chunk3 => tokens[4..7] => ["cinco","seis"] (aquí no hay token7)
    # => 3 chunks
    assert len(chunks) == 3
    assert "uno" in chunks[0] and "tres" in chunks[0]
    assert "tres" in chunks[1] and "cuatro" in chunks[1]
    assert "cinco" in chunks[1] and "cinco" in chunks[2]

def test_empty_text():
    splitter = TextSplitter()
    chunks = splitter.split_text("")
    assert chunks == []

def test_unknown_strategy():
    with pytest.raises(ValueError, match="Estrategia de división desconocida"):
        TextSplitter(strategy="inexistente").split_text("texto")
