<p align="center">
  <img src="https://img.shields.io/badge/MGBX-智能量化-0052FF?style=for-the-badge" alt="MGBX"/>
  <img src="https://img.shields.io/badge/龙虾-Skill-8A2BE2?style=for-the-badge" alt="龙虾"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">🧠 MGBX 智能量化</h1>
<h3 align="center">金字塔认知交易智能体</h3>

<p align="center">
  <i>基于 MGBX 合约 API 的 AI 驱动仓位滚动引擎 —— 蒸馏顶级交易员认知，执行多步博弈推演</i>
</p>

---

## 🧬 架构哲学

> *"浮盈加仓的本质不是放大杠杆，而是让利润在非对称风险结构中自我复制。"*

**MGBX 智能量化** 不是简单的策略脚本，而是一套**硅基交易认知体系**。它融合了两位顶级交易员的思维模型：

| 流派 | 核心思想 | 关键行为 |
|------|----------|----------|
| **比特皇** | 趋势突破后浮盈加仓，复利降杠杆 | 动态杠杆 + 止损熔断 |
| **予与** | 裸K识别震荡区间做波段 | 1:1 滚仓 + 龙头聚焦 |

两条认知流线合成了一条完整的 **感知 → 推理 → 执行 → 风控** 智能体管线。

---

## 🔄 交易逻辑流程

```mermaid
flowchart TD
    A["/rolling-position"] --> B{状态检查}
    B -->|"日止损 >= 3"| Z["熔断休息"]
    B -->|正常| C[获取资金]
    C --> D[获取持仓]
    D --> E["拉取K线 4H + 1H"]
    E --> F{模式识别}

    F -->|趋势| G{有持仓?}
    F -->|震荡| H{有持仓?}

    G -->|无| G1["突破开仓<br/>杠杆50% · 止损3%"]
    G -->|"浮盈 > 10%"| G2["浮盈加仓<br/>底仓止损移至成本"]
    G -->|浮亏| G3["禁止加仓<br/>观察/止损"]
    G -->|反转| G4[平仓退出]

    H -->|无| H1["区间端点挂单<br/>杠杆60%"]
    H -->|有浮盈| H2["持有至对端80%"]
    H -->|有浮亏| H3["观察 · 等待止损"]

    G1 --> V[验证止损]
    G2 --> V
    H1 --> V

    V --> R[输出报告]
    R --> U{确认?}
    U -->|yes| X[执行交易]
    U -->|no| Y[取消]

    style Z fill:#ff4444,color:#fff
    style G3 fill:#ffaa00,color:#000
    style G1 fill:#44aa44,color:#fff
    style G2 fill:#44aa44,color:#fff
    style X fill:#0052FF,color:#fff
```

---

## ⚖️ 铁律

```
LAW 1  浮亏时绝对禁止加仓
LAW 2  单日止损 3 次 → 强制熔断
LAW 3  每一笔加仓必须绑定止损
LAW 4  止损优先级 >> 止盈
```

---

## ⚠️ MGBX 风控合规

策略行为与 [MGBX 异常交易风控规则](https://support.mgbx.com/hc/zh-cn/articles/10048306641167) 对齐：

| 规则 | 阈值 | 策略行为 |
|------|------|----------|
| 超短线交易 | 持仓 < 40s | ✅ 分钟/小时级持有 |
| API 频率 | ≤ 100次/秒 | ✅ 按需调用 |
| 撤单率 | < 70% | ✅ 市价单为主 |
| 刷单 / AB仓 | 禁止 | ✅ 单一账户单向策略 |
| 关联账户协同 | 禁止 | ✅ 不涉及多账户 |

---

## ⚡ 快速开始

### 1. 前置条件

- MGBX 合约交易权限（[联系客服开通](https://www.mgbx.com)）
- MGBX API Key（个人中心 → API 管理）

### 2. 部署

```bash
git clone https://github.com/kime2026/rolling-position-mgbx.git
cd rolling-position-mgbx

mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py && chmod +x ~/.mgbx/mgbx_api.py
```

### 3. 配置密钥

```json
{
  "access_key": "your-access-key",
  "secret_key": "your-secret-key",
  "base_url": "https://open.mgbx.com"
}
```

保存至 `~/.mgbx/config.json`

### 4. 验证

```bash
python3 ~/.mgbx/mgbx_api.py balance
```

---

## 🎮 使用

在龙虾中激活 `rolling-position` Skill：

```bash
/rolling-position btc_usdt      # 分析 BTC
/rolling-position eth_usdt      # 分析 ETH
/rolling-position               # 默认 btc_usdt
```

---

## 📡 API 映射

| 操作 | MGBX REST API |
|------|---------------|
| 资金 | `GET /fut/v1/balance/list` |
| 持仓 | `GET /fut/v1/position/list` |
| K线 | `GET /fut/v1/public/q/kline` |
| 下单 (含止损止盈) | `POST /fut/v1/order/create` |
| 一键平仓 | `POST /fut/v1/position/close-all` |
| 调整杠杆 | `POST /fut/v1/position/adjust-leverage` |
| 撤单 | `POST /fut/v1/order/cancel` |

> 完整文档：https://apidoc.mgbx.com

---

## 🔐 安全模型

```
 龙虾 (AI推理)     mgbx_api.py (本地签名)     MGBX API (执行)
      ✗                       ✓                       ✓
  AI 不接触密钥           HMAC-SHA256             交易所
```

---

## 👤 作者

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/261858468?v=4" width="100" style="border-radius: 50%;" />
</p>

<h4 align="center">Kime</h4>
<h5 align="center">05后 金融认知架构师 · AI 交易智能体构建者</h5>

<p align="center">
他是数字原生的一代，也是金融 AI 原生的定义者。<br/>
当传统量化还在回测线性回归时，Kime 正在为下一个金融时代编写<strong>会思考的交易灵魂</strong>。<br/>
他专注于金融大模型的行为对齐，不单追求夏普比率，更致力于构建具备<strong>宏观嗅觉、反脆弱推理能力</strong>的认知交易智能体。<br/>
在 Kime 的架构中，AI 不再是执行指令的工具，而是在极度不确定的市场中，能进行<strong>多步博弈推演</strong>的硅基合伙人。
</p>

<p align="center">
  <code>AI Agent 交易系统设计</code>
  <code>金融 NLP 与情绪因子挖掘</code>
  <code>投资决策智能体对齐</code>
  <code>非线性交易架构</code>
</p>

---

## ⚠️ 免责声明

> 本 Skill 是基于规则的认知交易架构，**不构成投资建议**。加密货币合约交易存在极高风险，可能导致本金全部损失。请确认止损已正确设置，仓位在你风险承受范围内。

---

<p align="center">
  <sub>Built with care by <a href="https://github.com/kime2026">Kime</a></sub>
</p>
