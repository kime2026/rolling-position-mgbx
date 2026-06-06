# 🧠 MGBX 智能滚仓 · Rolling Position Strategy

> **4H 判大势 · 15min 抓拐点 · 50x 杠杆 · 保证金驱动**
>
> 下跌找"涨不动"做空 · 上涨找"跌不动"做多
> **不逆势 · 不扛单 · 不猜底**

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.0-blue" />
  <img src="https://img.shields.io/badge/platform-MGBX-green" />
  <img src="https://img.shields.io/badge/leverage-50x-red" />
  <img src="https://img.shields.io/badge/license-MIT-yellow" />
</p>

---

<details open>
<summary><b>🇨🇳 中文</b></summary>

## ⚖️ 铁律

| # | 规则 | 说明 |
|---|------|------|
| 1 | **不逆大势** | 4H 下跌只做空，上涨只做多 |
| 2 | **三次熔断** | 单日止损 >=3 → 强制休息 |
| 3 | **止损必绑** | 每笔同步设止损 |
| 4 | **移动锁利** | 浮盈 > 5% 启动移动止损 |

## 🔄 双周期架构

```
4H K线(战略)    →  趋势方向 UP/DOWN/NEUTRAL
        ↓
15min K线(战术) →  止跌/滞涨信号 → 入场+止损+止盈
        ↓
持仓管理       →  1.5R保本 + 2R追踪止盈
```

## 📊 回测结果

> **v1 原版 · 50x(实30x) · 盈亏比 1:2.5 · 1.5R保本+2R追踪**
> **MGBX 全部可用历史数据 · 全仓60%保证金驱动**

### 🏆 四币汇总

| 交易对 | 天数 | 本金 | 最终 | 收益率 | 交易 | 胜率 | 回撤 |
|--------|------|------|------|--------|------|------|------|
| **ETH** | 15.5 | $200 | **$2,443** | **+1,122%** | 9 | 56% | 48.7% |
| **BTC** | 15.5 | $200 | **$1,591** | **+696%** | 6 | 67% | 85.5% |
| SOL | 25 | $200 | $722 | +261% | 14 | 50% | 77.4% |
| LAB | 31 | $200 | — | ❌ | — | — | — |

### 📈 ETH/USDT

| # | 时间 | 方向 | 入场 | 出场 | 净利 |
|---|------|------|------|------|------|
| 1 | 05/21→05/23 | SHORT | 2112 | 2112 | -7 |
| 2 | 05/23→05/24 | SHORT | 2116 | 2123 | -19 |
| 3 | 05/24→05/26 | LONG | 2098 | 2056 | -68 💥 |
| 4 | 05/26 | LONG | 2075 | 2075 | -3 |
| 5 | 05/26→05/28 | SHORT | 2068 | 2007 | +50 ✓✓ |
| 6 | 05/28→06/03 | SHORT | 1981 | 1852 | +172 ✓✓ |
| 7 | 06/03 | SHORT | 1872 | 1794 | +231 ✓✓ |
| 8 | 06/03→06/05 | SHORT | 1793 | 1654 | +755 ✓✓ |
| 9 | 06/05 | SHORT | 1660 | 1577 | +1,132 🚀 ✓✓ |

> 净值：$200 → $193 → $174 → $103 → $153 → $556 → **$2,443**

### 📈 BTC/USDT

| # | 时间 | 方向 | 入场 | 出场 | 净利 |
|---|------|------|------|------|------|
| 1 | 05/21→05/29 | SHORT | 77080 | 73945 | +140 ✓✓ |
| 2 | 05/29→06/01 | LONG | 73793 | 73567 | -31 |
| 3 | 06/01→06/02 | SHORT | 73368 | 69761 | +263 ✓✓ |
| 4 | 06/02 | SHORT | 70029 | 71733 | -271 💥 |
| 5 | 06/02→06/04 | SHORT | 67864 | 61460 | +499 ✓✓ |
| 6 | 06/04→06/05 | SHORT | 63930 | 60290 | +792 🚀 ✓✓ |

> 净值：$200 → $340 → $309 → $300 → $29 → $800 → **$1,591**

### 📈 SOL/USDT

| # | 时间 | 方向 | 入场 | 出场 | 净利 |
|---|------|------|------|------|------|
| 1-4 | 05/12→05/15 | 混合 | — | — | +90 |
| 5-10 | 05/15→05/26 | 混合 | — | — | -245 💥 |
| 11-14 | 05/26→06/05 | SHORT | 84→62 | — | +676 🚀 |

> 净值：$200 → $290 → **$45** → $722

### 💡 洞察

1. **趋势是朋友** — 所有币种趋势确认后连续盈利
2. **仓位递减=天然风控** — 亏损后自动缩仓，恰好扛过震荡
3. **ETH > BTC > SOL >> LAB** — 主流币适配度最高
4. **保本+追踪有效** — 80%+ 盈利触发完整保护链

## 🔬 版本演进

| 版本 | 改动 | ETH 结果 | 结论 |
|------|------|----------|------|
| **v1** | 原版全仓60% | **+1,122%** 回撤49% | 🏆 最优 |
| v2 | 震荡过滤不开仓 | +80% | 💀 |
| v3 | 分层仓位10%→60% | +23% | 💀 |
| v4 | 结构+狗庄思维 | +282% | 🥈 |
| v5 | 止损反推仓位 | +175~458% | 🟡 |
| v6 | 单笔30%熔断 | +1,201% | 🟡 不稳定 |

> **v1 即最优解。所有"优化"引入新风险或牺牲收益。**

## 🚀 快速开始

```
git clone https://github.com/kime2026/rolling-position-mgbx.git
cd rolling-position-mgbx
mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py
cp SKILL.md ~/.mgbx/skills/rolling-position.md
cat > ~/.mgbx/config.json << EOF
{"access_key":"YOUR_KEY","secret_key":"YOUR_SECRET","base_url":"https://open.mgbx.com"}
EOF
python3 ~/.mgbx/mgbx_api.py balance
```

## ⚠️ 合规 · 免责

MGBX 风控全部合规（超短线/API频率/撤单率/AB仓）。
本策略不构成投资建议，合约交易存在极高风险。

</details>

<details>
<summary><b>🇬🇧 English</b></summary>

## ⚖️ Iron Rules

1. **No Counter-Trend** — 4H DOWN → short only
2. **3-Stop Breaker** — 3 daily stops → halt
3. **Always Set SL** — every position
4. **Trailing Lock** — PnL > 5% → trail

## 📊 Backtest (v1, $200, 50x→30x, 1:2.5 RR)

| Pair | Period | Final | Return | Trades | Win | Max DD |
|------|--------|-------|--------|--------|-----|--------|
| **ETH** | 15.5d | **$2,443** | **+1,122%** | 9 | 56% | 48.7% |
| **BTC** | 15.5d | **$1,591** | **+696%** | 6 | 67% | 85.5% |
| SOL | 25d | $722 | +261% | 14 | 50% | 77.4% |

### Key Insight

Trend-following with auto-shrinking position size = natural risk control.
v1 is the optimal version — all attempted "optimizations" (v2-v6) underperformed.

## 🚀 Quick Start

```
git clone https://github.com/kime2026/rolling-position-mgbx.git
cd rolling-position-mgbx
mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py
cp SKILL.md ~/.mgbx/skills/rolling-position.md
# Configure API keys in ~/.mgbx/config.json
python3 ~/.mgbx/mgbx_api.py balance
```

## ⚠️ Disclaimer

Not financial advice. Crypto futures carry extreme risk.

</details>
