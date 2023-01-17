# TranslatorUtil

苦于英语不佳，对现成工具不满意（特殊情况下复制文本后拼接困难），故自己简单造了个小轮子。
一个翻译源感觉够用了，加翻译源再说吧...

翻译逆向参考：`https://github.com/ybsdegit/JS_reverse_translate`



2023年1月16日更新 去huggingface找了一个翻译模型，辅助翻译还是够用的

2023年1月17日新增PdfToPdfWithoutImg来处理pdf，暂时未见cid的情况，使用方法参考main.py（参考项目[EasyTrans](https://github.com/QPromise/EasyTrans)的处理方法）



## 使用方法

python>=3.6

```shell
pip install -r requirements.txt
```

具体使用方法参考main.py中说明

```python
if __name__ == '__main__':
    baiduTranslate = BaiduTranslateJS() 
#    baiduTranslate = BaiduSelenium()
    translaExe = Translator(baiduTranslate)

    mdGenerated = MdFileGenerater(r"文件夹路径")  # 根据传入的dirpath路径，检索文件夹下的pdf生成标题带链接的md文档

    translaExe.translateEnToCnWithDirFromPDF(r"文件夹路径")  # 翻译文件，根据开头#或者空行进行分段，输出至同路径下一个带时间戳的md文档
```



### 使用huggingface模型

鉴于逆向的翻译api在翻译文本数量过多时容易触发风控，十分不稳定，我去[huggingface](https://huggingface.co/)找了一个[翻译模型](https://huggingface.co/Helsinki-NLP/opus-mt-en-zh)

环境基于windows 10

1、根据实际情况安装[pytorch](https://pytorch.org/get-started/locally/)

2、命令行运行`pip install -r requirements.txt`

3、运行`util/huggingface_hub_snapshot_download.py`文件下载模型数据到本地（这个方式下载快一些）。文件通常默认位于`"C:\Users\xxx\.cache\huggingface\hub\models--Helsinki-NLP--opus-mt-en-zh\snapshots\***"`下

4、将上述路径填写至`myModelPath`变量即可。或者移动至目标路径后填写至`myModelPath`变量，或者也可以采取软链接的方式。



#### 软链接方法

```powershell
# 管理员模式打开cmd，输入下面命令。“\d”指生成的是文件夹的软链接
mklink /d "需要生成的软链接绝对路径" "C:\Users\xxx\.cache\huggingface\hub\models--Helsinki-NLP--opus-mt-en-zh\snapshots\4fb87f7104ee945399ea39e145fcbb957981b50a"
```



### 示例

```python
if __name__ == '__main__':
    myModelPath = os.path.join(opusDirName, "opus_mt_en_zh") # 模型数据路径，自行修改
    opusMtTranslate = OpusMtEn2Zh(myModelPath)

    pdfToTxt = PDFToTxt()
    translaExe = Translator(opusMtTranslate, pdf2Txt=pdfToTxt, limitWordNum=512) # 模型自带长度限制512

    dirPath = r"文件夹路径"
    mdGenerated = MdFileGenerater(dirPath)
    # translaExe.translateEnToCnWithFile(mdGenerated)
    translaExe.translateEnToCnWithDirFromPDF(dirPath)
    
    pdfToPdf = PdfToPdfWithoutImg(opusMtTranslate)
    pdfToPdf.transferPdfWithDir(dirPath)
```

