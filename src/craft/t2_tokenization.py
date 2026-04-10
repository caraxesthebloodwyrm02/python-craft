from __future__ import annotations

from dataclasses import dataclass

import nltk
import tiktoken
from tokenizers import Tokenizer


@dataclass
class TokenSummary:
    word_count: int
    bpe_count: int
    openai_count: int


def summarize_tokens(text: str, tokenizer_path: str, encoding_name: str = "cl100k_base") -> TokenSummary:
    words = nltk.word_tokenize(text)
    bpe = Tokenizer.from_file(tokenizer_path)
    bpe_ids = bpe.encode(text).ids
    enc = tiktoken.get_encoding(encoding_name)
    openai_ids = enc.encode(text)
    return TokenSummary(word_count=len(words), bpe_count=len(bpe_ids), openai_count=len(openai_ids))
