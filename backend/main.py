# simple-cloud-disk-team 项目主入口
# 组长合并所有模块后，在此补充整合代码
from flask import Flask
app = Flask(__name__)
app.secret_key = 'simple_cloud_disk_team_2026'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
