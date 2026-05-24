# 全局配置
USER_HOTWORDS_FILE = "/root/voice_ime/user_hotwords.json"
MODEL_DIR = "/root/voice_ime/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
SAMPLE_RATE = 16000
NUM_THREADS = 4
DECODING_METHOD = "greedy_search"
MAX_ACTIVE_PATHS = 1
ENDPOINT_RULE1_SILENCE = 0.7
ENDPOINT_RULE2_SILENCE = 0.4
ENDPOINT_RULE3_UTTERANCE = 20
FORCE_ENDPOINT_LEN = 60