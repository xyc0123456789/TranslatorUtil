import abc
import re
from typing import List


class BaseTranslator(metaclass=abc.ABCMeta):

    def __init__(self, max_length=512):
        self.max_length = max_length

    @abc.abstractmethod
    def normalTranslate(self, query: str) -> str:
        pass

    def translate(self, query: str) -> str:
        query = re.sub('(?P<pre>[a-zA-z]+)(- )(?P<aft>[a-zA-z]+)', '\g<pre>\g<aft>', query)
        toTranslate = splitQuery(query, self.max_length)
        ans = ""
        for i in toTranslate:
            ans += self.normalTranslate(i)
        return ans


def splitQuery(query: str, length: int, splitChar='.') -> List[str]:
    """
    按指定大小切分字符串,因为翻译接口有字符长度限制，这里做字符切分
    @param query 需要分割的字符串
    @param splitChar 分句的依据
    @param length 限制单句长度
    """
    if len(query) <= length:
        return [query]
    t = query.rfind(splitChar, 0, length)
    if t == -1:
        if splitChar == ".":
            return splitQuery(query, length, " ")
        else:
            totalLen = len(query)
            res = []
            maxSplit = int(totalLen / length)
            for i in range(maxSplit):
                res.append(query[i * length:(i + 1) * length])
            if maxSplit * length < totalLen:
                res.append(query[maxSplit * length:])
            return res

    currentStr = query[:t + 1]
    if t + 1 < len(query):
        nextStrList = splitQuery(query[t + 1:], length)
        return [currentStr] + nextStrList
    else:
        return [currentStr]


def writeToFileForTranslate(filePath, oriStrList: List[str], translateStrList: List[str], append=True):
    assert len(oriStrList) == len(translateStrList), "翻译存在遗漏"
    if len(oriStrList) == 0:
        return
    mod = "w"
    if append:
        mod = "a"
    with open(filePath, mod, encoding='utf-8') as f:
        for i in range(len(oriStrList)):
            f.write(oriStrList[i])
            f.write("\n\n")
            f.write(translateStrList[i])
            f.write("\n\n\n\n")
            f.flush()
