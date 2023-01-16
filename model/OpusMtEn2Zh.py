# https://huggingface.co/Helsinki-NLP/opus-mt-en-zh
import os

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TranslationPipeline

opusDirName = os.path.dirname(__file__)


class OpusMtEn2Zh:
    def __init__(self, modelPath):
        self.tokenizer = AutoTokenizer.from_pretrained(modelPath)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(modelPath)
        if torch.cuda.is_available():
            self.translatePipeLine = TranslationPipeline(self.model, self.tokenizer, device=0)
        else:
            self.translatePipeLine = TranslationPipeline(self.model, self.tokenizer)
        self.model.eval()

    def translate(self, query):
        res = self.translatePipeLine(query)
        if len(res) > 1:
            pass
        elif len(res) == 0:
            return ""
        return res[0]["translation_text"]


if __name__ == '__main__':
    myModelPath = os.path.join(opusDirName, "opus_mt_en_zh")
    op = OpusMtEn2Zh(myModelPath)
    print(op.translate("My name is Wolfgang and I live in Berlin"))
