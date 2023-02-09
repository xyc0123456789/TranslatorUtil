# -*- coding: utf-8 -*-
from abc import ABC

from util.BaseTranslator import BaseTranslator


class DoNothingTranslator(BaseTranslator, ABC):

    def __init__(self, max_length=512):
        super().__init__(max_length=max_length)

    def normalTranslate(self, query: str) -> str:
        return query