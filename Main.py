import logging
import os.path
import re
import time
from typing import List, Tuple

from tqdm import tqdm

from model.OpusMtEn2Zh import OpusMtEn2Zh, opusDirName
from util.BaseTranslator import splitQuery, writeToFileForTranslate
from util.PDF2Txt import PDFToTxt, transCidToChar
from util.PdfToPdfWithoutImg import PdfToPdfWithoutImg

# 不打印pdfminer的各种warining信息
logging.propagate = False
logging.getLogger().setLevel(logging.ERROR)
projectRoot = os.path.dirname(__file__)


class Translator:

    def __init__(self, translateExe, pdf2Txt=None, limitWordNum=5000):
        """
        @param translateExe: 翻译类，需要实现特定方法def translate(query: str) -> str
        @param limitWordNum: 翻译时字符长度限制
        """
        self.limitWordNum = limitWordNum
        self.translateExe = translateExe
        self.pdf2Txt = pdf2Txt

    def translateLines(self, toTranslate: List[str], timeSleep=0.0) -> Tuple[List[str], List[str]]:
        """
        逐行文本翻译，并进行标题提取
        :param timeSleep:
        :param toTranslate:
        :return:
        """
        translateStrList = []

        for strToTranslate in tqdm(toTranslate):
            # strToTranslate = transCidToChar(i)  # cid to char

            if strToTranslate.startswith("#") and strToTranslate.find("[") != -1 and strToTranslate.endswith(")"):  # 标题提取
                translateStr = self.translateEnToCnWithStr(strToTranslate[strToTranslate.find("[") + 1:strToTranslate.find("]")])
            else:
                translateStr = self.translateEnToCnWithStr(strToTranslate)
            translateStrList.append(translateStr)
            # time.sleep(timeSleep)

        return toTranslate, translateStrList

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
        toTranslate, translateStrList = self.translateLines(toTranslate)
        print("translate " + filePath + " finished")
        writeToFileForTranslate(targetFilePath, oriStrList=toTranslate, translateStrList=translateStrList)
        print("write to " + targetFilePath + " finished")

    def translateEnToCnWithDirFromPDF(self, dirTltPath: str, targetFile="", pdfReadAgain=False, timeSleep=0.0) -> None:
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
            toTranslate, translateStrList = self.translateLines(toTranslate, timeSleep)
            print("《" + pdfName + "》 translate finished")
            titleToAppend = "# [" + pdfName + "](file:///" + os.path.join(dirTltPath, currentPdf) + ")\n\n\n\n"
            writeToFile(targetFile, titleToAppend)
            writeToFileForTranslate(targetFile, oriStrList=toTranslate, translateStrList=translateStrList)
            print("《" + pdfName + "》 write finished")


def readAndDealFile(filePath: str) -> List[str]:
    """#开头的作为标题处理，其他的中间有空行的不合并，没空行的，直接合并为一行，处理(cid:)"""
    ans = []
    with open(filePath, "r", encoding='utf-8') as f:
        lines = f.readlines()
    tmp = ''
    for row in lines:
        row = row.strip()
        row = transCidToChar(row)  # 处理(cid:)
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
            if subFiles.startswith("Z_"):
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
    opusMtTranslate = OpusMtEn2Zh(myModelPath, max_length=512)
    pdfToPdf = PdfToPdfWithoutImg(opusMtTranslate)

    dirPath = r"文件夹路径"
    mdGenerated = MdFileGenerater(dirPath)
    pdfToPdf.transferPdfWithDir(dirPath)
