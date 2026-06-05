---
name: rolling-position
description: "MGBX 智能量化 — 4H定方向 + 15min抓时机。跌不动就多，涨不起来就空。触发词：/rolling-position"
license: MIT
metadata:
  author: Kime
  version: "4.0.0"
---

# 🧠 MGBX 智能量化 · 双周期滚仓引擎

## 核心理念

> **4 小时定大方向，15 分钟抓开仓时机。**
> 大趋势向下 → 只找"涨不起来了"做空。大趋势向上 → 只找"跌不动了"做多。
> **永远不逆大势开单。**

---

## ⚖️ 铁律

1. **不逆大势** — 4H 下跌只做空，上涨只做多
2. **三次熔断** — 单日止损 3 次 → 强制停止
3. **止损必绑** — 每笔开仓必须同步设止损
4. **移动锁利** — 浮盈 > 5% 启动移动止损，只进不退

---

## 🔄 双周期架构

```
        4H K线                      15min K线
    ┌──────────┐              ┌──────────────┐
    │ 宏观方向  │──────────────▶│  开仓时机     │
    │ UP/DOWN  │  定调子       │  跌不动 → 多  │
    │          │              │  涨不动 → 空  │
    └──────────┘              └──────────────┘
```

---

## Step 1：状态检查

```bash
cat ~/.mgbx/skills/rolling-position-state.json 2>/dev/null || echo '{"daily_stops":0,"last_stop_date":"","total_equity_usd":0}'
```

`daily_stops ≥ 3` 且同日 → 🛑 熔断，不执行任何操作。

---

## Step 2：4H 宏观方向

```bash
python3 ~/.mgbx/mgbx_api.py kline btc_usdt 4h 100
```

取最近 **12 根 4H K 线**（约 2 天）：

| 判定条件 | 方向 |
|----------|------|
| 后半 6 根均价 < 前半 × 0.97（跌超 3%） | **DOWN ↓** |
| 连续 8 根低点降低（lower low） | **DOWN ↓** |
| 后半 6 根均价 > 前半 × 1.03（涨超 3%） | **UP ↑** |
| 都不满足 | **NEUTRAL** |

---

## Step 3：资金与杠杆

```bash
python3 ~/.mgbx/mgbx_api.py balance CONTRACT
```

`walletBalance` → 确定杠杆上限：

| 净值 | 最大杠杆 | 单笔上限 |
|------|---------|---------|
| < $10K | 20x | 20% |
| $10K–$100K | 10x | 25% |
| $100K–$1M | 5x | 20% |
| > $1M | 3x | 15% |

---

## Step 4：15 分钟开仓信号

```bash
python3 ~/.mgbx/mgbx_api.py kline btc_usdt 15m 100
```

### 🟢 做多（仅 4H = UP 或 NEUTRAL）

**"跌不动了"**：最近 4 根 15min K 线中，至少 3 根低点逐步抬高

止损 = 近 20 根最低点 × 0.99 | 止盈 = 入场 + (入场-止损) × 3

### 🔴 做空（仅 4H = DOWN 或 NEUTRAL）

**"涨不起来了"**：最近 4 根 15min K 线中，至少 3 根高点逐步降低

止损 = 近 20 根最高点 × 1.01 | 止盈 = 入场 - (止损-入场) × 3

---

## Step 5：持仓管理

### 浮盈加仓
浮盈 > 10% + 宏观同向 + 加仓 < 2 次 + 未熔断 → 加仓 ≤ 底仓量

### 移动止损
浮盈 > 5% 启用，向有利方向移 2%，只进不退

### 强制平仓
止损触发 / 宏观反向 / 止盈触发 → `closeall`

```bash
python3 ~/.mgbx/mgbx_api.py closeall btc_usdt
```

---

## 📊 报告格式

```
═══════════════════════════════════════
  MGBX 智能量化 · 双周期分析
═══════════════════════════════════════
交易对   {symbol}    价格  {price}

【4H宏观】{UP/DOWN/NEUTRAL}

【15min信号】
  低点: {l1} {l2} {l3} {l4}
  高点: {h1} {h2} {h3} {h4}
  信号: {跌不动/涨不动/无}

【持仓】{LONG/SHORT/无}
  均价 {entry}  张数 {size}  浮盈 {pnl}%

【建议】
  动作 {做多/做空/加仓/持仓/平仓}
  入场 {price}  止损 {sl}  止盈 {tp}
  盈亏比 {ratio}:1

[yes] 执行  [no] 取消
═══════════════════════════════════════
```

---

## ⚠️ MGBX 风控合规

| 规则 | 阈值 | 策略 |
|------|------|------|
| 超短线 | < 40s | ✅ 15min 级别 |
| API 频率 | ≤ 100/s | ✅ 按需 |
| 撤单率 | < 70% | ✅ 市价为主 |

---

## 🔌 部署

```bash
mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py && chmod +x ~/.mgbx/mgbx_api.py
cat > ~/.mgbx/config.json << 'EOF'
{"access_key":"YOUR_KEY","secret_key":"YOUR_SECRET","base_url":"https://open.mgbx.com"}
EOF
python3 ~/.mgbx/mgbx_api.py balance
```

---

## 使用

```bash
/rolling-position btc_usdt
/rolling-position          # 默认 btc_usdt
```

---

## 免责声明

不构成投资建议。加密货币合约交易存在极高风险。

---

## 附：mgbx_api.py

见 [mgbx_api.py](./mgbx_api.py)
