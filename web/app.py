from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置会话密钥

# 数据库文件路径
DATABASE = 'assignments.db'

# 初始化数据库
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                file_path TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

# 获取数据库连接
def get_db():
    return sqlite3.connect(DATABASE)

@app.route('/')
def home():
    search_query = request.args.get('search', '')
    with get_db() as conn:
        cursor = conn.cursor()
        if search_query:
            cursor.execute('SELECT * FROM assignments WHERE title LIKE ? OR description LIKE ?', 
                          (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute('SELECT * FROM assignments')
        assignments = cursor.fetchall()
    return render_template('index.html', assignments=assignments, search_query=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user[0]
                    session['role'] = user[3]
                    flash('登录成功', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('用户名或密码错误', 'error')
        else:
            flash('请填写完整信息', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        if username and password and role:
            with get_db() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                                  (username, password, role))
                    conn.commit()
                    flash('注册成功，请登录', 'success')
                    return redirect(url_for('login'))
                except sqlite3.IntegrityError:
                    flash('用户名已存在', 'error')
        else:
            flash('请填写完整信息', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('已退出登录', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)