# HUMANJUDGE
## 安装依赖
pip install Flask tqdm

## 配置路径
打开 app.py 文件，仔细修改顶部的3个配置项：SOURCE_JSON_PATH, IMAGE_DIRECTORY_ROOT, 和 DATABASE_PATH。

## 在Windows上用 
set FLASK_APP=app.py
## 在Mac/Linux上用 
export FLASK_APP=app.py


## 先初始化数据库表
flask init-db
## 再导入数据
flask import-data

## 然后直接运行
flask run --port=5001