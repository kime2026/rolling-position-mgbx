---
name: rolling-position
description: "MGBX 智能量化 — 金字塔认知交易智能体。融合比特皇趋势滚仓与予与裸K波段，通过 MGBX API 执行，AI 推理 + 本地签名，密钥不离机。触发词：/rolling-position"
license: MIT
metadata:
  author: Kime
  version: "3.1.0"
---

# 🧠 MGBX 智能量化 · 滚仓引擎

## 概述

融合两位顶级交易员的认知模型，构建 AI 驱动的合约交易智能体：

| 模式 | 来源 | 核心逻辑 |
|------|------|----------|
| **趋势滚仓** | 比特皇 | 突破建仓 → 浮盈加仓 → 复利降杠杆 → 三次止损熔断 |
| **裸K波段** | 予与 | 裸K识别震荡区间 → 端点挂单 → 波段滚动 → 龙头聚焦 |

---

## ⚖️ 铁律

> 以下规则为硬约束，AI 在任何条件下不得违反：

1. **浮亏禁加仓** — 亏损头寸任何时候不得加仓
2. **三次熔断** — 单日止损达 3 次 → 强制停止当日所有操作
3. **止损必绑** — 每一笔加仓必须同步设置止损
4. **止损优先** — 止损决策优先级高于止盈

---

## 🔄 执行流水线

```
/rolling-position [交易对]
        │
        ▼
┌─────────────────────────────────────┐
│ Step 1  状态检查                      │
│  daily_stops ≥ 3 且同日 → 🛑 熔断     │
├─────────────────────────────────────┤
│ Step 2  获取资金                      │
│  walletBalance → 确定杠杆上限          │
├─────────────────────────────────────┤
│ Step 2.5  操作前检查                   │
│  撤销冲突挂单 · 确认无策略无效订单       │
├─────────────────────────────────────┤
│ Step 3  获取持仓                      │
│  entryPrice · unsettledProfit · lever │
├─────────────────────────────────────┤
│ Step 4  K线分析                      │
│  4H × 100 + 1H × 50 → 裸K模式识别     │
├─────────────────────────────────────┤
│ Step 5  输出报告 → 等待确认 → 执行      │
└─────────────────────────────────────┘
```

---

## Step 1：状态文件

```bash
cat ~/.mgbx/skills/rolling-position-state.json 2>/dev/null || echo '{"daily_stops":0,"last_stop_date":"","total_equity_usd":0}'
```

| 字段 | 含义 |
|------|------|
| `daily_stops` | 今日止损次数（≥3 → 熔断） |
| `last_stop_date` | 最近止损日期 |
| `total_equity_usd` | 账户净值快照 |
| `positions` | 持仓记忆（入场价、底仓量、加仓次数、止损位、模式） |

---

## Step 2：资金与杠杆上限

```bash
python3 ~/.mgbx/mgbx_api.py balance CONTRACT
```

提取 `balanceType == "CONTRACT"` 条目中的 `walletBalance`（不含 bonus）。

| 净值范围 | 最大杠杆 | 单笔上限 |
|---------|---------|---------|
| < $10K | 20x | 30% |
| $10K–$100K | 10x | 25% |
| $100K–$1M | 5x | 20% |
| > $1M | 3x | 15% |

---

## Step 2.5：操作前检查

```bash
python3 ~/.mgbx/mgbx_api.py orders btc_usdt NEW     # 活跃挂单
python3 ~/.mgbx/mgbx_api.py positions btc_usdt       # 持仓（含 profit 止盈止损）
```

> MGBX 创建订单时可直接附带 `triggerStopPrice` / `triggerProfitPrice`，无需额外创建止损单。
> 撤单：`python3 ~/.mgbx/mgbx_api.py cancel <orderId>`

---

## Step 3：持仓解析

```bash
python3 ~/.mgbx/mgbx_api.py positions btc_usdt
```

| 字段 | 含义 |
|------|------|
| `positionSize` | 持仓张数 |
| `positionSide` | LONG / SHORT |
| `entryPrice` | 开仓均价 |
| `unsettledProfit` | 未实现盈亏 (USDT) |
| `leverage` | 当前杠杆 |
| `profit.stopPrice` | 止损价（如有） |
| `profit.profitPrice` | 止盈价（如有） |

> 浮盈率 ≈ `unsettledProfit / (entryPrice × positionSize × contractSize)`
> `contractSize` 通过 `python3 ~/.mgbx/mgbx_api.py symbol btc_usdt` 获取

---

## Step 4：K线数据

```bash
python3 ~/.mgbx/mgbx_api.py kline btc_usdt 4h 100    # 4小时趋势
python3 ~/.mgbx/mgbx_api.py kline btc_usdt 1h 50     # 1小时结构
```

K线结构：`o`(开) `h`(高) `l`(低) `c`(收) `a`(量) `v`(额)

---

## Step 5：模式识别（裸K分析）

### 趋势判定（≥ 2 条）

- 4H 连续 3+ 根同向 K 线
- 价格突破近 20 根 K 线极值
- 回调 < 前波涨幅 50%（HL 抬高 / LH 降低）
- 突破时成交量放大

### 震荡判定（≥ 2 条）

- 价格在明确区间内往复
- 多次触及同一支撑/阻力后反弹
- 4H 无方向，1H 有波段
- 高低点差距 < 15%

### 关键位

- **支撑**：近 3 个低点均值
- **阻力**：近 3 个高点均值
- **突破确认**：收盘价超越关键位 > 2%

---

## 决策矩阵

### 🟢 A · 无持仓 + 趋势

**条件**：突破关键位 > 2%

| 动作 | 参数 |
|------|------|
| 底仓 | 净值 × 20% |
| 杠杆 | 上限的 50% |
| 止损 | 突破点 ± 3% |
| 止盈 | 盈亏比 ≥ 3:1 |

```bash
python3 ~/.mgbx/mgbx_api.py setleverage btc_usdt <杠杆>
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt --side BUY --posSide LONG --type MARKET \
  --qty <张数> --leverage <杠杆> --sl <止损> --tp <止盈>

# 空单：--side SELL --posSide SHORT
# 验证
python3 ~/.mgbx/mgbx_api.py orders btc_usdt NEW
```

---

### 🟡 B · 无持仓 + 震荡

**条件**：价距支撑/阻力 < 2%，1H 出现止跌/止涨信号

| 动作 | 参数 |
|------|------|
| 仓位 | 净值 × 15% |
| 杠杆 | 上限的 60% |
| 止损 | 区间外 3% |
| 止盈 | 对端 80% |

```bash
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt --side BUY --posSide LONG --type LIMIT \
  --price <支撑位> --qty <张数> --leverage <杠杆> --sl <止损> --tp <止盈>
```

---

### 🔵 C · 有持仓 + 浮盈 > 10% + 趋势延续

**加仓条件（全部满足）**：
- 浮盈率 > 10%
- 价格新高/新低确认
- 杠杆 < 上限
- 今日止损 < 3

**规则**：
- 加仓量 ≤ 底仓量
- 加仓部分独立止损（加仓价 ± 3%）
- 底仓止损移至成本价

```bash
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt --side BUY --posSide LONG --type MARKET \
  --qty <加仓张数> --leverage <杠杆> --sl <新止损>

# 底仓止损上移 → 通过 Web 端/App 手动操作
# 或：先平底仓保护，再开新仓附带新止损
```

---

### 🔴 D · 有持仓 + 浮亏

> ⛔ **绝对禁止加仓**

| 浮亏程度 | 动作 |
|----------|------|
| < 5% | 观察不动 |
| 5%–止损位 | 等待触发 |
| 触及止损 | 立即执行 ↓ |

```bash
python3 ~/.mgbx/mgbx_api.py closeall btc_usdt
```

执行后 `daily_stops += 1`，更新状态文件。

---

### ⚫ E · 趋势反转

**触发条件（≥ 1 条）**：
- 4H 头肩/双顶底
- 跌破/突破关键位
- 连续 3 根 K 线无方向（趋势→震荡）

```bash
python3 ~/.mgbx/mgbx_api.py closeall btc_usdt    # 强信号：全平
# 弱信号：平 50%，剩余移动止损
```

---

## 📊 输出报告

```
═══════════════════════════════════════
  MGBX 智能量化 · 滚仓分析
═══════════════════════════════════════
交易对   {symbol}
价格     {price}    时间  {timestamp}

【模式】 {趋势/震荡} · 置信度 {高/中/低}
  支撑  {support}    阻力  {resistance}

【持仓】 {LONG/SHORT/无}
  均价  {entry}     张数  {size}
  盈亏  {pnl} USDT   杠杆  {lever}x
  止损  {sl}         止盈  {tp}

【账户】
  净值  ${equity}    熔断  {stops}/3

【建议】
  动作  {开仓/加仓/观察/止损/平仓/熔断}
  方向  {多/空}      仓位  {pct}% (≈${amount})
  入场  {price}      止损  {sl} ({loss}%)
  止盈  {tp} ({gain}%)  盈亏比  {ratio}:1

【风控】{具体风险说明 + MGBX合规提示}

[yes] 执行  [no] 取消
═══════════════════════════════════════
```

---

## ⚠️ MGBX 风控合规

策略行为与 [MGBX 异常交易风控规则](https://support.mgbx.com/hc/zh-cn/articles/10048306641167) 对齐：

| 规则 | 阈值 | 策略 |
|------|------|------|
| 超短线 | 持仓 < 40s | ✅ 分钟/小时级 |
| API 频率 | ≤ 100/s | ✅ 按需调用 |
| 撤单率 | < 70% | ✅ 市价单为主 |
| 刷单/AB仓 | 禁止 | ✅ 单一方向 |
| 关联账户 | 禁止 | ✅ 不涉及 |

---

## 🔌 前置配置

### 1. 开通合约权限
联系 [MGBX 客服](https://www.mgbx.com) 开通合约交易。

### 2. 获取 API Key
MGBX 官网 → 个人中心 → API 管理

### 3. 部署

```bash
mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py && chmod +x ~/.mgbx/mgbx_api.py

cat > ~/.mgbx/config.json << 'EOF'
{"access_key":"YOUR_KEY","secret_key":"YOUR_SECRET","base_url":"https://open.mgbx.com"}
EOF

python3 ~/.mgbx/mgbx_api.py balance   # 验证
```

---

## 🔐 安全

```
 AI 推理 (龙虾)  →  本地签名 (mgbx_api.py)  →  执行 (MGBX)
       ✗                        ✓                        ✓
   密钥不可见              HMAC-SHA256               交易所
```

---

## 状态文件

`~/.mgbx/skills/rolling-position-state.json`

```json
{
  "daily_stops": 0,
  "last_stop_date": "2026-06-05",
  "total_equity_usd": 10000,
  "positions": {
    "btc_usdt": {
      "entry_price": 80000,
      "base_size": 100,
      "add_count": 0,
      "stop_loss": 77600,
      "mode": "trend"
    }
  }
}
```

---

## 使用

```bash
/rolling-position btc_usdt
/rolling-position eth_usdt
/rolling-position          # 默认 btc_usdt
```

> MGBX 交易对格式：小写 + 下划线（`btc_usdt`、`eth_usdt`）

---

## 免责声明

本 Skill 是基于规则的认知交易架构，**不构成投资建议**。加密货币合约交易存在极高风险，可能导致本金全部损失。请确认止损已正确设置，仓位在你风险承受范围内。

---

## 附：mgbx_api.py

完整脚本见 [mgbx_api.py](./mgbx_api.py)。

```bash
cp mgbx_api.py ~/.mgbx/mgbx_api.py
chmod +x ~/.mgbx/mgbx_api.py
```
