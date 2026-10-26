---
name: fx-lstm-forecast
description: FX予測エンジン LSTMスキル - 短期〜中短期の通貨ペアリターン分布推定
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, windows]
metadata:
  hermes.tags: ["fx", "lstm", "forecast", "trading", "risk-management"]
  hermes.category: "devops"
  hermes.related_skills: ["cronjob-management", "memory-social-sync-patterns"]
  hermes.config:
    gpu.visible_device: "GPUインデックス"
    gpu.memory_fraction: "VRAM使用率上限"
    data.symbols: "予測対象シンボル"
    model.lstm.hidden_size: "LSTM_hidden_size"
    model.lstm.num_layers: "LSTM層数"
    model.lstm.dropout: "ドロップアウト率"
    model.lstm.batch_size: "バッチサイズ"
    model.lstm.max_epochs: "最大エポック数"
    risk.max_risk_per_trade: "トレードあたり最大リスク"
    risk.max_daily_loss: "日間最大損失"
    risk.max_consecutive_losses: "連続損失上限"
    execution.mode: "実行モード（research|paper|demo）"
---

# fx-lstm-forecast Skill

## When to Use

- デモ口座またはペーパートレードでLSTMモデルの妥当性を検証したいとき
- GPU 12〜16GB環境（RTX 3060/4060 Ti/5060 Ti等）で推論・学習を試したいとき
- 無料のYahooファイナンスデータ（yfinance）だけでまずは検証を開始したいとき
- Hermes Agentから `fx_forecast` ツールを叩いて予測結果を得たいとき

## Prerequisites

- Python 3.12 + CUDA 12.1+ (RTX 5060 Tiは cu128 ビルド必須)
- GPU: NVIDIA RTX 12GB以上推奨（VRAM 16GB確保）
- 仮想環境: `.venv` または `conda` env
- インストール済みパッケージ: `torch`, `numpy`, `pandas`, `yfinance`, `scikit-learn`, `fastapi`, `pyyaml`
- FXデータへのアクセス: `yfinance`（無料）または任意のREST APIエンドポイント

## How to Run

### 1. 環境セットアップ

```bash
# リポジトリのクローンまたは新規作成
git clone https://github.com/your-org/fx-research-engine.git
cd fx-research-engine

# 仮想環境構築
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux/macOS

# 依存パッケージインストール（cu128対応PyTorch）
uv pip install --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cu128 \
  torch numpy pandas yfinance scikit-learn fastapi "uvicorn[standard]" \
  scipy matplotlib pytest pyyaml

# 開発モードインストール
uv pip install -e .
```

### 2. 設定ファイルの確認

`configs/research.yaml` を確認し、以下をチェック：

```yaml
gpu:
  visible_device: "0"           # 使用GPUのインデックス
  memory_fraction: 0.85         # VRAM使用率上限（16GB環境で15GB程度に制限）
  precision: "fp16"             # 混合精度推論

data:
  symbols: ["USDJPY=X", "GBPJPY=X", "EURJPY=X"]
  timeframe: "1h"
  lookback_years: 2

model:
  lstm:
    hidden_size: 128
    num_layers: 2
    dropout: 0.3
    batch_size: 32
    max_epochs: 100

risk:
  max_risk_per_trade: 0.005
  max_daily_loss: 0.02
  max_consecutive_losses: 3
  paper_only: true

execution:
  mode: "research"          # research | paper | demo
```

### 3. 最初の予測を実行

```bash
# ツールとして実行（Hermes読み込み時）
/skill fx-lstm-forecast forecast --symbol USDJPY --timeframe H1 --horizon 5

# または CLI 直接実行
python -m fx_engine forecast --config configs/research.yaml --symbol USDJPY --timeframe H1 --horizon 5
```

## Quick Reference

| コマンド / ツール | 説明 |
|---|---|
| `/skill fx-lstm-forecast forecast` | 直近N本のリターン分布を予測 |
| `python -m fx_engine lstm train` | LSTMモデルの学習 |
| `python -m fx_engine lstm forecast` | 学習済みモデルでの推論 |
| `python -m fx_engine walkforward` | ウォークフォワード検証 |
| `python -m fx_engine report` | 学習・検証レポートの生成 |
| `python -m fx_engine paper` | ペーパートレード記録

## Alternative: Hermes Plugin

For immediate experimentation without installing dependencies, you can use the Hermes plugin `fx_lstm_forecast` which provides a simple forecast tool.

```bash
/skill fx_lstm_forecast forecast --symbol USDJPY --timeframe H1 --horizon 5
```

This plugin tries to fetch real data from Yahoo Finance; if unavailable, it falls back to deterministic mock data so you always get a prediction.

## Procedure

### ステップ 1: 環境とデータの準備

```python
# verify_cuda.py スクリプト実行
python scripts/verify_cuda.py
# → CUDA利用可・GPU名称・VRAM確認

# データ取得テスト
python -c "
import yfinance as yf
df = yf.download('USDJPY=X', period='2y', interval='1h')
print(f'取得バー数: {len(df)}')
print(f'期間: {df.index[0].date()} ~ {df.index[-1].date()}')
"
```

### ステップ 2: 特徴量エンジニアリング

`src/fx_engine/features/technicals.py` によります。以下の指標を計算し、将来のデータを参照しないよう注意：

```python
# 例: 単純移動平均・RSI・ボリンジャーバンド
def add_technical_features(df):
    df['sma_5'] = df['Close'].rolling(5).mean()
    df['sma_20'] = df['Close'].rolling(20).mean()
    delta = df['Close'].diff()
    ups = delta.clip(lower=0).rolling(14).mean()
    downs = -delta.clip(upper=0).rolling(14).mean()
    df['rsi'] = 100 - (100 / (1 + ups / downs))
    df['bb_upper'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()
    df['bb_lower'] = df['Close'].rolling(20).mean() - 2 * df['Close'].rolling(20).std()
    return df
```

### ステップ 3: データ分割（時系列順）

```python
# ランダムシャッフル厳禁！
train_end = int(len(df) * 0.7)
val_end = int(len(df) * 0.85)
train_df, val_df, test_df = df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]
```

### ステップ 4: LSTMモデル学習

`src/fx_engine/models/lstm.py` 参照。AMP (FP16) を使用し、VRAM OOM対策で `max_norm_grad` 等を設定：

```python
# モデル定義（簡略版）
class LSTMForecaster(nn.Module):
    def __init__(self, input_size, hidden_size=128, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, dropout=dropout, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)  # 1ステップ先リターン予測

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # 最後のタイムステップのみ使用
        return out
```

学習時の重要ポイント：

```python
# 混合精度学習（AMP）の有効化
scaler = torch.cuda.amp.GradScaler()
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)

for epoch in range(max_epochs):
    model.train()
    for batch in train_loader:
        inputs, targets = batch  # shape: (B, seq_len, features), (B, 1)

        optimizer.zero_grad()
        with torch.cuda.amp.autocast():
            outputs = model(inputs)
            loss = criterion(outputs, targets)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()

    # 検証・早期停止処理...
```

### ステップ 5: 推論と予測分布

```python
model.eval()
with torch.no_grad():
    with torch.cuda.amp.autocast():
        pred = model(test_inputs)  # shape: (B, 1)

    # 予測分布の計算（複数シミュレーションで区間推定）
    n_simulations = 100
    preds = []
    for _ in range(n_simulations):
        # ドロップアウト有効化によるモンテカルロ推定
        pred_i = model(test_inputs)
        preds.append(pred_i.item())

    quantiles = np.percentile(preds, [10, 50, 90])
    direction_prob = sum(1 for p in preds if p > 0) / n_simulations
```

### ステップ 6: ウォークフォワード検証

```python
#  rolling-origin cross-validation
results = []
for fold in range(n_folds):
    train = data[fold*step : fold*step + train_len]
    test = data[fold*step + train_len : fold*step + train_len + test_len]

    # モデル再学習・評価
    model, score = train_and_evaluate(train, test)
    results.append(score)

# レポートにまとめる
print(f"勝率: {sum(1 for s in results if s > 0) / len(results):.2f}")
print(f"平均シャープ: {np.mean([s['sharpe'] for s in results]):.3f}")
```

### ステップ 7: レポート生成

```bash
python -m fx_engine report --output artifacts/reports/lstm-h1-v001.json
```

## Pitfalls

1. **CUDAバージョン不一致** → RTX 5060 Ti (sm_120) は必ず `cu128` ビルドのPyTorchでないとカーネルが実行されずエラーになる。常に `torch --version` で確認。
2. **データリーク** → 時系列分割でランダムシャッフルを厳禁。特に技術指標の`shift()`処理をおろそかにすると未来情報が漏れる。
3. **バッチサイズ過大** → 16GB VRAMでも LSTM のバッチサイズ 64 以上だと OOMになることがある。`fp16`・`gradient_accumulation` で調整。
4. **予測 horizon の誤用** → 1本〜5本先まで。それ以上 then モデル不安定になるので実験時は短めに。
5. **特徴量のスケーリング忘れ** → 標準化（StandardScaler）は訓練データのみで fit し、テスト/予測時は transform だけ適用。

## Verification

### CUDA 有効確認

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0)); print('VRAM:', torch.cuda.get_device_properties(0).total_memory / 1e9, 'GB')"
# → True / NVIDIA GeForce RTX 5060 Ti / 16.311 GB
```

### LSTM 形状チェック

```python
import torch
x = torch.randn(4, 10, 5)  # (batch, seq_len, features)
print(x.shape)  # torch.Size([4, 10, 5])
# モデル forward 実行可能かテスト
```

### 予測結果の妥当性

```python
# 予測リターンが極端に外れていないかチェック
pred_return = 0.0015  # 0.15% の予測
assert -0.1 < pred_return < 0.1, "予測リターンが現実的範囲外です"
```

### レポート スキーマ検証

`artifacts/reports/*.json` は以下のキーを必須とします。

```json
{
  "symbol": "USDJPY",
  "timeframe": "H1",
  "horizon_bars": 5,
  "predicted_return": 0.0012,
  "quantiles": {"p10": -0.0008, "p50": 0.0012, "p90": 0.0027},
  "direction_probability": 0.64,
  "model_version": "lstm-h1-v001",
  "data_timestamp": "2026-10-10T12:00:00Z",
  "training_history": {...},
  "walkforward_results": [...]
}
```

## Support Files

This skill is accompanied by the following support files in the skill directory:

- `references/technical-indicators.md` - Detailed technical indicator calculations and shift() warnings
- `scripts/verify_cuda.py` - CUDA verification script
- `scripts/check_data_leak.py` - Data leakage detection script for time series

These files are referenced in the skill's `references/` directory and can be loaded via `skill_view(name='fx-lstm-forecast', file_path='references/technical-indicators.md')` etc.

ASI_ACCEL.