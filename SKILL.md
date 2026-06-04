---
name: rolling-position
description: "智能滚仓助手 — 融合比特皇趋势滚仓与予与裸K波段两种模式。基于 MGBX API 分析行情后给出结构化操作建议，通过 Python 脚本安全执行交易（密钥不离开本地）。触发词：/rolling-position, 滚仓, 加仓策略, 仓位管理"
license: MIT
metadata:
  author: awan
  version: "3.0.0-mgbx"
---

# 智能滚仓助手 (MGBX 版)

## 概述

本 Skill 融合两位顶级交易员的核心方法论：
- **比特皇模式**：趋势突破后浮盈加仓，随资金增长动态降杠杆，三次止损强制休息
- **予与模式**：裸K识别震荡区间做波段，趋势行情浮盈1:1滚仓，只做龙头标的

**核心铁律（不可违反）**：
1. 浮亏时绝对禁止加仓
2. 单日止损3次 → 强制停止当日所有交易
3. 加仓仓位必须同时设置止损
4. 止损优先于止盈考虑

---

## 执行流程

用户调用 `/rolling-position [交易对]` 时，按以下步骤执行：

### Step 1：读取状态文件

检查 `~/.mgbx/skills/rolling-position-state.json` 是否存在：

```bash
cat ~/.mgbx/skills/rolling-position-state.json 2>/dev/null || echo '{"daily_stops": 0, "last_stop_date": "", "total_equity_usd": 0}'
```

如果 `daily_stops >= 3` 且 `last_stop_date == 今日日期` → **立即停止，输出强制休息提示，不执行任何操作**。

### Step 2：获取账户资金

通过 MGBX API 获取合约账户资金（使用 `mgbx` Python 脚本）：

```bash
python3 ~/.mgbx/mgbx_api.py balance CONTRACT
```

提取 `data` 数组中 `balanceType == "CONTRACT"` 的条目：
- `walletBalance`：钱包余额
- `availableBalance`：可用余额
- `openOrderMarginFrozen`：委托冻结
- `isolatedMargin`：逐仓保证金
- `crossedMargin`：全仓保证金

**账户总净值** = `walletBalance`（合约账户的 USDT 余额，不含赠送金 bonus）

根据净值确定**最大杠杆上限**（比特皇复利降杠杆原则）：

| 净值范围 | 最大杠杆 | 单笔最大仓位 |
|---------|---------|------------|
| < $10,000 | 20x | 净值 30% |
| $10k–$100k | 10x | 净值 25% |
| $100k–$1M | 5x | 净值 20% |
| > $1M | 3x | 净值 15% |

### Step 2.5：操作前检查（每次必做）

在执行任何交易操作前，必须先检查当前挂单和止盈止损：

```bash
# 查看当前活跃订单（NEW 状态）
python3 ~/.mgbx/mgbx_api.py orders btc_usdt NEW
```

**注意事项**：
- MGBX 在创建订单时即可附带 `triggerStopPrice` 和 `triggerProfitPrice`，无需单独创建止损单
- 修改杠杆前需确认无挂单（有挂单时调杠杆可能失败）
- 撤销订单：`python3 ~/.mgbx/mgbx_api.py cancel <orderId>`

### Step 3：获取当前持仓

```bash
python3 ~/.mgbx/mgbx_api.py positions btc_usdt
```

提取：
- `positionSize`：持仓数量（张）
- `positionSide`：LONG（多）/ SHORT（空）
- `entryPrice`：开仓均价
- `unsettledProfit`：未实现盈亏
- `leverage`：当前杠杆
- `profit.stopPrice`：止损价（如果设置了）
- `profit.profitPrice`：止盈价（如果设置了）

**浮盈率计算**：`unsettledProfit / (entryPrice × positionSize × 合约面值)`
（合约面值可通过 `python3 ~/.mgbx/mgbx_api.py symbol btc_usdt` 的 `contractSize` 获取）

### Step 4：获取 K 线数据

```bash
# 4小时 K 线
python3 ~/.mgbx/mgbx_api.py kline btc_usdt 4h 100

# 1小时 K 线
python3 ~/.mgbx/mgbx_api.py kline btc_usdt 1h 50
```

返回每根 K 线的 `o`（开盘）、`h`（最高）、`l`（最低）、`c`（收盘）、`a`（成交量）、`v`（成交额）。

同时获取4小时和1小时两个级别，用于判断趋势/震荡。

### Step 5：行情模式判断（裸K分析，不依赖指标）

#### 趋势模式判断条件（满足2条以上）
- 4H级别：连续3根以上同向K线
- 价格突破近20根K线的最高/最低点
- 回调不超过前一波涨幅的50%（更高的低点/更低的高点）
- 成交量在突破时明显放大

#### 震荡模式判断条件（满足2条以上）
- 价格在明确的高低点区间内来回运动
- 多次触及同一支撑/阻力位后反弹
- 4H级别无明显方向，1H级别有小波段
- 近期高点和低点的差距 < 15%

#### 关键价位识别
- **支撑位**：近期多次触及的低点，取最近3个低点的均值
- **阻力位**：近期多次触及的高点，取最近3个高点的均值
- **突破确认**：收盘价超过阻力位/支撑位 2% 以上

---

## 操作决策树

### 情况A：无持仓 + 趋势模式

**开仓条件**：价格刚突破阻力位（多）或跌破支撑位（空），突破幅度 > 2%

**操作**：
1. 建底仓：账户净值 × 20%，杠杆 = 当前级别最大杠杆的 50%
2. 同时设置止损：止损位 = 突破点下方 3%（多）/ 上方 3%（空）
3. 止盈目标：盈亏比至少 3:1，理想 10:1

**下单命令模板**：

MGBX 的订单创建支持直接在请求中附带止损/止盈，无需像 OKX 那样分开创建：

```bash
# === 开多 + 止损/止盈 ===
# 先调整杠杆
python3 ~/.mgbx/mgbx_api.py setleverage btc_usdt <杠杆倍数>

# 市价开多，同时附带止损和止盈
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt \
  --side BUY \
  --posSide LONG \
  --type MARKET \
  --qty <合约张数> \
  --leverage <杠杆倍数> \
  --sl <止损价> \
  --tp <止盈价>

# === 开空 + 止损/止盈 ===
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt \
  --side SELL \
  --posSide SHORT \
  --type MARKET \
  --qty <合约张数> \
  --leverage <杠杆倍数> \
  --sl <止损价> \
  --tp <止盈价>

# 【必做】验证订单（确认止损止盈已附带）
python3 ~/.mgbx/mgbx_api.py orders btc_usdt NEW
# 检查返回结果中 triggerStopPrice 和 triggerProfitPrice 是否正确
```

**补挂止损/止盈**（如果开仓时遗漏，或需要单独修改）：

MGBX 的止盈止损与持仓绑定。如需单独设置，可通过持仓列表查看 `profit` 字段。
如需修改，使用：
```bash
# 调整杠杆（如果需要）
python3 ~/.mgbx/mgbx_api.py setleverage btc_usdt <杠杆>
```

---

### 情况B：无持仓 + 震荡模式（予与裸K波段）

**开仓条件**：
- 做多：价格接近支撑位（距离 < 2%），且1H出现止跌信号（下影线、锤子线）
- 做空：价格接近阻力位（距离 < 2%），且1H出现止涨信号（上影线、射击之星）

**操作**：
1. 建仓：账户净值 × 15%，杠杆 = 当前级别最大杠杆的 60%
2. 止损：区间外 3%（支撑位下方 3% / 阻力位上方 3%）
3. 止盈：区间另一端的 80% 位置

**下单命令**：
```bash
# 震荡做多（限价单，挂支撑位附近）
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt \
  --side BUY \
  --posSide LONG \
  --type LIMIT \
  --price <支撑位附近价格> \
  --qty <合约张数> \
  --leverage <杠杆倍数> \
  --sl <止损价> \
  --tp <止盈价>

# 震荡做空（限价单，挂阻力位附近）
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt \
  --side SELL \
  --posSide SHORT \
  --type LIMIT \
  --price <阻力位附近价格> \
  --qty <合约张数> \
  --leverage <杠杆倍数> \
  --sl <止损价> \
  --tp <止盈价>
```

---

### 情况C：有持仓 + 浮盈 > 10% + 趋势延续（滚仓核心）

**加仓条件**（必须同时满足）：
- 浮盈率 > 10%（根据 `unsettledProfit` 和持仓价值计算）
- 价格继续突破新高/新低（趋势延续确认）
- 当前杠杆 < 最大杠杆上限
- 今日止损次数 < 3

**加仓规则（比特皇/予与共同原则）**：
- 加仓量 ≤ 底仓量（1:1 原则，不超过底仓）
- 加仓后整体杠杆不超过上限
- 加仓部分必须单独设置止损（止损位 = 加仓价下方 3%）
- 底仓止损上移至成本价（保本止损）

**加仓命令模板**：
```bash
# 1. 加仓（市价开多，附带止损）
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt \
  --side BUY \
  --posSide LONG \
  --type MARKET \
  --qty <加仓张数> \
  --leverage <当前杠杆> \
  --sl <加仓止损价>

# 2. 验证加仓止损已生效
python3 ~/.mgbx/mgbx_api.py orders btc_usdt NEW

# 3. 底仓止损上移至成本价
#    （MGBX持仓自带的止盈止损信息通过 position 接口查看 profit 字段）
#    目前 MGBX API 的止损修改需通过重新下单方式实现；
#    建议：加仓后通过 Web 端/App 手动将底仓止损上移至成本价
#    或者：先平底仓止损保护，再开新仓附带新止损
```

**趋势行情中保护浮盈（移动止损）**：
MGBX 支持 `TRAILING_STOP_MARKET` 委托类型。通过 WebSocket 或 Web 端可设置 trailing stop。

---

### 情况D：有持仓 + 浮亏（铁律）

**禁止加仓**，分析浮亏程度：
- 浮亏 < 5%：观察，不操作
- 浮亏 5%–止损位：等待，准备止损
- 触及止损位：**立即执行止损**

止损执行：
```bash
# 一键平掉指定交易对的全部持仓
python3 ~/.mgbx/mgbx_api.py closeall btc_usdt

# 或者平特定方向的持仓（通过下单反向平仓）
python3 ~/.mgbx/mgbx_api.py open \
  --symbol btc_usdt \
  --side SELL \
  --posSide LONG \
  --type MARKET \
  --qty <持仓张数> \
  --close
```

止损后更新状态文件（daily_stops + 1）。

---

### 情况E：有持仓 + 趋势反转信号

**平仓条件**（满足1条即可）：
- 4H级别出现明显反转形态（头肩顶/底、双顶/底）
- 价格跌破/突破关键支撑/阻力位
- 行情从趋势转为震荡（连续3根K线无方向）

**操作**：
- 信号强（形态完整）：一次性全平
- 信号弱（仅价格异常）：平仓50%，剩余移动止损

```bash
# 一键平仓
python3 ~/.mgbx/mgbx_api.py closeall btc_usdt
```

---

## 输出格式

每次分析后，输出以下结构化报告：

```
═══════════════════════════════════════
📊 滚仓策略分析报告 (MGBX)
═══════════════════════════════════════
交易对：{symbol}
当前价格：{price}
分析时间：{timestamp}

【行情模式】{趋势/震荡} - 置信度 {高/中/低}
  4H趋势：{上涨/下跌/横盘}
  关键支撑：{price}
  关键阻力：{price}

【当前持仓】
  方向：{多/空/无仓}
  均价：{entryPrice}
  持仓量：{positionSize}张
  未实现盈亏：{unsettledProfit} USDT
  止损价：{stopPrice}
  止盈价：{profitPrice}

【账户状态】
  净值：${totalEquity}
  今日止损次数：{n}/3
  最大杠杆上限：{lever}x

【操作建议】
  动作：{开仓/加仓/持仓观察/止损/平仓/强制休息}
  方向：{多/空}
  仓位：净值的 {n}%（约 ${amount}）
  杠杆：{lever}x
  入场价：{price}（{市价/限价}）
  止损位：{slPx}（亏损 {n}%）
  止盈位：{tpPx}（盈利 {n}%）
  盈亏比：{ratio}:1

【风险提示】
  {具体风险说明}

【执行确认】
  输入 'yes' 执行上述操作，输入 'no' 取消
═══════════════════════════════════════
```

---

## MGBX API 前置要求

本 Skill 通过 Python 脚本 `mgbx_api.py` 调用 MGBX REST API 执行所有交易操作，API 密钥始终存储在用户本地 `~/.mgbx/config.json`，不会传递给 AI。

### 1. 申请合约交易权限

⚠️ **重要**：MGBX 合约交易功能需要联系客服开通。请通过平台官网联系在线客服或发送邮件申请开通。

### 2. 获取 API 密钥

登录 [MGBX 官网](https://www.mgbx.com) → 个人中心 → API 管理 → 创建 API Key，获取：
- Access Key
- Secret Key

### 3. 安装配置

```bash
# 创建配置目录和文件
mkdir -p ~/.mgbx/skills

# 创建 API 配置文件 ~/.mgbx/config.json
cat > ~/.mgbx/config.json << 'EOF'
{
  "access_key": "你的AccessKey",
  "secret_key": "你的SecretKey",
  "base_url": "https://open.mgbx.com"
}
EOF

# 下载 mgbx_api.py 脚本（由本 Skill 初始化时自动创建）
# 见下方「附：mgbx_api.py 脚本」
```

### 4. 验证连接

```bash
python3 ~/.mgbx/mgbx_api.py balance
```

如果返回余额数据，说明配置成功。

### 安全说明
- API 密钥存储在本地 `~/.mgbx/config.json`，AI 不接触密钥
- 所有 API 请求签名在本地 Python 进程中完成
- 建议使用子账户 API 密钥，限制 IP 和权限范围
- 永远不要将 `config.json` 分享给他人

---

## 状态文件

`~/.mgbx/skills/rolling-position-state.json`：

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

## 使用示例

```
/rolling-position btc_usdt
/rolling-position eth_usdt
/rolling-position sol_usdt
```

不带参数时，默认分析 `btc_usdt`。

⚠️ **注意**：MGBX 交易对格式为小写+下划线，如 `btc_usdt`、`eth_usdt`。

---

## 免责声明

本 Skill 提供基于规则的策略建议，不构成投资建议。加密货币合约交易存在极高风险，可能导致本金全部损失。执行任何交易前请确认止损已正确设置，仓位大小在你的风险承受范围内。

---

## 附：mgbx_api.py 脚本

完整脚本见仓库根目录的 [mgbx_api.py](./mgbx_api.py) 文件。

安装方式：
```bash
cp mgbx_api.py ~/.mgbx/mgbx_api.py
chmod +x ~/.mgbx/mgbx_api.py
```
