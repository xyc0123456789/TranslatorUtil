import io
import os.path
from typing import List

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, process_pdf


class PDFToTxt:

    def __init__(self, caching=True):
        self.caching = caching
        self.rsrcmgr = PDFResourceManager(caching=self.caching)  # 创建一个PDF资源管理器对象来存储共赏资源

    def pdfTotxt(self, file, password="", targetFilePath="", rmNotNeed=True, pdfReadAgain=False):
        """
        pdf转txt
        :param pdfReadAgain: false:当文件存在且大小不为0时不再重新读取,true:会重新读取
        :param file: pdf文件
        :param password: pdf密码
        :param targetFilePath: 文本输出位置,默认同名txt
        :param rmNotNeed: true将 去除多余两行的空行， 拼接单字符行，去除references，acknowledgements，false：原样返回
        :return:
        """
        assert file.endswith(".pdf"), "文件后缀错误"
        if targetFilePath == '' or targetFilePath is None:
            targetFilePath = os.path.join(os.path.dirname(file), os.path.basename(file)[:-4] + ".txt")

        if not pdfReadAgain:
            if os.path.exists(targetFilePath) and os.path.getsize(targetFilePath) != 0:
                print(os.path.basename(targetFilePath) + " exists, pdftotxt skiped")
                return targetFilePath

        outfp = io.open(targetFilePath, 'wt', encoding="utf-8", errors='ignore')  # 指定outfile
        device = TextConverter(self.rsrcmgr, outfp, laparams=LAParams())
        fp = io.open(file, 'rb')  # 来创建一个pdf文档分析器
        try:
            process_pdf(self.rsrcmgr, device, fp, set(), maxpages=0, password=password, caching=self.caching, check_extractable=True)  # 调用process_pdf
        finally:
            fp.close()
            device.close()
            outfp.close()
        if rmNotNeed:
            return removeNotNeed(targetFilePath)
        return targetFilePath

    def pdf2txtWithDir(self, dirPath, rmNotNeed=True, pdfReadAgain=False) -> List[str]:
        """
        将文件加下所有PDF转为同名txt，
        :param rmNotNeed: true将 去除多余两行的空行， 拼接单字符行，去除references，acknowledgements，false：原样返回
        :param dirPath:
        :param pdfReadAgain: false:当文件存在且大小不为0时不再重新读取,true:会重新读取
        :return:
        """
        assert os.path.exists(dirPath), dirPath + " not exists"
        txtPathList = []
        for pdfName in os.listdir(dirPath):
            if not pdfName.endswith("pdf"):
                print(os.path.basename(pdfName) + " skiped for Not PDF!")
                continue
            currentPdf = os.path.join(dirPath, pdfName)
            txtPath = self.pdfTotxt(currentPdf, pdfReadAgain=pdfReadAgain, rmNotNeed=rmNotNeed)
            txtPathList.append(txtPath)
        return txtPathList


def removeNotNeed(oriFile, targetFilePath="", rmTitleHead=True):
    """
    去除多余两行的空行， 拼接单字符行，去除references，acknowledgements
    @:param rmTitleHead true：在开头#之前添加//
    """
    overWrited = targetFilePath == '' or targetFilePath is None
    with open(oriFile, "r", encoding="UTF-8") as f:
        lines = f.readlines()
        ans = []

        countSpace = 0  # 去除多余两行的空行

        # 拼接单字符行，去除references，acknowledgements
        singleFlag = False
        tmp = ""
        for row in lines:
            # 去除多余两行的空行
            if len(row) == 1 and row == "\n":
                countSpace = countSpace + 1
            else:
                countSpace = 0
            if countSpace > 2:
                continue

            # 拼接单字符行
            if len(row) == 2 and len(row.strip()) != 0:
                tmp += row.strip()
                singleFlag = True
                continue
            elif singleFlag:
                singleFlag = len(row.strip()) == 0
                if singleFlag:
                    continue
            else:
                singleFlag = False
                if len(tmp) > 0:
                    ans.append(tmp + "\n")
                    tmp = ""

            # 去除references，acknowledgements
            if len(row) < 20 and (row.strip().lower() == "references" or row.strip().lower() == "acknowledgements"):
                break

            if rmTitleHead and row[0] == "#":
                row = "//"+row
            ans.append(row)

    if overWrited:
        targetFilePath = oriFile
    with open(targetFilePath, "w", encoding="UTF-8") as of:
        for i in ans:
            of.write(i)
            of.flush()
    return targetFilePath


if __name__ == '__main__':
    pdf2text = PDFToTxt()

    fpath = r""
    targetFile = pdf2text.pdfTotxt(fpath)
    removeNotNeed(targetFile)
