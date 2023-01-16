from huggingface_hub import snapshot_download
snapshot_download(repo_id="Helsinki-NLP/opus-mt-en-zh", ignore_regex=["*.h5", "*.ot", "*.msgpack","*.tflite"])

# mklink /d "软链接路径" "C:\Users\xxx\.cache\huggingface\hub\models--Helsinki-NLP--opus-mt-en-zh\snapshots\4fb87f7104ee945399ea39e145fcbb957981b50a"