<p align="center">
  <img src="https://img.shields.io/badge/MGBX-智能量化-0052FF?style=for-the-badge" />
  <img src="https://img.shields.io/badge/龙虾-Skill-8A2BE2?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Leverage-50x-ff4444?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">🧠 MGBX 智能量化</h1>

<p align="center">
  <b>双周期滚仓引擎</b> · 4H 定方向 + 15min 抓拐点 · 小本金友好
</p>

<p align="center">
  <i>跌不动就多，涨不起来就空。50x 杠杆，保证金驱动仓位。永远不逆大势。</i>
</p>

<hr>

## 🧬 设计哲学

传统策略的致命缺陷：**用同一个时间框架同时判断方向和时机**——震荡中反复止损，趋势中追涨杀跌。

本策略将决策**空间解耦**为两个独立维度：

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│   4H 宏观层（战略）          15min 执行层（战术）        │
│   ────────────────          ─────────────────          │
│   · 12 根 K 线滚动            · 4 根 K 线微观结构        │
│   · 判断大方向                · 识别止跌 / 滞涨          │
│   · 只做多 / 只做空           · 确定入场点 + 止损        │
│                                                        │
│   慢变量 → 高胜率             快变量 → 优入场             │
│                                                        │
└──────────────────────────────────────────────────────┘
```

### ⚡ 小本金优化

50x 杠杆下每张合约保证金仅 **$0.15–$0.25**。$20 本金即可开数十张，打破「小资金只能买 1 张」的物理瓶颈。

| 杠杆 | 每张保证金 | $20 可开张数 |
|------|-----------|-------------|
| 20x | $0.38 | ~31 张 |
| **50x** | **$0.15** | **~80 张** |

---

## 🔄 决策流程图

```mermaid
flowchart TD
    A["📥 /rolling-position"] --> B{"🚦 熔断?"}
    B -->|"日止损 ≥ 3"| Z["🛑 休息"]
    B -->|"正常"| C["📡 4H 宏观判定"]

    C --> D{"方向?"}
    D -->|"DOWN ↓"| E["只做空"]
    D -->|"UP ↑"| F["只做多"]
    D -->|"NEUTRAL"| G["双向"]

    E --> H["🔍 15min 找涨不动"]
    F --> I["🔍 15min 找跌不动"]
    G --> J["🔍 15min 双向"]

    H --> K{"信号?"}
    I --> K
    J --> K

    K -->|"涨不动"| L["🔴 做空<br/>+ 止损"]
    K -->|"跌不动"| M["🟢 做多<br/>+ 止损"]
    K -->|"无"| N["⏳ 等待"]

    L --> O["📊 持仓管理"]
    M --> O

    O --> P{"浮盈 > 5%"}
    P -->|"是"| Q["🔒 移动止损"]
    P -->|"否"| R["保持原止损"]
    Q --> S{"浮盈 > 10%<br/>+ 宏观同向"}
    R --> S
    S -->|"是"| T["📈 加仓"]
    S -->|"否"| U["持有"]
    T --> O
    U --> O

    style Z fill:#ff4444,color:#fff
    style L fill:#ff6600,color:#fff
    style M fill:#44aa44,color:#fff
    style T fill:#0052FF,color:#fff
    style Q fill:#ffaa00,color:#000
```

---

## ⚖️ 铁律

| # | 规则 | 说明 |
|---|------|------|
| 1 | 不逆大势 | 4H 下跌只做空，上涨只做多 |
| 2 | 三次熔断 | 单日止损 3 次 → 强制休息 |
| 3 | 止损必绑 | 每笔开仓必须同步设止损 |
| 4 | 移动锁利 | 浮盈 > 5% 启动移动止损 |

---

## 📊 回测验证

> **$20 本金 · 50x 杠杆 · 60% 保证金 · 2026.5.25–6.05（BTC 暴跌 −17%）**

| 指标 | 结果 |
|------|------|
| 初始资金 | $20.00 |
| 最终资金 | **$213.43** |
| 总回报 | **+967.14%** |
| 交易次数 | 4 |
| 胜率 | **100%**（4 胜 0 负） |
| 最大回撤 | 0% |
| 止损次数 | 0 |

| # | 日期 | 方向 | 入场 | 出场 | 张数 | 保证金 | 盈亏 | 回报率 |
|---|------|------|------|------|------|--------|------|--------|
| 1 | 5/25 | 🔴 空 | 77,580 | 74,900 | 46 | $11.90 | +$12.33 | +103.6% |
| 2 | 5/27 | 🔴 空 | 75,054 | 70,924 | 77 | $19.26 | +$31.80 | +165.1% |
| 3 | 6/02 | 🔴 空 | 67,998 | 63,392 | 169 | $38.31 | +$77.84 | +203.2% |
| 4 | 6/04 | 🔴 空 | 64,370 | 62,570 | 397 | $85.18 | +$71.45 | +83.9% |

> 4H 从 5/25 起判定为持续 DOWN，15 分钟只做「涨不动就空」。
> 单边暴跌 17% 的市场中，反向赚了 967%。

---

## ⚠️ MGBX 风控合规

与 [MGBX 风控规则](https://support.mgbx.com/hc/zh-cn/articles/10048306641167) 完全对齐：

| 规则 | 阈值 | 策略实际 |
|------|------|----------|
| 超短线 | < 40s | ✅ 15min 级别 |
| API 频率 | ≤ 100 次/秒 | ✅ 按需，远低阈值 |
| 撤单率 | < 70% | ✅ 市价单为主 |
| 刷单 / AB 仓 | 禁止 | ✅ 单向，单账户 |

---

## ⚡ 快速开始

```bash
git clone https://github.com/kime2026/rolling-position-mgbx.git
cd rolling-position-mgbx

# 部署本地交易引擎
mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py
chmod +x ~/.mgbx/mgbx_api.py

# 配置 MGBX API 密钥
cat > ~/.mgbx/config.json << 'EOF'
{"access_key":"YOUR_KEY","secret_key":"YOUR_SECRET","base_url":"https://open.mgbx.com"}
EOF

# 验证
python3 ~/.mgbx/mgbx_api.py balance
```

---

## 🎮 使用

```bash
/rolling-position btc_usdt      # BTC 永续
/rolling-position               # 默认 btc_usdt
```

---

## 👤 作者

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/261858468?v=4" width="100" style="border-radius: 50%;" />
</p>

<h4 align="center">Kime</h4>
<h5 align="center">05 后金融认知架构师 · AI 交易智能体构建者</h5>

<p align="center">
他是数字原生的一代，也是金融 AI 原生的定义者。<br/>
当传统量化还在回测线性回归时，Kime 正在为下一个金融时代编写<strong>会思考的交易灵魂</strong>。<br/>
他专注于金融大模型的行为对齐，不单追求夏普比率，更致力于构建具备<strong>宏观嗅觉与反脆弱推理能力</strong>的认知交易智能体。<br/>
在 Kime 的架构中，AI 不是执行指令的工具，而是在极度不确定的市场中，能进行<strong>多步博弈推演</strong>的硅基合伙人。
</p>

<p align="center">
  <code>AI Agent 交易系统设计</code>
  <code>金融 NLP 与情绪因子挖掘</code>
  <code>投资决策智能体对齐</code>
  <code>非线性交易架构</code>
</p>

---

## ⚠️ 免责声明

> 本 Skill 是基于规则的认知交易架构，**不构成投资建议**。
> 加密货币合约交易存在极高风险，可能导致本金全部损失。

---

<p align="center">
  <sub>Built with 🧬 by <a href="https://github.com/kime2026">Kime</a> · MGBX Intelligent Quant v4.1</sub>
</p>
