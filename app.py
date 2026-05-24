#!/usr/bin/env python3
import json
import gc
import numpy as np
from flask import Flask, render_template, request, jsonify
from flask_sock import Sock
from config import FORCE_ENDPOINT_LEN
from hotwords import load_user_hotwords, save_user_hotwords, build_hotword_replacer
from text_utils import full_clean, light_clean, common_prefix_len   # 确保导入 light_clean 和 common_prefix_len
from asr_engine import create_recognizer

app = Flask(__name__)
sock = Sock(app)

# 初始化 ASR 引擎
recognizer = create_recognizer()

# ------------------ 路由 ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset')
def reset_backend():
    return "OK"

@app.route('/get_hotwords')
def get_hotwords():
    return jsonify(load_user_hotwords())

@app.route('/add_hotword', methods=['POST'])
def add_hotword():
    data = request.json
    origin = data.get('origin')
    target = data.get('target')
    if not origin or not target:
        return "Invalid data", 400
    user_hotwords = load_user_hotwords()
    user_hotwords[origin] = target
    save_user_hotwords(user_hotwords)
    build_hotword_replacer()
    return "OK"

@app.route('/del_hotword', methods=['POST'])
def del_hotword():
    data = request.json
    origin = data.get('origin')
    user_hotwords = load_user_hotwords()
    if origin in user_hotwords:
        del user_hotwords[origin]
        save_user_hotwords(user_hotwords)
        build_hotword_replacer()
    return "OK"

# ------------------ WebSocket（含预览推送） ------------------
@sock.route('/ws')
def ws_handler(ws):
    print("新客户端连接")
    stream = recognizer.create_stream()
    last_raw_partial = ""
    last_clean_partial = ""

    while True:
        data = ws.receive()
        if data is None:
            break

        if isinstance(data, bytes):
            samples = np.frombuffer(data, dtype=np.float32)
            stream.accept_waveform(16000, samples)
            while recognizer.is_ready(stream):
                recognizer.decode_stream(stream)

            raw_result = recognizer.get_result(stream)
            force_endpoint = len(raw_result) > FORCE_ENDPOINT_LEN

            if recognizer.is_endpoint(stream) or force_endpoint:
                if raw_result:
                    clean = full_clean(raw_result)
                    if clean:
                        ws.send(json.dumps({"type": "confirmed", "text": clean}))
                recognizer.reset(stream)
                gc.collect()
                last_raw_partial = ""
                last_clean_partial = ""
            else:
                # 🔥 预览阶段：增量推送轻量清洗的文字
                if raw_result and raw_result != last_raw_partial:
                    p_len = common_prefix_len(last_raw_partial, raw_result)
                    new_part = raw_result[p_len:]
                    clean_new = light_clean(new_part)  # 仅去标签，极速
                    current_clean = last_clean_partial[:p_len] + clean_new
                    if current_clean:
                        ws.send(json.dumps({"type": "partial", "text": current_clean}))
                    last_raw_partial = raw_result
                    last_clean_partial = current_clean

if __name__ == '__main__':
    print("✅ 服务器启动: http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)