"""
dprs2traccar.py

D-STARのD-PRS（位置情報中継）形式で送られてくるAPRSスタイルの位置電文を、
シリアルポートから受信し、TraccarサーバーへHTTP経由で送信するPythonスクリプト。

機能概要：
- シリアルポートから1行ずつD-PRS電文を受信（STX/ETXなし、改行終端）
- $$CRCで始まる電文を解析し、コールサインと緯度・経度を抽出
- 緯度経度はNMEA/APRS形式から10進形式に変換
- TraccarのHTTP API（port 5055）へ送信し、地図上にリアルタイム表示

対応フォーマット例：
$$CRC9396,7M4MON>API705,DSTAR*:/020304h3437.54N/13534.14Eb/

ライセンス：MIT
"""

# --- 必要なライブラリのインポート ---
import serial         # シリアルポート通信用
import re             # 正規表現による文字列解析用
import requests       # HTTPリクエスト送信用（Traccarに送る）

# --- 設定項目（必要に応じて変更） ---
TRACCAR_URL = "http://localhost:5055"  # Traccar HTTP APIのURL
SERIAL_PORT = "COM9"                   # シリアルポートの指定
BAUD_RATE = 9600                       # 通信速度（bps）

# --- NMEA形式の緯度・経度を10進数形式に変換 ---
def convert_nmea_to_decimal(degree_str, direction):
    if not degree_str or '.' not in degree_str:
        return None
    # 緯度(N/S)と経度(E/W)で桁数が異なるため分岐
    if direction in ['N', 'S']:
        d = int(degree_str[:2])
        m = float(degree_str[2:])
    else:
        d = int(degree_str[:3])
        m = float(degree_str[3:])
    decimal = d + m / 60
    if direction in ['S', 'W']:
        decimal *= -1  # 南・西はマイナス値
    return round(decimal, 6)

# --- D-PRS電文の解析処理 ---
def parse_dprs(text):
    if not text.startswith("$$CRC"):  # D-PRS電文の先頭チェック
        return None, None, None

    try:
        parts = text.split(',')
        id_part = parts[1].split('>')[0]  # コールサイン抽出（例：7M4MON）
        payload = parts[2] if len(parts) > 2 else ''

        # 緯度・経度（APRS形式）を正規表現で抽出
        match = re.search(r'(\d{4,5}\.\d{2})([NS])[/\\](\d{5,6}\.\d{2})([EW])', payload)
        if match:
            lat = convert_nmea_to_decimal(match.group(1), match.group(2))
            lon = convert_nmea_to_decimal(match.group(3), match.group(4))
            return id_part, lat, lon
    except Exception as e:
        print("❌ D-PRS解析エラー:", e)

    return None, None, None

# --- Traccarサーバーへ位置情報をHTTP送信 ---
def send_to_traccar(device_id, lat, lon):
    if lat is None or lon is None or not device_id:
        return
    params = {
        "id": device_id,
        "lat": lat,
        "lon": lon
    }
    try:
        r = requests.get(TRACCAR_URL, params=params)
        print(f"✅ Traccar送信: {params} → ステータス: {r.status_code}")
    except Exception as e:
        print("❌ Traccar送信エラー:", e)

# --- メイン処理：シリアルポートからD-PRS電文を1行ずつ受信 ---
def main():
    print(f"📡 {SERIAL_PORT} を監視中（{BAUD_RATE}bps, 改行区切り D-PRSモード）...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        while True:
            try:
                # 1行受信（CRLFまたはLF区切り）
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue
                print(f"📥 受信: {line}")
                # D-PRS形式の電文を解析
                device_id, lat, lon = parse_dprs(line)
                if device_id:
                    print(f"➡️  ID={device_id}, 緯度={lat}, 経度={lon}")
                    send_to_traccar(device_id, lat, lon)
            except Exception as e:
                print("❌ 受信エラー:", e)

# --- エントリーポイント ---
if __name__ == "__main__":
    main()
