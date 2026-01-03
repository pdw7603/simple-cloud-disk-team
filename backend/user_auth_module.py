# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, render_template_string, session
import os
import datetime
import json
import uuid

app = Flask(__name__, static_folder=None, static_url_path=None)
app.secret_key = 'simple_cloud_disk_team_2026'
USER_DATA_FILE = "/usr/local/cloud-disk/user_data.json"
SERVER_PORT = 8081
SERVER_IP = "192.168.41.130"

if not os.path.exists(USER_DATA_FILE):
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    init_admin_data = {"admin": {"password": "123456", "user_id": str(uuid.uuid4()), "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(init_admin_data, f, ensure_ascii=False, indent=4)

def read_all_users():
    with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

def require_login(func):
    def wrapper(*args, **kwargs):
        if not session.get("is_authed"):
            return redirect(f"http://{SERVER_IP}:{SERVER_PORT}/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    error_msg = ""
    success_msg = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        repassword = request.form.get('repassword', '').strip()
        if not username or not password or not repassword:
            error_msg = "用户名和密码不能为空！"
        elif len(username) <3 or len(username)>20:
            error_msg = "用户名长度需在3-20个字符之间！"
        elif len(password)<6:
            error_msg = "密码长度不能少于6位！"
        elif password != repassword:
            error_msg = "两次输入的密码不一致！"
        else:
            all_users = read_all_users()
            if username in all_users:
                error_msg = "该用户名已被注册，请更换！"
            else:
                new_user_info = {"password": password, "user_id": str(uuid.uuid4()), "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                all_users[username] = new_user_info
                save_user_data(all_users)
                success_msg = "注册成功！请返回登录页登录"
    register_html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>用户注册 - 简易云盘系统</title>
    <style>* {{margin:0;padding:0;box-sizing:border-box;}}body {{width:380px;margin:120px auto;font-family:Arial,sans-serif;font-size:16px;}}.register-box {{padding:30px;border:1px solid #e6e6e6;border-radius:8px;}}h2 {{text-align:center;color:#1677ff;margin-bottom:25px;}}.form-item {{margin-bottom:20px;}}input {{width:100%;padding:10px;border:1px solid #d9d9d9;border-radius:4px;font-size:16px;}}input:focus {{outline:none;border-color:#1677ff;}}.error {{color:#ff4d4f;text-align:center;margin-bottom:15px;height:20px;}}.success {{color:#52c41a;text-align:center;margin-bottom:15px;height:20px;}}button {{width:100%;padding:10px;background:#1677ff;color:#fff;border:none;border-radius:4px;cursor:pointer;}}button:hover {{background:#0958d9;}}.link {{text-align:center;margin-top:20px;font-size:14px;}}.link a {{color:#1677ff;text-decoration:none;}}.link a:hover {{text-decoration:underline;}}</style>
</head>
<body>
    <div class="register-box">
        <h2>用户注册</h2>
        <div class="error">{error_msg}</div>
        <div class="success">{success_msg}</div>
        <form method="post" action="/register">
            <div class="form-item"><input type="text" name="username" placeholder="请输入用户名（3-20字符）" required autocomplete="off"></div>
            <div class="form-item"><input type="password" name="password" placeholder="请输入密码（不少于6位）" required autocomplete="off"></div>
            <div class="form-item"><input type="password" name="repassword" placeholder="请再次输入密码" required autocomplete="off"></div>
            <button type="submit">立即注册</button>
            <div class="link">已有账号？<a href="/login">点击登录</a></div>
        </form>
    </div>
</body>
</html>'''
    return register_html

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    error_msg = ""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        all_users = read_all_users()
        if (username == "admin" and password == "123456") or (username in all_users and all_users[username]["password"] == password):
            session["is_authed"] = True
            session["username"] = username
            return redirect(f"http://{SERVER_IP}:{SERVER_PORT}/upload")
        else:
            error_msg = "账号或密码错误，请重新输入！"
    login_html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>系统登录 - 简易云盘系统</title>
    <style>* {{margin:0;padding:0;box-sizing:border-box;}}body {{width:380px;margin:120px auto;font-family:Arial,sans-serif;font-size:16px;}}.login-box {{padding:30px;border:1px solid #e6e6e6;border-radius:8px;}}h2 {{text-align:center;color:#1677ff;margin-bottom:25px;}}.form-item {{margin-bottom:20px;}}input {{width:100%;padding:10px;border:1px solid #d9d9d9;border-radius:4px;font-size:16px;}}input:focus {{outline:none;border-color:#1677ff;}}.error {{color:#ff4d4f;text-align:center;margin-bottom:15px;height:20px;}}button {{width:100%;padding:10px;background:#1677ff;color:#fff;border:none;border-radius:4px;cursor:pointer;}}button:hover {{background:#0958d9;}}.link {{text-align:center;margin-top:20px;font-size:14px;}}.link a {{color:#1677ff;text-decoration:none;}}.link a:hover {{text-decoration:underline;}}</style>
</head>
<body>
    <div class="login-box">
        <h2>用户登录</h2>
        <div class="error">{error_msg}</div>
        <form method="post" action="/login">
            <div class="form-item"><input type="text" name="username" placeholder="请输入用户名" required autocomplete="off"></div>
            <div class="form-item"><input type="password" name="password" placeholder="请输入密码" required autocomplete="off"></div>
            <button type="submit">登录系统</button>
            <div class="link">还没有账号？<a href="/register">立即注册</a></div>
        </form>
    </div>
</body>
</html>'''
    return login_html

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all_undefined_path(path):
    return redirect(f"http://{SERVER_IP}:{SERVER_PORT}/login")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=False, use_reloader=False)
