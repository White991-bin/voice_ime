# 哔哩哔哩项目介绍与演示
https://www.bilibili.com/video/BV1GPGR6GEU2/?spm_id_from=333.1007.top_right_bar_window_history.content.click&vd_source=5485d92863584ff934cf7703305de3f4

# 语音输入法 —— 《将进酒》智能校正版

基于 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 的实时语音识别（ASR）系统，专为背诵《将进酒》等古文优化，具备热词管理、拼音辅助校正、诗句滑动窗口匹配等功能，能够将凌乱的口语识别结果自动还原为标准诗句。

## 特性

- 极低延迟：采用 greedy_search 解码，尾静音 0.7 秒快速断句，预览推送零滞后。
- 实时预览与最终确认：WebSocket 推送预览文本（轻清洗）和确认文本（深度校正）。
- 灵活配置：通过 config.py 调整解码参数、端点检测等。
- 简洁 Web 界面：录音控制、实时显示、热词管理（添加/删除）。
- 智能校正：  
  - 热词批量替换（支持自定义热词）  
  - 拼音辅助模糊匹配（需要 pypinyin）  
  - 滑动窗口算法从全文中定位并修正诗句片段

## 目录结构

```
voice_ime/
├── app.py                # Flask 主应用，WebSocket 处理，路由
├── config.py             # 全局配置常量
├── hotwords.py           # 热词加载、保存、正则构建
├── text_utils.py         # 文本清洗、去重、增量逻辑
├── poem_corrector.py     # 《将进酒》诗句模糊匹配校正
├── asr_engine.py         # sherpa-onnx ASR 模型加载
├── templates/
│   └── index.html        # 前端界面（录音、显示、热词管理）
├── requirements.txt      # Python 依赖
└── user_hotwords.json    # 用户自定义热词（运行时生成）
```

## 依赖库

项目依赖以下 Python 库（详见 requirements.txt）：

- [sherpa-onnx](https://pypi.org/project/sherpa-onnx/) — 流式语音识别引擎
- [Flask](https://pypi.org/project/Flask/) — Web 框架
- [Flask-Sock](https://pypi.org/project/Flask-Sock/) — WebSocket 支持
- [numpy](https://pypi.org/project/numpy/) — 音频数据处理
- [pypinyin](https://pypi.org/project/pypinyin/) — 中文拼音转换（可选，但推荐）

安装命令：
```bash
pip install -r requirements.txt
```

## ASR 模型下载

本项目默认使用 sherpa-onnx 中英双语流式模型（sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20），模型文件需提前下载。

- 所有预训练模型列表：  
  [https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models](https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models)

- 本项目使用的模型直接下载：
  ```bash
  wget https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
  tar -xjf sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2
  ```

解压后目录应包含以下文件：
- encoder-epoch-99-avg-1.int8.onnx
- decoder-epoch-99-avg-1.int8.onnx
- joiner-epoch-99-avg-1.int8.onnx
- tokens.txt

请将解压后的目录路径配置到 config.py 的 MODEL_DIR 变量中（默认为 /root/voice_ime/...）。

## 快速开始

1. 克隆仓库
   ```bash
   git clone https://github.com/White991-bin/voice_ime.git
   cd voice_ime
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 下载并放置 ASR 模型（见上方说明）

4. 启动服务
   ```bash
   python app.py
   ```
   服务默认运行在 http://0.0.0.0:8080。

5. 打开浏览器访问 http://服务器IP:8080，点击“开始录音”并允许麦克风权限，即可体验实时语音输入与校正。

## 自定义配置

编辑 config.py 可调整以下关键参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| MODEL_DIR | ASR 模型路径 | /root/voice_ime/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20 |
| DECODING_METHOD | 解码策略 greedy_search / modified_beam_search | greedy_search |
| MAX_ACTIVE_PATHS | 活跃路径数（仅 beam search） | 1 |
| ENDPOINT_RULE1_SILENCE | 主尾静音时长（秒） | 0.7 |
| ENDPOINT_RULE2_SILENCE | 次尾静音时长（秒） | 0.4 |
| ENDPOINT_RULE3_UTTERANCE | 最小发声字数 | 20 |
| FORCE_ENDPOINT_LEN | 强制断句字数上限 | 60 |

修改后重启服务即可生效。

## API 接口

| 路由 | 方法 | 说明 |
|------|------|------|
| / | GET | 返回前端页面 |
| /reset | GET | 重置后端状态 |
| /get_hotwords | GET | 获取用户自定义热词 |
| /add_hotword | POST | 添加热词 {"origin":"错误词","target":"正确词"} |
| /del_hotword | POST | 删除热词 {"origin":"错误词"} |
| /ws | WebSocket | 语音流传输与识别结果推送 |

## 技术原理

- 语音识别：sherpa-onnx 流式 transducer 模型，16kHz 单声道音频。
- 清洗流水线：  
  1. 去除标签、英文字母等噪音  
  2. 正则去重（单字、短语）  
  3. 热词批量正则替换  
  4. 诗句滑动窗口匹配（移除标点后进行，支持拼音辅助）
- 实时预览：仅执行步骤 1，保证推送延迟 < 10ms。
- 端点检测：基于静音时长和发声字数自动断句。

## 常见问题

**Q: 识别结果不理想怎么办？**  
A: 在热词管理中添加常见错误映射，或调整 config.py 中的端点静音时长和解码策略。

**Q: 预览文字出现很多逗号？**  
A: 最终确认文字会自动清理多余标点，预览阶段建议保留原始输出以观察识别效果。

**Q: 如何添加其他诗词？**  
A: 编辑 poem_corrector.py 中的 JIANGJINJIU 列表，并扩充 hotwords.py 中的热词映射。

## 许可证

MIT License
