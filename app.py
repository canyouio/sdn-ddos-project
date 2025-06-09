# ~/sdn_ddos_project/app.py
import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='sdn-ddos-frontend/dist', static_url_path='/')

@app.route('/')
def index():
    # Vue 应用的入口是 index.html
    return send_from_directory(app.static_folder, 'index.html')

# 其他所有未匹配的路由都指向 Vue 应用的 index.html，由 Vue Router 处理
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # 确保在生产环境不使用 debug=True
    app.run(host='0.0.0.0', port=5000, debug=False)
