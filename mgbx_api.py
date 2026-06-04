#!/usr/bin/env python3
"""
MGBX 合约 REST API 封装脚本
用法: python3 mgbx_api.py <command> [args...]

命令:
  balance [balanceType]         - 查询账户资金
  positions [symbol]            - 查询持仓
  orders <symbol> [state]       - 查询订单列表
  order <orderId>               - 查询订单详情
  kline <symbol> <interval> [limit] - 查询K线
  ticker <symbol>               - 查询行情
  symbol <symbol>               - 查询交易对详情
  open --symbol ... [options]   - 开仓/平仓
  closeall [symbol]             - 一键平仓
  setleverage <symbol> <lev>    - 调整杠杆
  cancel <orderId>              - 撤销订单
"""

import sys, os, json, time, hmac, hashlib, uuid, urllib.request, urllib.parse

CONFIG_PATH = os.path.expanduser("~/.mgbx/config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(json.dumps({"error": "配置文件不存在，请先创建 ~/.mgbx/config.json"}))
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)

def make_signature(params, secret_key, timestamp):
    """MGBX 签名算法: HMAC-SHA256, 参数按key字母排序后拼接timestamp"""
    sorted_keys = sorted(params.keys())
    param_str = "&".join(f"{k}={params[k]}" for k in sorted_keys)
    param_str += f"&timestamp={timestamp}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature, param_str

def api_request(method, path, params=None, auth=True):
    cfg = load_config()
    base_url = cfg["base_url"]
    
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4()).replace("-", "")[:32]
    
    url = f"{base_url}{path}"
    
    if params is None:
        params = {}
    
    headers = {}
    if auth:
        signature, _ = make_signature(params, cfg["secret_key"], timestamp)
        headers = {
            "X-Access-Key": cfg["access_key"],
            "X-Signature": signature,
            "X-Request-Timestamp": timestamp,
            "X-Request-Nonce": nonce,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    if method == "GET":
        if params:
            query_string = urllib.parse.urlencode(params)
            url += "?" + query_string
        req = urllib.request.Request(url, headers=headers, method="GET")
    elif method == "POST":
        body = urllib.parse.urlencode(params).encode('utf-8') if params else b""
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

# ─── 命令实现 ───

def cmd_balance(balance_type=None):
    params = {}
    if balance_type:
        params["balanceType"] = balance_type
    result = api_request("GET", "/fut/v1/balance/list", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_positions(symbol=None):
    params = {}
    if symbol:
        params["symbol"] = symbol
    result = api_request("GET", "/fut/v1/position/list", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_orders(symbol=None, state=None):
    params = {}
    if symbol:
        params["symbol"] = symbol
    if state:
        params["state"] = state
    result = api_request("GET", "/fut/v1/order/list", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_order(order_id):
    result = api_request("GET", "/fut/v1/order/detail", {"orderId": order_id})
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_kline(symbol, interval, limit="100"):
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    result = api_request("GET", "/fut/v1/public/q/kline", params, auth=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_ticker(symbol):
    params = {"symbol": symbol}
    result = api_request("GET", "/fut/v1/public/q/ticker", params, auth=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_symbol(symbol):
    params = {"symbol": symbol}
    result = api_request("GET", "/fut/v1/public/symbol/detail", params, auth=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_open():
    """解析 --symbol --side --posSide --type --qty [--price] [--leverage] [--sl] [--tp] [--close]"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"])
    parser.add_argument("--posSide", required=True, choices=["LONG", "SHORT"])
    parser.add_argument("--type", required=True, choices=["LIMIT", "MARKET"])
    parser.add_argument("--qty", required=True)
    parser.add_argument("--price", default=None)
    parser.add_argument("--leverage", type=int, default=None)
    parser.add_argument("--sl", dest="sl", default=None, help="止损价")
    parser.add_argument("--tp", dest="tp", default=None, help="止盈价")
    parser.add_argument("--close", action="store_true", help="平仓模式(需配合positionId)")
    parser.add_argument("--positionId", default=None, help="平仓时指定持仓ID")
    args = parser.parse_known_args()[0] if '--symbol' in sys.argv else parser.parse_args(sys.argv[2:])
    
    params = {
        "symbol": args.symbol,
        "orderSide": args.side,
        "orderType": args.type,
        "positionSide": args.posSide,
        "origQty": args.qty,
    }
    if args.price and args.type == "LIMIT":
        params["price"] = args.price
    if args.leverage:
        params["leverage"] = args.leverage
    if args.sl:
        params["triggerStopPrice"] = args.sl
    if args.tp:
        params["triggerProfitPrice"] = args.tp
    if args.close:
        params["closePosition"] = "true"
    if args.positionId:
        params["positionId"] = args.positionId
    
    result = api_request("POST", "/fut/v1/order/create", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_closeall(symbol=None):
    params = {}
    if symbol:
        params["symbol"] = symbol
    result = api_request("POST", "/fut/v1/position/close-all", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_setleverage(symbol, leverage, pos_side=None):
    params = {"symbol": symbol, "leverage": int(leverage)}
    if pos_side:
        params["positionSide"] = pos_side
    result = api_request("POST", "/fut/v1/position/adjust-leverage", params)
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_cancel(order_id):
    result = api_request("POST", "/fut/v1/order/cancel", {"orderId": order_id})
    print(json.dumps(result, indent=2, ensure_ascii=False))

# ─── 主入口 ───

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "balance":
        cmd_balance(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "positions":
        cmd_positions(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "orders":
        cmd_orders(
            sys.argv[2] if len(sys.argv) > 2 else None,
            sys.argv[3] if len(sys.argv) > 3 else None
        )
    elif cmd == "order":
        if len(sys.argv) < 3:
            print("Usage: mgbx_api.py order <orderId>")
            sys.exit(1)
        cmd_order(sys.argv[2])
    elif cmd == "kline":
        if len(sys.argv) < 4:
            print("Usage: mgbx_api.py kline <symbol> <interval> [limit]")
            sys.exit(1)
        cmd_kline(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "100")
    elif cmd == "ticker":
        if len(sys.argv) < 3:
            print("Usage: mgbx_api.py ticker <symbol>")
            sys.exit(1)
        cmd_ticker(sys.argv[2])
    elif cmd == "symbol":
        if len(sys.argv) < 3:
            print("Usage: mgbx_api.py symbol <symbol>")
            sys.exit(1)
        cmd_symbol(sys.argv[2])
    elif cmd == "open":
        cmd_open()
    elif cmd == "closeall":
        cmd_closeall(sys.argv[2] if len(sys.argv) > 2 else None)
    elif cmd == "setleverage":
        if len(sys.argv) < 4:
            print("Usage: mgbx_api.py setleverage <symbol> <leverage> [positionSide]")
            sys.exit(1)
        cmd_setleverage(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "cancel":
        if len(sys.argv) < 3:
            print("Usage: mgbx_api.py cancel <orderId>")
            sys.exit(1)
        cmd_cancel(sys.argv[2])
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()