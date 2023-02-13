# -*- encoding: utf-8 -*-

'''
@Author  :  leoqin

@Contact :  qcs@stu.ouc.edu.cn

@Software:  Pycharm

@Time    :  May 29,2019

@Desc    :  pdf必应翻译，将要翻译的pdf放到input_file目录下，然后记得改39行path最后的pdf名字

pymupdf api 名称参考 https://pymupdf.readthedocs.io/en/latest/znames.html#deprecated-names

'''
import shutil
import os
import re
import time
import traceback

import fitz
import numpy as np

from model.DoNothingTranslator import DoNothingTranslator
from model.OpusMtEn2Zh import opusDirName, OpusMtEn2Zh
from util.BaseTranslator import BaseTranslator, writeToFileForTranslate


class PdfToPdfWithoutImg:
    def __init__(self, translator: BaseTranslator, frontFilePath=os.path.join(opusDirName, '../fonts/SimSun.ttf')):
        self.translator = translator
        self.frontFilePath = frontFilePath
        assert os.path.exists(self.frontFilePath), "fonts file not exists"

    def transferPdfWithDir(self, pdfDirPath, targetDirPath="", continueTransfer=True):
        assert os.path.exists(pdfDirPath), pdfDirPath + " not exists"
        renameFlag = False
        if targetDirPath is not None and targetDirPath != "":
            os.makedirs(targetDirPath, exist_ok=True)
            renameFlag = True

        hasTransfor = []
        if continueTransfer:
            for i in os.listdir(pdfDirPath):
                if i.startswith("Z_") and i.endswith(".pdf"):
                    hasTransfor.append(i[2:-20] + ".pdf")
        costList = []
        pageSizeList = []
        for i in os.listdir(pdfDirPath):
            if not i.endswith(".pdf"):
                continue
            if continueTransfer and i in hasTransfor:
                print(i+" has been translated")
                continue
            t0 = time.time()
            if renameFlag:
                tFile = os.path.join(targetDirPath, i)
                tDir = os.path.join(targetDirPath, i[:-4])
                pageSize = self.transferPdf(os.path.join(pdfDirPath, i), targetPdfPath=tFile, tempDir=tDir)
            else:
                pageSize = self.transferPdf(os.path.join(pdfDirPath, i))
            t1 = time.time()
            costList.append(t1-t0)
            pageSizeList.append(pageSize)
            print(f"当前耗时:{int(t1-t0)}s, 翻译页数:{pageSize}, 每页平均耗时:{int((t1-t0) / pageSize)}s, 总耗时:{int(np.sum(costList))}s, 翻译总页数:{np.sum(pageSizeList)}, 每页平均耗时:{int(np.sum(costList)/np.sum(pageSizeList))}s")

    def transferPdf(self, pdfPath: str, targetPdfPath="", tempDir="", toTxt=True):
        """
        pdf转化
        :param toTxt: 默认true，将翻译追加至txt
        :param pdfPath: 需要翻译的pdf
        :param targetPdfPath: 目标pdf路径，否则默认添加后缀
        :param tempDir: 临时图片路径
        :return:
        """
        assert pdfPath.endswith(".pdf"), pdfPath + " is not pdf"

        file_name = os.path.basename(pdfPath)
        if file_name.startswith("Z_"):
            return
        pdfDir = os.path.dirname(pdfPath)
        if targetPdfPath == "" or targetPdfPath is None:
            curtime = time.strftime("_%Y%m%d_%H%M%S", time.localtime())
            targetPdfPath = os.path.join(pdfDir, "Z_" + file_name[:-4] + curtime + file_name[-4:])
        print(targetPdfPath)
        if tempDir == "" or tempDir is None:
            tempDir = os.path.join(pdfDir, file_name[:-4])
            os.makedirs(tempDir, exist_ok=True)

        print('当前翻译的pdf名字 ' + file_name + " 目标文件保存于: " + targetPdfPath)
        toTranslate = []
        translateStrList = []
        t0 = time.time()
        cur_pdf = fitz.open(pdfPath)  # 待翻译的pdf
        new_pdf = fitz.open()  # 翻译完成后要写入的pdf
        i = 0  # 定义页面数的递增
        try:
            imgcount = 0
            writeimgcount = 0
            reference_flag = 0  # 判断是否在参考文献之后
            imageDict = {}
            for cur_page in cur_pdf:
                print('正在翻译 {} 第{}页...'.format(file_name, i + 1))
                img_list = cur_page.get_images()  # 获取当前页面的图片对象

                for img in img_list:  # 获取当前页面的图像列表
                    pix_temp = cur_pdf.extract_image(img[0])
                    image_name = f"image{imgcount}.{pix_temp['ext']}"
                    with open(os.path.join(tempDir, image_name), "wb") as f:
                        f.write(pix_temp["image"])
                    imageDict[imgcount] = image_name
                    imgcount += 1
                blks = cur_page.get_text_blocks(flags=4)  # read text blocks of input page
                new_page = new_pdf.new_page(-1, width=cur_page.mediabox_size[0], height=cur_page.mediabox_size[1])  # 创建一个新的页面与之前的页面相同大小
                begin = (0, 0, 0, 0)  # 记录初始值
                end = (0, 0, 0, 0)  # 记录终结值
                flag = 0  # 记录当前的循
                blks.append((0, 0, 0, 0, "", 0))
                content = ""

                # fonts = 9
                for num in range(len(blks)):  # loop through the blocks
                    # 如果是本页面最后一个块,直接结束,因为最后一个是方便计算自己添加的。
                    if num == len(blks) - 1:
                        break
                    # 如果这个块里放的是图像.
                    if blks[num][-1] == 1:
                        # print('图像:::',blks[num][4])
                        img_r = blks[num][:4]  # 图片要放置位置的坐标
                        try:
                            path_img = os.path.join(tempDir, imageDict[writeimgcount])  # 当前页面第几个图片的位置
                            writeimgcount += 1
                            img = open(path_img, "rb").read()  # 输入流
                            new_page.insert_image(img_r, stream=img, keep_proportion=True)  # 输入到新的pdf页面对应位置
                            # os.remove(path_img)  # 输入到新的pdf之后就移除
                        except:
                            pass
                            # traceback.print_exc()
                        continue

                    # 设置默认字体大小以及位置
                    if i == 0:  # 当前是第一页的话
                        if num == 0 or num == 1:
                            fonts = 15
                            text_pos = fitz.TEXT_ALIGN_CENTER  # 一般论文前面的标题,作者,机构名等要居中
                        elif num == 2:
                            fonts = 10
                            text_pos = fitz.TEXT_ALIGN_CENTER  # 一般论文前面的标题,作者,机构名等要居中
                        elif num == 3:
                            fonts = 10
                            text_pos = fitz.TEXT_ALIGN_CENTER  # 一般论文前面的标题,作者,机构名等要居中
                        else:
                            fonts = 10
                            text_pos = fitz.TEXT_ALIGN_LEFT  # 设置文字在当前矩阵中的位置靠左排列
                    else:
                        fonts = 10
                        text_pos = fitz.TEXT_ALIGN_LEFT  # 设置文字在当前矩阵中的位置靠左排列
                    # 目的为了记录起始块坐标
                    if flag == 0:
                        begin = blks[num][:4]
                        content = blks[num][4].replace("\n", " ")
                    # 矩形块，b[0]b[1]为左上角的坐标，b[2]b[3]为右下角的坐标
                    r = fitz.Rect(blks[num][:4])
                    # 两个块y轴距离很近的话，这里以1.0为界，这里判断当前数的右下角的坐标y值
                    if (abs(blks[num + 1][1] - blks[num][3]) <= 1.0 and abs(
                            blks[num + 1][1] - blks[num][3]) >= 0):
                        # 当前块在参考文献之后
                        if reference_flag == 1:
                            trans_pragraph = blks[num][4].replace("\n", " ")
                            res = self.translator.translate(trans_pragraph).replace(' ', '')
                            new_page.insert_textbox(r, res, fontname="song", fontfile=self.frontFilePath,
                                                    fontsize=7, align=text_pos)  #
                        # 其它情况
                        else:
                            flag = 1  #
                            # 记录最后的矩形坐标，目的为了取出最后的右下角坐标点
                            end = blks[num + 1][:4]
                            if blks[num + 1][-1] != 1:  # 不是图片
                                content += blks[num + 1][4].replace("\n", " ")

                    # 两个块y轴距离远的的时候
                    else:
                        if flag == 1:  # 存在未处理的连续文本
                            res = self.translator.translate(content).replace(' ', '')  # 翻译结果去掉汉字中的空格
                            toTranslate.append(content)
                            translateStrList.append(res)
                            if begin[2] > end[2]:  # 如果起始点的右下角x坐标小于结束点的右下角x坐标
                                autoInsertTextBox(new_page, fitz.Rect(begin[0], begin[1], begin[2], end[3]), res, fontname="song",
                                                  fontfile=self.frontFilePath,
                                                  fontsize=fonts, align=text_pos)
                            else:
                                autoInsertTextBox(new_page, fitz.Rect(begin[0], begin[1], end[2], end[3]), res, fontname="song",
                                                  fontfile=self.frontFilePath,
                                                  fontsize=fonts, align=text_pos)
                            flag = 0
                        else:
                            trans_pragraph = blks[num][4].replace("\n", " ")  # 将待翻译的句子换行换成空格
                            if is_figure(trans_pragraph.replace(' ', '')):  # 将该块的判断是否是图片标注
                                res = self.translator.translate(trans_pragraph).replace(' ', '')  # 翻译结果去掉汉字中的空格
                                new_page.insert_textbox(r, res, fontname="song", fontfile=self.frontFilePath, fontsize=7,
                                                        align=fitz.TEXT_ALIGN_CENTER)
                            elif is_table(trans_pragraph):  # 将该块的判断是否是表格标注
                                res = self.translator.translate(trans_pragraph).replace(' ', '')  # 翻译结果去掉汉字中的空格
                                new_page.insert_textbox(r, res, fontname="song", fontfile=self.frontFilePath, fontsize=7,
                                                        align=fitz.TEXT_ALIGN_CENTER)
                            # 标记在这里之后的都是参考文献
                            elif is_reference(trans_pragraph.replace(' ', '')):
                                reference_flag = 1
                                new_page.insert_textbox(r, '参考文献', fontname="song", fontfile=self.frontFilePath, fontsize=fonts, align=text_pos)
                            elif is_image(trans_pragraph.replace(' ', '')):
                                pass
                            else:
                                # 翻译结果去掉汉字中的空格
                                res = self.translator.translate(trans_pragraph).replace(' ', '')
                                toTranslate.append(content)
                                translateStrList.append(res)
                                if reference_flag == 1:
                                    new_page.insert_textbox(r, res, fontname="song", fontfile=self.frontFilePath, fontsize=7, align=text_pos)
                                else:

                                    autoInsertTextBox(new_page, r, res, fontname="song", fontfile=self.frontFilePath, fontsize=fonts, align=text_pos)
                        # 记录起始矩形坐标
                        begin = blks[num + 1][:4]
                        try:
                            content = blks[num + 1][4].replace("\n", " ")
                        except:
                            pass
                i += 1
        except Exception as e:
            traceback.print_exc()
            print('翻译过程出现异常......')

        shutil.rmtree(tempDir)
        if toTxt:
            txtPath = targetPdfPath[:-4] + ".txt"
            writeToFileForTranslate(txtPath, toTranslate, translateStrList)

        # 文件保存
        if os.path.exists(targetPdfPath):
            try:
                os.remove(targetPdfPath)
            except:
                print('删除已有的文件失败，请先关闭该文件然后重新翻译！')
        new_pdf.save(targetPdfPath, garbage=4, deflate=True, clean=True)  # 保存翻译后的pdf
        t1 = time.time()
        print("Total translation time: %g sec" % (t1 - t0))
        return i

def is_reference(target):
    """正则匹配参考文献"""
    return re.match(r'references', target, re.I)


def is_figure(target):
    """正则匹配图片标注"""
    return re.match(r'fig.*?\.', target, re.I)


def is_table(target):
    return re.match(r'^table \d+.*', target, re.I)


def is_image(target):
    """正则匹配图片标注"""
    return re.match(r'<image.*?width.*?height.*?>', target, re.I)


def autoInsertTextBox(new_page, r, res, fontname="song", fontfile="", fontsize=12, align=fitz.TEXT_ALIGN_LEFT):
    while fontsize >= 0:
        textbox = new_page.insert_textbox(r, res, fontname=fontname, fontfile=fontfile, fontsize=fontsize, align=align)
        if textbox >= 0:
            break
        fontsize -= 1


if __name__ == '__main__':
    myModelPath = os.path.join(opusDirName, "opus_mt_en_zh")
    opusMtTranslate = OpusMtEn2Zh(myModelPath)

    # path = r"D:\CodeAndIDE\gitRepositories\EasyTrans\trans\input_file\test1.pdf"
    # pdfToPdf = PdfToPdfWithoutImg(opusMtTranslate)
    # pdfToPdf.transferPdf(path)
