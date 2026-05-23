#!/usr/bin/env python3
import sherpa_onnx
import soundfile as sf
import time
import sys

# 1. 创建流式识别器
recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
    encoder="./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20/encoder-epoch-99-avg-1.int8.onnx",
    decoder="./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20/decoder-epoch-99-avg-1.int8.onnx",
    joiner="./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20/joiner-epoch-99-avg-1.int8.onnx",
    tokens="./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20/tokens.txt",
    num_threads=1,
    sample_rate=16000,
    decoding_method="greedy_search",
)

# 2. 创建流
stream = recognizer.create_stream()

# 3. 读取音频文件
audio_file = "./sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20/test_wavs/0.wav"
samples, sample_rate = sf.read(audio_file)

# 如果音频是立体声，转单声道
if len(samples.shape) > 1:
    samples = samples[:, 0]

# 如果采样率不是 16000，需要重采样（这里简单跳过，实际可能需要处理）
if sample_rate != 16000:
    print(f"警告: 采样率为 {sample_rate}, 需要 16000。退出。")
    sys.exit(1)

# 4. 模拟实时输入：每次送 0.1 秒的音频
chunk_size = 1600  # 16000 * 0.1 = 1600 个采样点
total_samples = len(samples)
last_result = ""

print("=" * 50)
print("开始实时语音识别 (模拟麦克风输入)...")
print(f"音频时长: {total_samples/sample_rate:.1f} 秒")
print("-" * 50)

for start in range(0, total_samples, chunk_size):
    end = min(start + chunk_size, total_samples)
    chunk = samples[start:end]
    
    # 送入音频数据
    stream.accept_waveform(sample_rate, chunk)
    
    # 解码
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    
    # 获取当前识别结果
    result = recognizer.get_result(stream)
    
    # 如果有新结果，打印出来
    if result and result != last_result:
        # 用 \r 刷新当前行，实现动态更新
        sys.stdout.write("\r" + " " * 80)
        sys.stdout.flush()
        sys.stdout.write("\r" + result)
        sys.stdout.flush()
        last_result = result
    
    # 模拟实时处理速度
    time.sleep(0.1)

# 5. 最终结果
print()
print("-" * 50)
print("最终识别结果:")
final_result = recognizer.get_result(stream)
print(final_result)
print("=" * 50)
