<p align="center">
  <img src="https://img.shields.io/badge/MGBX-Trading-0052FF?style=for-the-badge" alt="MGBX"/>
  <img src="https://img.shields.io/badge/LobeHub-Skill-8A2BE2?style=for-the-badge" alt="LobeHub Skill"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">Rolling Position Agent</h1>
<h3 align="center">MGBX Edition</h3>

<p align="center">
  <i>AI-powered contract trading agent — distilling alpha traders' cognitive architecture into executable decisions</i>
</p>

---

## Philosophy

> *"The essence of pyramiding is not amplifying leverage — it's letting profits self-replicate within an asymmetric risk structure."*

This is not a simple strategy script. It's a **silicon-based trading cognition system** that distills the mental models of two elite traders:

| School | Core Idea | Signature Move |
|--------|-----------|----------------|
| **BitHuang** | Trend breakout pyramiding, compound deleveraging | Dynamic leverage + mandatory stop |
| **YuYu** | Naked-chart range swing trading | 1:1 rolling + leader-only focus |

Together they form a complete **Perceive -> Reason -> Execute -> Control** cognitive pipeline.

---

## Laws

```
LAW 1  Never add to a losing position
LAW 2  3 daily stops -> forced circuit breaker
LAW 3  Every add-on must carry its own stop loss
LAW 4  Stop loss priority >> Take profit
```

Four laws form the behavioral constraint layer, ensuring the AI never makes reflexive averaging-down decisions — regardless of market state.

---

## Quick Start

### 1. Get MGBX API Keys

> Contract trading requires contacting [MGBX Support](https://www.mgbx.com) to activate.

Login -> API Management -> Create Key

### 2. Deploy

```bash
git clone https://github.com/kime2026/rolling-position-mgbx.git
cd rolling-position-mgbx

mkdir -p ~/.mgbx/skills
cp mgbx_api.py ~/.mgbx/mgbx_api.py
chmod +x ~/.mgbx/mgbx_api.py
```

### 3. Configure

Save to `~/.mgbx/config.json`:

```json
{
  "access_key": "your-access-key",
  "secret_key": "your-secret-key",
  "base_url": "https://open.mgbx.com"
}
```

### 4. Verify

```bash
python3 ~/.mgbx/mgbx_api.py balance
# {"code": 0, "msg": "success", "data": [...]}
```

---

## Usage

Activate `rolling-position` Skill in LobeChat:

```bash
/rolling-position btc_usdt
/rolling-position eth_usdt
/rolling-position           # defaults to btc_usdt
```

Cognitive pipeline:

```
State Check -> Balance -> Position -> K-line -> Pattern -> Suggestion -> Confirm -> Execute
```

---

## API Map

| Action | MGBX REST API |
|--------|---------------|
| Balance | `GET /fut/v1/balance/list` |
| Position | `GET /fut/v1/position/list` |
| K-line | `GET /fut/v1/public/q/kline` |
| Order (w/ SL/TP) | `POST /fut/v1/order/create` |
| Close All | `POST /fut/v1/position/close-all` |
| Leverage | `POST /fut/v1/position/adjust-leverage` |
| Cancel | `POST /fut/v1/order/cancel` |

> Full docs: https://apidoc.mgbx.com

---

## Security

```
+-----------+       +-------------+       +-----------+
| LobeChat  |------>| mgbx_api.py |------>| MGBX API  |
| (reason)  |       | (local sign)|       | (execute) |
+-----------+       +-------------+       +-----------+
      X                    Y                    Y
  No key access     HMAC-SHA256            Exchange
```

---

## Author

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/261858468?v=4" width="120" style="border-radius: 50%;" />
</p>

<h3 align="center">Kime</h3>
<h4 align="center">Post-05 Financial Cognitive Architect &bull; AI Trading Agent Builder</h4>

<p align="center">
He is a digital native, and the definer of financial AI nativity.<br/>
While traditional quants are still backtesting linear regressions, Kime is writing <strong>trading souls that think</strong> for the next financial era.<br/>
He focuses on behavioral alignment of financial LLMs — not merely chasing Sharpe ratios, but building cognitive trading agents with <strong>macro嗅觉 (macro perception) and antifragile reasoning</strong>.<br/>
In Kime's architecture, AI is no longer a tool executing commands — it is a <strong>silicon-based partner</strong> capable of multi-step game-theoretic deduction in extremely uncertain markets.
</p>

<p align="center">
  <strong>Domains</strong><br/>
  <code>AI Agent Trading System Design</code>
  <code>Financial NLP & Sentiment Factor Mining</code>
  <code>Investment Decision Agent Alignment</code>
  <code>Nonlinear Trading Architecture</code>
</p>

---

## Disclaimer

> This Skill is a rules-based cognitive trading architecture. It does NOT constitute investment advice.
> Crypto contract trading carries extreme risk and may result in total loss of principal.
> Always verify stop-loss settings and position sizing before execution.

---

<p align="center">
  <sub>Built with care by Kime &middot; <a href="https://github.com/kime2026">GitHub</a></sub>
</p>
