# 智能滚仓助手 (MGBX 版)

融合**比特皇趋势滚仓**与**予与裸K波段**两种模式的合约交易策略 Skill。

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/rolling-position-mgbx.git
cd rolling-position-mgbx

# 2. 安装 Python 脚本
mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py
chmod +x ~/.mgbx/mgbx_api.py

# 3. 配置 MGBX API 密钥
cat > ~/.mgbx/config.json << 'CFGEOF'
{
  "access_key": "你的AccessKey",
  "secret_key": "你的SecretKey",
  "base_url": "https://open.mgbx.com"
}
CFGEOF

# 4. 验证连接
python3 ~/.mgbx/mgbx_api.py balance
```

## 使用

在 LobeChat 中激活 `rolling-position` Skill 后：

```
/rolling-position btc_usdt
/rolling-position eth_usdt
```

## 核心铁律

1. 浮亏时绝对禁止加仓
2. 单日止损3次 -> 强制停止当日所有交易
3. 加仓仓位必须同时设置止损
4. 止损优先于止盈考虑

## 前置条件

MGBX 合约交易功能需要联系客服开通。请通过平台官网联系在线客服申请开通。

## API 文档

https://apidoc.mgbx.com

## 免责声明

本 Skill 提供基于规则的策略建议，不构成投资建议。加密货币合约交易存在极高风险。
