# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, render_template_string, send_from_directory, session
import os
import datetime
import json

app = Flask(__name__, static_folder=None, static_url_path=None)
app.secret_key = 'simple_cloud_disk_team_2026'
ROOT_UPLOAD_DIRECTORY = "/usr/local/cloud-disk/upload"
SERVER_PORT = 8081
SERVER_IP = "192.168.41.130"

if not os.path.exists(ROOT_UPLOAD_DIRECTORY):
    os.makedirs(ROOT_UPLOAD_DIRECTORY)

def get_current_user_upload_dir():
    current_username = session.get("username")
    if not current_username:return None
    user_upload_dir = os.path.join(ROOT_UPLOAD_DIRECTORY, current_username)
    if not os.path.exists(user_upload_dir):os.makedirs(user_upload_dir)
    return user_upload_dir

def require_login(func):
    def wrapper(*args, **kwargs):
        if not session.get("is_authed"):return redirect(f"http://{SERVER_IP}:{SERVER_PORT}/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/upload', methods=['GET', 'POST'])
@require_login
def file_upload_handler():
    error_msg = ""
    user_upload_dir = get_current_user_upload_dir()
    if not user_upload_dir:error_msg = "用户目录获取失败，请重新登录！"
    elif request.method == 'POST':
        upload_file_obj = request.files.get('file')
        if not upload_file_obj or upload_file_obj.filename.strip() == "":
            error_msg = "请选择需要上传的文件！"
        else:
            try:
                original_filename = upload_file_obj.filename.strip()
                file_save_path = os.path.join(user_upload_dir, original_filename)
                file_suffix_num =1
                while os.path.exists(file_save_path):
                    file_name_part, file_ext_part = os.path.splitext(original_filename)
                    file_save_path = os.path.join(user_upload_dir, f"{file_name_part}_{file_suffix_num}{file_ext_part}")
                    file_suffix_num +=1
                upload_file_obj.save(file_save_path)
                return redirect(f"http://{SERVER_IP}:{SERVER_PORT}/list")
            except Exception as e:error_msg = f"文件上传失败：{str(e)}"
    upload_html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>文件上传 - 简易云盘系统</title>
    <style>* {{margin:0;padding:0;box-sizing:border-box;}}body {{width:520px;margin:120px auto;font-family:Arial,sans-serif;font-size:16px;}}.upload-box {{padding:35px;border:2px dashed #d9d9d9;border-radius:8px;text-align:center;}}h2 {{text-align:center;color:#1677ff;margin-bottom:30px;}}.error {{color:#ff4d4f;text-align:center;margin-bottom:20px;height:22px;}}input[type="file"] {{margin-bottom:20px;padding:8px;font-size:16px;width:100%;}}button {{padding:10px 25px;background:#1677ff;color:#fff;border:none;border-radius:4px;cursor:pointer;}}button:hover {{background:#0958d9;}}</style>
</head>
<body>
    <h2>文件上传中心</h2>
    <div class="upload-box">
        <div class="error">{error_msg}</div>
        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" required><br>
            <button type="submit">立即上传</button>
        </form>
    </div>
</body>
</html>'''
    return upload_html

@app.route('/list')
@require_login
def user_file_list_handler():
    file_info_list = []
    user_upload_dir = get_current_user_upload_dir()
    if not user_upload_dir:return '<h3 style="text-align:center;margin:50px;color:#ff4d4f;">用户目录获取失败，请重新登录！</h3>'
    for single_filename in os.listdir(user_upload_dir):
        single_file_path = os.path.join(user_upload_dir, single_filename)
        if os.path.isfile(single_file_path):
            file_size_bytes = os.path.getsize(single_file_path)
            file_size_show = f"{round(file_size_bytes/1024,2)}KB" if file_size_bytes>1024 else f"{file_size_bytes}B"
            file_create_time = datetime.datetime.fromtimestamp(os.path.getctime(single_file_path))
            file_time_show = file_create_time.strftime("%Y-%m-%d %H:%M:%S")
            file_info_list.append((single_filename, file_size_show, file_time_show))
    file_info_list.sort(reverse=True, key=lambda x:x[2])
    file_list_html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>个人文件列表 - 简易云盘系统</title>
    <style>* {{margin:0;padding:0;box-sizing:border-box;}}body {{width:90%;margin:50px auto;font-family:Arial,sans-serif;font-size:16px;}}h2 {{text-align:center;color:#1677ff;margin-bottom:30px;}}table {{width:100%;border-collapse:collapse;margin:20px 0;}}th,td {{border:1px solid #e6e6e6;padding:12px;text-align:center;}}th {{background:#f5f5f5;font-weight:bold;}}tr:hover {{background:#fafafa;}}a {{color:#1677ff;text-decoration:none;margin:0 5px;}}a:hover {{text-decoration:underline;}}.btn-box {{text-align:center;margin-top:30px;}}.btn {{display:inline-block;padding:8px 20px;background:#1677ff;color:#fff;border-radius:4px;text-decoration:none;}}.btn:hover {{background:#0958d9;}}</style>
</head>
<body>
    <h2>个人文件列表</h2>
    <table><tr><th>文件名</th><th>文件大小</th><th>上传时间</th><th>操作</th></tr>'''
    for file_name,file_size,file_time in file_info_list:
        preview_suffix_list = ['txt','md','py','json','yml','css','js','conf']
        file_suffix = file_name.split('.')[-1].lower() if '.' in file_name else ''
        preview_button = f'<a href="/preview/{file_name}" target="_blank">预览</a> | ' if file_suffix in preview_suffix_list else ''
        file_list_html += f'<tr><td>{file_name}</td><td>{file_size}</td><td>{file_time}</td><td>{preview_button}<a href="/download/{file_name}">下载</a></td></tr>'
    if not file_info_list:file_list_html += '<tr><td colspan="4" style="color:#999;">暂无上传文件</td></tr>'
    file_list_html += '''</table>
    <div class="btn-box">
        <a href="/upload" class="btn">继续上传</a>
        <a href="/login" class="btn" style="background:#666;margin-left:15px;">返回登录</a>
    </div>
</body>
</html>'''
    return file_list_html

@app.route('/preview/<single_filename>')
@require_login
def file_preview_handler(single_filename):
    user_upload_dir = get_current_user_upload_dir()
    if not user_upload_dir:return '<h3 style="text-align:center;margin:50px;color:#ff4d4f;">用户目录获取失败！</h3>'
    target_file_path = os.path.join(user_upload_dir, single_filename)
    if os.path.isfile(target_file_path):
        with open(target_file_path, 'r', encoding='utf-8', errors='ignore') as f:file_content = f.read()
        preview_html = f'<pre style="font-size:16px;margin:50px;white-space:pre-wrap;">{file_content}</pre><center><a href="/list" style="color:#1677ff;">返回列表</a></center>'
        return preview_html
    return '<h3 style="text-align:center;margin:50px;color:#ff4d4f;">文件不存在！</h3><center><a href="/list">返回列表</a></center>'

@app.route('/download/<single_filename>')
@require_login
def file_download_handler(single_filename):
    user_upload_dir = get_current_user_upload_dir()
    if not user_upload_dir:return '<h3 style="text-align:center;margin:50px;color:#ff4d4f;">用户目录获取失败！</h3>'
    target_file_path = os.path.join(user_upload_dir, single_filename)
    if os.path.isfile(target_file_path):return send_from_directory(user_upload_dir, single_filename, as_attachment=True)
    return '<h3 style="text-align:center;margin:50px;color:#ff4d4f;">文件不存在！</h3><center><a href="/list">返回列表</a></center>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=False, use_reloader=False)
