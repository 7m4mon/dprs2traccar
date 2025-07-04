# dprs2traccar

📡 **D-STAR の D-PRS 電文を受信し、Traccar サーバーに位置情報として送信する Python スクリプト**です。

アマチュア無線機（GPS対応 D-STAR 機）から出力される位置情報を Traccar に登録し、地図上で可視化することができます。

![](https://github.com/7m4mon/dprs2traccar/blob/main/dprs2traccar_sc.png)


---

## 🔧 主な機能

- 以下のような D-PRS 形式の電文を処理します：

  > `$$CRC9396,7M4MON>API705,DSTAR*:/020304h3437.54N/13534.14Eb/`

- 以下の情報を抽出・送信します：
  - **コールサイン**（例：`7M4MON`）→ Traccar 上のデバイスIDとして使用
  - **緯度・経度**（APRS形式 → 小数点形式に変換）

- 受信データを Traccar の HTTP API に送信し、リアルタイムに地図上に表示

---

## 🖥 動作環境

- Python 3.7 以降
- Traccar サーバー（ローカルで動作、ポート 5055）
- D-PRS 出力が可能な無線機またはゲートウェイ（シリアルポート 接続）

---

## 🔧 必要な Python ライブラリ

以下をインストールしてください：

```
pip install pyserial requests
```

---

## 🚀 使い方

スクリプトを以下のように実行します：

```
python dprs2traccar.py
```

スクリプト内で設定されているデフォルトは以下の通りです：

```
TRACCAR_URL = "http://localhost:5055"
SERIAL_PORT = "COM5"
BAUD_RATE = 9600
```

必要に応じてシリアルポートやボーレートを変更してください。

---

## 🗺 動作のしくみ

1. シリアルポートから、改行（`\n`）ごとに1行の電文を読み取ります
2. `$$CRC` で始まる行を解析し、コールサイン・緯度・経度を抽出
3. 緯度経度を 10進形式に変換
4. Traccar に以下のような HTTP リクエストで送信します：

   > `http://localhost:5055/?id=7M4MON&lat=34.625833&lon=135.569167`

5. Traccar の地図上にリアルタイム表示されます

---

## 📝 出力例

```
📡 COM5 を監視中（9600bps, 改行区切り D-PRSモード）...
📥 受信: $$CRC9396,7M4MON>API705,DSTAR*:/020304h3437.54N/13534.14Eb/
➡️  ID=7M4MON, 緯度=34.625833, 経度=135.569167
✅ Traccar送信: {'id': '7M4MON', 'lat': 34.625833, 'lon': 135.569167} → ステータス: 200
```

---

## 📜 ライセンス

このスクリプトは [MITライセンス](https://opensource.org/licenses/MIT) で公開されています。  
Traccar 本体は [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) に基づいて配布されています。

---

## 💡 補足

- Traccar 側で該当 ID（コールサイン）を登録しておくことで、マップに正しく表示されます

---

## 📞 お問い合わせ・貢献

改善提案・バグ報告・フォークも歓迎です。

