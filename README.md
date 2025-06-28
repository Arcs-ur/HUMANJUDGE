# HUMANJUDGE
## 安装依赖
```bash
pip install Flask tqdm
```
## 配置路径
打开 app.py 文件，仔细修改顶部的3个配置项：SOURCE_JSON_PATH, IMAGE_DIRECTORY_ROOT, 和 DATABASE_PATH。

## 在Windows上用 
```bash
set FLASK_APP=app.py
```
## 在Mac/Linux上用 
```bash
export FLASK_APP=app.py
```

## 先初始化数据库表
```bash
flask init-db
```
## 再导入数据
```bash
flask import-data
```
## 然后直接运行
```bash
flask run --port=5001
```