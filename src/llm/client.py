from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

_MODEL_NAME = "google/flan-t5-base"

_tokenizer = None
_model = None


def get_llm():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)
        _model.eval()
    return _tokenizer, _model
