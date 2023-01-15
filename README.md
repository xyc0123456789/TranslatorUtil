# TranslatorUtil

苦于英语不佳，对现成工具不满意（特殊情况下复制文本后拼接困难），故自己简单造了个小轮子。
一个翻译源感觉够用了，加翻译源再说吧...

翻译逆向参考：`https://github.com/ybsdegit/JS_reverse_translate`

## 使用方法

python>=3.6

```shell
pip install -r requirements.txt
```

具体方法参考main.py

```python
if __name__ == '__main__':
    baiduTranslate = BaiduTranslateJS() # 翻译量短时间过大会被风控，需要进一步的逆向...此时建议使用selenium方法，速度会慢了不少
#    baiduTranslate = BaiduSelenium()
    translaExe = Translator(baiduTranslate)

    mdGenerated = MdFileGenerater(r"文件夹路径")  # 根据传入的dirpath路径，检索文件夹下的pdf生成标题带链接的md文档

    translaExe.translateEnToCnWithFile(mdGenerated)  # 翻译文件，根据开头#或者空行进行分段，输出至同路径下一个带时间戳的md文档
```

