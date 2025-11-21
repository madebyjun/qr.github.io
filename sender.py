import time
import json
import base64
import math
import tkinter as tk
from PIL import ImageTk
import qrcode

# ==========================================
# 設定
# ==========================================
INPUT_FILE = 'secret_data.txt' # 送りたいファイル名
CHUNK_SIZE = 150               # QR1枚あたりの文字数（調整可）
DISPLAY_INTERVAL_MS = 200      # QR切り替え速度（ミリ秒）
# ==========================================

def create_chunks(data):
    # データをBase64化してバイナリセーフにする
    b64_data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    total_length = len(b64_data)
    total_chunks = math.ceil(total_length / CHUNK_SIZE)
    
    chunks = []
    for i in range(total_chunks):
        start = i * CHUNK_SIZE
        end = start + CHUNK_SIZE
        chunk_data = b64_data[start:end]
        
        # 順序がバラバラに読み込まれても大丈夫なようにJSON化
        # i: index, t: total, d: data
        payload = json.dumps({
            "i": i,
            "t": total_chunks,
            "d": chunk_data
        })
        chunks.append(payload)
    return chunks

def generate_qr_images(chunks):
    images = []
    for chunk in chunks:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L, # 読み取り速度優先で低めに設定
            box_size=10,
            border=4,
        )
        qr.add_data(chunk)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        images.append(img)
    return images

# GUIセットアップ
root = tk.Tk()
root.title("Secret Optical Transmitter")

# データの読み込み（ダミーデータを使用する場合はここを書き換えてください）
try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_text = f.read()
except FileNotFoundError:
    raw_text = "これはテストデータです。" * 50
    print("ファイルが見つからないため、テストデータを使用します。")

print(f"データサイズ: {len(raw_text)}文字")
chunks = create_chunks(raw_text)
qr_images = generate_qr_images(chunks)
print(f"QR枚数: {len(qr_images)}枚")

# アニメーション表示用ラベル
label = tk.Label(root)
label.pack()

current_frame = 0

def update_frame():
    global current_frame
    pil_image = qr_images[current_frame]
    tk_image = ImageTk.PhotoImage(pil_image)
    label.config(image=tk_image)
    label.image = tk_image # ガベージコレクション対策
    
    # 進捗表示
    root.title(f"Transmitting... [{current_frame + 1}/{len(qr_images)}]")
    
    current_frame = (current_frame + 1) % len(qr_images) # ループ
    root.after(DISPLAY_INTERVAL_MS, update_frame)

# 開始
update_frame()
root.mainloop()
