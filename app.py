import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, send_from_directory

# ==============================================================================
#                             【请在这里配置】
# ==============================================================================
# 1. 您的源JSON文件路径 (相对于此脚本)
SOURCE_JSON_PATH = 'data/benchmark_questions_1157_0627_detail.json'

# 2. 您存放所有图片的根目录的【绝对路径】或【相对路径】
#    例如: '/home/user/my_project/images' 或 '../images_folder'
IMAGE_DIRECTORY_ROOT = '/Users/arcsur/coding/zzs/smath/1200_own_images' 

# 3. 数据库文件路径
DATABASE_PATH = 'data/audit_database.db'
# ==============================================================================

app = Flask(__name__)
app.config['DATABASE'] = DATABASE_PATH
app.config['IMAGE_ROOT'] = os.path.abspath(IMAGE_DIRECTORY_ROOT)

# --- 数据库辅助函数 ---
def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """在请求结束后关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- 数据库初始化命令 ---
def init_db():
    """初始化数据库，创建表结构"""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('init-db')
def init_db_command():
    """Flask命令行接口：初始化数据库"""
    init_db()
    print('✅ 数据库已初始化。')

@app.cli.command('import-data')
def import_data_command():
    """Flask命令行接口：从JSON文件导入数据到数据库"""
    if not os.path.exists(SOURCE_JSON_PATH):
        print(f"❌ 错误：源JSON文件未找到于 '{SOURCE_JSON_PATH}'")
        return
        
    db = get_db()
    cursor = db.cursor()
    
    with open(SOURCE_JSON_PATH, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    imported_count = 0
    for record in records:
        # 检查记录是否已存在，避免重复导入
        cursor.execute("SELECT id FROM reviews WHERE image_path = ?", (record.get('path'),))
        if cursor.fetchone() is None:
            # 只有当记录包含DebateValidation时才导入
            if 'DebateValidation' in record:
                dv = record['DebateValidation']
                cursor.execute(
                    """
                    INSERT INTO reviews (image_path, question, gemini_answer, consensus_answer, debate_history)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        record.get('path'),
                        record.get('question'),
                        dv.get('gemini_answer'),
                        dv.get('consensus_answer'),
                        json.dumps(dv.get('debate_history'), ensure_ascii=False, indent=2)
                    )
                )
                imported_count += 1
    
    db.commit()
    print(f"✅ 数据导入完成，新增了 {imported_count} 条记录。")


# --- Web应用路由 ---
@app.route('/')
def index():
    """首页，自动重定向到第一条未审核的记录"""
    db = get_db()
    # 查找第一条is_reviewed为0的记录的ID
    record = db.execute("SELECT id FROM reviews WHERE is_reviewed = 0 ORDER BY id ASC LIMIT 1").fetchone()
    if record:
        return redirect(url_for('review_page', record_id=record['id']))
    return "🎉 恭喜！所有记录都已审核完成！"

@app.route('/review/<int:record_id>', methods=['GET', 'POST'])
def review_page(record_id):
    """审核页，展示数据并处理表单提交"""
    db = get_db()
    
    # 处理表单提交 (POST请求)
    if request.method == 'POST':
        verdict = request.form.get('verdict')
        manual_answer = request.form.get('manual_answer', '')
        manual_analysis = request.form.get('manual_analysis', '')
        
        db.execute(
            """
            UPDATE reviews 
            SET human_verdict = ?, human_answer = ?, human_analysis = ?, is_reviewed = 1
            WHERE id = ?
            """,
            (verdict, manual_answer, manual_analysis, record_id)
        )
        db.commit()
        
        # 自动跳转到下一条未审核的记录
        return redirect(url_for('index'))

    # 展示页面 (GET请求)
    record = db.execute("SELECT * FROM reviews WHERE id = ?", (record_id,)).fetchone()
    if not record:
        return "记录未找到！", 404
        
    # 解析debate_history以便在模板中展示
    debate_history = json.loads(record['debate_history'])
    
    return render_template('review.html', record=record, debate_history=debate_history)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """从配置的图片根目录提供图片文件"""
    return send_from_directory(app.config['IMAGE_ROOT'], filename)


# --- 用于初始化的数据库表结构文件 ---
# 将这个内容保存为 `schema.sql`，和`app.py`放在同一目录
# (或者，你也可以在init_db函数中直接使用这个字符串)
db_schema = """
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  image_path TEXT NOT NULL UNIQUE,
  question TEXT NOT NULL,
  gemini_answer TEXT,
  consensus_answer TEXT,
  debate_history TEXT,
  is_reviewed INTEGER NOT NULL DEFAULT 0,
  human_verdict TEXT,
  human_answer TEXT,
  human_analysis TEXT,
  reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# 将schema写入文件，以便app.open_resource能找到它
with open('schema.sql', 'w') as f:
    f.write(db_schema)

if __name__ == '__main__':
    app.run(debug=True, port=5001)