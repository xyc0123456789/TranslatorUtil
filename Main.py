import logging
import os.path
import re
import time
from typing import List

from tqdm import tqdm

from model.OpusMtEn2Zh import OpusMtEn2Zh, opusDirName
from util.PDF2Txt import PDFToTxt

# 不打印pdfminer的各种warining信息
logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)


class Translator:

    def __init__(self, translateExe, pdf2Txt=None, limitWordNum=5000):
        """
        @param translateExe: 翻译类，需要实现特定方法def translate(query: str) -> str
        @param limitWordNum: 翻译时字符长度限制
        """
        self.limitWordNum = limitWordNum
        self.translateExe = translateExe
        self.pdf2Txt = pdf2Txt

    def translateLines(self, toTranslate: List[str], timeSleep=0.0) -> List[str]:
        """
        逐行文本翻译，并进行标题提取
        :param timeSleep:
        :param toTranslate:
        :return:
        """
        translateStrList = []
        for i in tqdm(toTranslate):
            if i.startswith("#") and i.find("[") != -1 and i.endswith(")"):  # 标题提取
                translateStr = self.translateEnToCnWithStr(i[i.find("[") + 1:i.find("]")])
            else:
                translateStr = self.translateEnToCnWithStr(i)
            translateStrList.append(translateStr)
            time.sleep(timeSleep)
        return translateStrList

    def translateEnToCnWithStr(self, query: str) -> str:
        """文本翻译"""
        query = re.sub(r'[^\x00-\x7F]+', '&', query)  # 替换非ascii字符为&
        queryStrList = splitQuery(query, self.limitWordNum)
        ans = ""
        for i in queryStrList:
            if len(i.strip()) == 0:
                continue
            tmp = self.translateExe.translate(i)
            ans += tmp
        return ans

    def translateEnToCnWithFile(self, filePath: str) -> None:
        """翻译文件，根据# 或者空行进行分段"""
        assert os.path.exists(filePath), filePath + " not exists"
        index = filePath.rfind(".")
        curtime = time.strftime("_%Y%m%d_%H%M%S", time.localtime())
        targetFilePath = filePath[:index] + curtime + filePath[index:]
        toTranslate = readAndDealFile(filePath)
        print("read " + filePath + " finished")
        translateStrList = self.translateLines(toTranslate)
        print("translate " + filePath + " finished")
        writeToFileForTranslate(targetFilePath, oriStrList=toTranslate, translateStrList=translateStrList)
        print("write to " + targetFilePath + " finished")

    def translateEnToCnWithDirFromPDF(self, dirTltPath: str, targetFile="", pdfReadAgain=False, timeSleep=0.5) -> None:
        """
        将dirPath文件夹下所有PDF翻译为中文，并写入targetFile（默认名称为文件夹名称_total.md）中，不同文件之间将以分割线
        :param timeSleep:
        :param pdfReadAgain:
        :param targetFile: 目标文件
        :param dirTltPath:查找pdf的路径
        :return:
        """
        assert self.pdf2Txt is not None, "pdf2Txt is None"
        assert os.path.exists(dirTltPath), dirTltPath + " not exists"
        if targetFile == "" or targetFile is None:
            targetFile = os.path.join(dirTltPath, os.path.basename(dirTltPath) + "_total.md")
        txtPathList = self.pdf2Txt.pdf2txtWithDir(dirTltPath, pdfReadAgain=pdfReadAgain)
        print(txtPathList)
        for txtPath in txtPathList:
            pdfName = txtPath[txtPath.rfind(os.path.sep) + 1:-4]
            currentPdf = pdfName + ".pdf"
            toTranslate = readAndDealFile(txtPath)
            print("《" + pdfName + "》  read finished, translate started")
            translateStrList = self.translateLines(toTranslate, timeSleep)
            print("《" + pdfName + "》 translate finished")
            titleToAppend = "# [" + pdfName + "](file:///" + os.path.join(dirTltPath, currentPdf) + ")\n\n\n\n"
            writeToFile(targetFile, titleToAppend)
            writeToFileForTranslate(targetFile, oriStrList=toTranslate, translateStrList=translateStrList)
            print("《" + pdfName + "》 write finished")


def readAndDealFile(filePath: str) -> List[str]:
    """#开头的作为标题处理，其他的中间有空行的不合并，没空行的，直接合并为一行"""
    ans = []
    with open(filePath, "r", encoding='utf-8') as f:
        lines = f.readlines()
    tmp = ''
    for row in lines:
        row = row.strip()
        if len(row) == 0 or row.startswith("#"):
            if len(tmp) > 0:
                ans.append(tmp)
                tmp = ''

        if row.startswith("#"):
            ans.append(row)
        elif len(row) > 0:
            if row.endswith("-"):
                tmp += row[:-1]  # -意味着连词
            else:
                tmp += row
                tmp += " "  # 默认换行加空格
    if len(tmp) > 0:
        ans.append(tmp)
    return ans


def writeToFile(filePath, toWriteStrOrList, append=True):
    mod = "w"
    if append:
        mod = "a"
    with open(filePath, mod, encoding='utf-8') as f:
        if isinstance(toWriteStrOrList, str):
            f.write(toWriteStrOrList)
            f.flush()
        else:
            for i in range(toWriteStrOrList):
                f.write(toWriteStrOrList)
                f.write("\n")
                f.flush()


def writeToFileForTranslate(filePath, oriStrList: List[str], translateStrList: List[str], append=True):
    assert len(oriStrList) == len(translateStrList), "翻译存在遗漏"
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


def splitQuery(query: str, length: int, splitChar='.') -> List[str]:
    """按指定大小切分字符串,因为翻译接口有字符长度限制，这里做字符切分
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
                res.append(query[i*length:(i+1)*length])
            if maxSplit * length < totalLen:
                res.append(query[maxSplit * length:])
            return res

    currentStr = query[:t + 1]
    if t + 1 < len(query):
        nextStrList = splitQuery(query[t + 1:], length)
        return [currentStr] + nextStrList
    else:
        return [currentStr]


def MdFileGenerater(dirMdPath: str) -> str:
    """根据dirMdPath路径的文件夹下的pdf生成标题带链接的md文档"""
    assert os.path.exists(dirMdPath), "文件夹不存在"
    fileList = os.listdir(dirMdPath)
    targetfile = os.path.join(dirMdPath, os.path.basename(dirMdPath) + ".md")
    if os.path.exists(targetfile):
        print(targetfile + " is exists")
        return targetfile
    with open(targetfile, "a", encoding="utf-8") as f:
        for subFiles in fileList:
            if not subFiles.endswith(".pdf"):
                continue
            currentPdf = os.path.join(dirMdPath, subFiles)
            f.write("# [" + subFiles[:-4] + "](file:///" + currentPdf + ")\n\n\n\n\n\n\n\n")
            f.flush()
    return targetfile


'''
1、读取md
2、#开头的作为标题处理，其他的中间有空行的不合并，没空行的，直接合并为一行
3、重新写进一个新文件，格式为标题 标题翻译 段落 段落翻译
'''

if __name__ == '__main__':
    myModelPath = os.path.join(opusDirName, "opus_mt_en_zh")
    opusMtTranslate = OpusMtEn2Zh(myModelPath)

    pdfToTxt = PDFToTxt()
    translaExe = Translator(opusMtTranslate, pdf2Txt=pdfToTxt, limitWordNum=512)

    dirPath = r""
    mdGenerated = MdFileGenerater(dirPath)
    translaExe.translateEnToCnWithDirFromPDF(dirPath)

    # filePath = r""
    # translaExe.translateEnToCnWithFile(filePath)