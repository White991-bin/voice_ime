import sherpa_onnx
from config import MODEL_DIR, SAMPLE_RATE, NUM_THREADS, DECODING_METHOD, MAX_ACTIVE_PATHS
from config import ENDPOINT_RULE1_SILENCE, ENDPOINT_RULE2_SILENCE, ENDPOINT_RULE3_UTTERANCE

def create_recognizer():
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        encoder=f"{MODEL_DIR}/encoder-epoch-99-avg-1.int8.onnx",
        decoder=f"{MODEL_DIR}/decoder-epoch-99-avg-1.int8.onnx",
        joiner=f"{MODEL_DIR}/joiner-epoch-99-avg-1.int8.onnx",
        tokens=f"{MODEL_DIR}/tokens.txt",
        num_threads=NUM_THREADS,
        sample_rate=SAMPLE_RATE,
        decoding_method=DECODING_METHOD,
        max_active_paths=MAX_ACTIVE_PATHS,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=ENDPOINT_RULE1_SILENCE,
        rule2_min_trailing_silence=ENDPOINT_RULE2_SILENCE,
        rule3_min_utterance_length=ENDPOINT_RULE3_UTTERANCE,
    )
    return recognizer