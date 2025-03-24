"""
text_splitter.py – Módulo Avanzado para División de Textos en el Sistema RAG

Este módulo ofrece estrategias "state-of-the-art" para dividir textos extensos en "chunks"
que puedan ser procesados por los generadores de embeddings y LLMs sin sobrepasar límites
de tokens o causar problemas de contexto. Algunos aspectos destacados:

- Estrategias de división configurables: por longitud de caracteres, por separador (e.g. párrafos),
  o por tokens (usando un contador heurístico).
- Overlap opcional entre chunks, para mantener contexto entre segmentos.
- Posibilidad de normalizaciones (por ej. recortar espacios, remover saltos de línea innecesarios).
- Mecanismos que permiten integración con utils/validation.py si se desea filtrar chunks irrelevantes.
- Manejo de excepciones y logging detallado, con un "estado" inmutable (no hay variables globales).
  
Ideal para integrarse con pipelines de embeddings, a fin de trocear documentos grandes y
pasar cada chunk a la capa de embeddings.
"""

import logging
from typing import List, Optional, Callable

from utils.logger import logger

DEFAULT_MAX_CHARS = 1000
DEFAULT_OVERLAP = 50
DEFAULT_SEPARATOR = "\n\n"


class TextSplitter:
    def __init__(
        self,
        chunk_size: int = DEFAULT_MAX_CHARS,
        overlap: int = DEFAULT_OVERLAP,
        strategy: str = "by_chars",
        separator: Optional[str] = None,
        custom_token_counter: Optional[Callable[[str], int]] = None
    ):
        """
        Constructor para un divisor de textos avanzado.

        Args:
            chunk_size (int): Tamaño máximo de cada chunk. Depende de la estrategia.
            overlap (int): Número de caracteres (o tokens) que se superponen entre chunks consecutivos.
            strategy (str): Estrategia de división. Puede ser:
                - "by_chars": por longitud de caracteres.
                - "by_separator": dividir por un separador (separator).
                - "by_tokens": si custom_token_counter está definido, se mide el chunk_size en tokens.
            separator (str, opcional): Cadena usada para dividir si strategy="by_separator".
            custom_token_counter (Callable, opcional): Función que dado un texto, retorna la cantidad de tokens
                estimados. Solo requerido si strategy="by_tokens".  
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.strategy = strategy
        self.separator = separator or DEFAULT_SEPARATOR
        self.custom_token_counter = custom_token_counter

        if overlap >= chunk_size:
            logger.warning("El overlap es mayor o igual al chunk_size; puede generar chunks redundantes excesivos.")

        if strategy == "by_tokens" and not custom_token_counter:
            msg = "Se requiere una función custom_token_counter si strategy='by_tokens'."
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"TextSplitter inicializado con strategy={strategy}, chunk_size={chunk_size}, overlap={overlap}")

    def split_text(self, text: str) -> List[str]:
        """
        Divide un texto según la estrategia configurada. Retorna una lista de chunks.

        Args:
            text (str): El texto completo a dividir.

        Returns:
            list[str]: Lista de trozos de texto (chunks).
        """
        text = text.strip()
        if not text:
            logger.warning("Texto vacío o en blanco pasado a split_text.")
            return []

        if self.strategy == "by_chars":
            return self._split_by_chars(text)
        elif self.strategy == "by_separator":
            return self._split_by_separator(text)
        elif self.strategy == "by_tokens":
            return self._split_by_tokens(text)
        else:
            msg = f"Estrategia de división desconocida: {self.strategy}"
            logger.error(msg)
            raise ValueError(msg)

    def _split_by_chars(self, text: str) -> List[str]:
        """
        Estrategia: dividir por longitud de caracteres, con solapamiento si self.overlap > 0.
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.overlap  # retrocede 'overlap' para crear un solapamiento
            if start < 0:
                start = 0  # por seguridad

        return chunks

    def _split_by_separator(self, text: str) -> List[str]:
        """
        Estrategia: dividir por un separador, luego reagrupar chunks para no exceder self.chunk_size.
        Se asume un chunk_size en chars.
        """
        # Dividimos por el separador
        parts = text.split(self.separator)
        chunks = []
        current_chunk = ""

        for part in parts:
            if not current_chunk:
                current_chunk = part
            elif len(current_chunk) + len(self.separator) + len(part) <= self.chunk_size:
                current_chunk += self.separator + part
            else:
                # Agregar el chunk a la lista
                chunks.append(current_chunk)
                # Solapamiento: permitir que parte del chunk anterior se sume al siguiente
                overlap_str = ""
                if self.overlap > 0:
                    # Tomar self.overlap chars del final
                    tail = current_chunk[-self.overlap:]
                    overlap_str = tail

                current_chunk = overlap_str + part

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _split_by_tokens(self, text: str) -> List[str]:
        """
        Estrategia: usar la función custom_token_counter para medir tokens, con chunk_size en tokens.
        """
        chunks = []
        tokens_list = self._tokenize_text(text)
        total_tokens = len(tokens_list)
        start = 0

        while start < total_tokens:
            end = min(start + self.chunk_size, total_tokens)
            chunk_tokens = tokens_list[start:end]
            chunk_text = self._detokenize_text(chunk_tokens)
            chunks.append(chunk_text)
            # overlap en tokens
            start = end - self.overlap if (end - self.overlap) >= 0 else end

        return chunks

    def _tokenize_text(self, text: str) -> List[str]:
        """
        Transforma el texto en una lista de "tokens" (usando la función custom_token_counter o un fallback).
        Realmente, custom_token_counter() retorna la cantidad, no la lista de tokens, así que
        necesitamos un método heurístico si queremos la lista.
        """
        # En un caso real, se podría usar una librería de NLP (ej. NLTK, regex, etc.)
        # si custom_token_counter no provee la lista. Por ejemplo:
        #   tokens = re.findall(r"\S+|\n", text)
        # y luego para contarlos, se llama a custom_token_counter. 
        # Pero, “by_tokens” a menudo significa que chunk_size es en tokens. 
        # Asumamos una heurística simple: cada palabra + saltos de línea es un token.

        import re
        tokens = re.findall(r"\S+|\n", text)
        return tokens

    def _detokenize_text(self, tokens: List[str]) -> str:
        """
        Combina la lista de tokens en un string. 
        Estrategia muy simplificada, puede ajustarse con más lógica.
        """
        return " ".join(tokens)
