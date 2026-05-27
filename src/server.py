import logging
import os
import sys
from typing import Dict, Optional, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from service import BybitService

# Logging configuration
logging.basicConfig(
    level=logging.INFO,  # Change logging level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# BEZPIECZENSTWO: NIE logujemy kluczy API

# Create BybitService instance
bybit_service = BybitService()

# BEZPIECZENSTWO: NIE przekazujemy kluczy do MCP env
# BEZPIECZENSTWO: USUNIETO get_secret_key() i get_access_key() -- LLM NIE moze wyciagnac kluczy
mcp = FastMCP()

from config import Config
@mcp.tool()
def get_orderbook(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    limit: int = Field(default=50, description="Number of orderbook entries to retrieve")
) -> Dict:
    """
    Get orderbook data
    :parameter
        symbol: Symbol (e.g., BTCUSDT)
        limit: Number of orderbook entries to retrieve
        category: Category (spot, linear, inverse, etc.)

    Args:
        category: Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)
        limit (int): Number of orderbook entries to retrieve

    Returns:
        Dict: Orderbook data

    Example:
        get_orderbook("spot", "BTCUSDT", 10)

    Reference:
        https://bybit-exchange.github.io/docs/v5/market/orderbook
    """
    try:
        result = bybit_service.get_orderbook(category, symbol, limit)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get orderbook: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get orderbook: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_kline(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    interval: str = Field(description="Time interval (1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M)"),
    start: Optional[int] = Field(default=None, description="Start time in milliseconds"),
    end: Optional[int] = Field(default=None, description="End time in milliseconds"),
    limit: int = Field(default=200, description="Number of records to retrieve")
) -> Dict:
    """
    Get K-line (candlestick) data

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)
        interval (str): Time interval (1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M)
        start (Optional[int]): Start time in milliseconds
        end (Optional[int]): End time in milliseconds
        limit (int): Number of records to retrieve

    Returns:
        Dict: K-line data

    Example:
        get_kline("spot", "BTCUSDT", "1h", 1625097600000, 1625184000000, 100)

    Reference:
        https://bybit-exchange.github.io/docs/v5/market/kline
    """
    try:
        result = bybit_service.get_kline(category, symbol, interval, start, end, limit)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get K-line data: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get K-line data: {e}", exc_info=True)
        return {"error": str(e)}

@mcp.tool()
def get_tickers(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)")
) -> Dict:
    """
    Get ticker information

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)

    Returns:
        Dict: Ticker information

    Example:
        get_tickers("spot", "BTCUSDT")

    Reference:
        https://bybit-exchange.github.io/docs/v5/market/tickers
    """
    try:
        result = bybit_service.get_tickers(category, symbol)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get ticker information: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get ticker information: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_wallet_balance(
    accountType: str = Field(description="Account type (UNIFIED, CONTRACT, SPOT)"),
    coin: Optional[str] = Field(default=None, description="Coin symbol")
) -> Dict:
    """
    Get wallet balance

    Args:
        accountType (str): Account type (UNIFIED, CONTRACT, SPOT)
        coin (Optional[str]): Coin symbol

    Returns:
        Dict: Wallet balance information

    Example:
        get_wallet_balance("UNIFIED", "BTC")

    Reference:
        https://bybit-exchange.github.io/docs/v5/account/wallet-balance
    """
    try:
        result = bybit_service.get_wallet_balance(accountType, coin)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get wallet balance: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get wallet balance: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_positions(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: Optional[str] = Field(default=None, description="Symbol (e.g., BTCUSDT)"),
    settleCoin: Optional[str] = Field(default=None, description="Settle coin (e.g., USDT) — list all positions on perps settled in this coin. Use this to see ALL open positions in one call without iterating symbols."),
    baseCoin: Optional[str] = Field(default=None, description="Base coin (e.g., BTC) — list all positions whose base asset matches.")
) -> Dict:
    """
    Get position information

    For linear/inverse categories Bybit requires one of: symbol, settleCoin, or baseCoin.
    Use settleCoin="USDT" to list every open USDT-perp position in a single call.

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (Optional[str]): Symbol (e.g., BTCUSDT)
        settleCoin (Optional[str]): Settle coin (e.g., USDT)
        baseCoin (Optional[str]): Base coin (e.g., BTC)

    Returns:
        Dict: Position information

    Example:
        get_positions("linear", settleCoin="USDT")   # all USDT-perp positions
        get_positions("linear", symbol="BTCUSDT")    # specific symbol

    Reference:
        https://bybit-exchange.github.io/docs/v5/position
    """
    try:
        result = bybit_service.get_positions(category, symbol, settleCoin, baseCoin)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get position information: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get position information: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def place_order(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    side: str = Field(description="Order direction (Buy, Sell)"),
    orderType: str = Field(description="Order type (Market, Limit)"),
    qty: str = Field(description="Order quantity"),
    price: Optional[str] = Field(default=None, description="Order price (for limit orders)"),
    positionIdx: Optional[str] = Field(default=None, description="Position index (1: Long, 2: Short)"),
    timeInForce: Optional[str] = Field(default=None, description="Time in force (GTC, IOC, FOK, PostOnly)"),
    orderLinkId: Optional[str] = Field(default=None, description="Order link ID"),
    isLeverage: Optional[int] = Field(default=None, description="Use leverage (0: No, 1: Yes)"),
    orderFilter: Optional[str] = Field(default=None, description="Order filter (Order, tpslOrder, StopOrder). Use 'StopOrder' for conditional/stop-limit orders (hidden from order book until triggered)."),
    triggerPrice: Optional[str] = Field(default=None, description="Trigger price for conditional orders"),
    triggerBy: Optional[str] = Field(default=None, description="Trigger basis (LastPrice, MarkPrice, IndexPrice)"),
    triggerDirection: Optional[int] = Field(default=None, description="Conditional order trigger direction. REQUIRED when triggerPrice is set: 1=triggered when price RISES through triggerPrice (e.g., short entry above market), 2=triggered when price FALLS through triggerPrice (e.g., stop-loss below market)."),
    orderIv: Optional[str] = Field(default=None, description="Order volatility"),
    takeProfit: Optional[str] = Field(default=None, description="Take profit price"),
    stopLoss: Optional[str] = Field(default=None, description="Stop loss price"),
    tpTriggerBy: Optional[str] = Field(default=None, description="Take profit trigger basis"),
    slTriggerBy: Optional[str] = Field(default=None, description="Stop loss trigger basis"),
    tpLimitPrice: Optional[str] = Field(default=None, description="Take profit limit price"),
    slLimitPrice: Optional[str] = Field(default=None, description="Stop loss limit price"),
    tpOrderType: Optional[str] = Field(default=None, description="Take profit order type (Market, Limit)"),
    slOrderType: Optional[str] = Field(default=None, description="Stop loss order type (Market, Limit)"),
    tpslMode: Optional[str] = Field(default=None, description="TP/SL mode: 'Full' (default — closes entire position) or 'Partial' (requires explicit qty)"),
    reduceOnly: Optional[bool] = Field(default=None, description="If True, order only reduces position size — critical for hedge closes (e.g., closing short hedge with buy). Prevents accidental position opening."),
    closeOnTrigger: Optional[bool] = Field(default=None, description="If True, conditional order will close the position when triggered (used for TP/SL on existing positions)")
) -> Dict:
    """
    Execute order

    Args:
        category (str): Category
            - spot: Spot trading
                * Minimum order quantity: 0.000011 BTC (up to 6 decimal places)
                * Minimum order amount: 5 USDT
                * If buying at market price, qty should be input in USDT units (e.g., "10" = 10 USDT)
                * If selling at market price, qty should be input in BTC units (e.g., "0.000100" = 0.0001 BTC)
                * If placing a limit order, qty should be input in BTC units
                * positionIdx is not used
            - linear: Futures trading (USDT margin)
                * positionIdx is required (1: Long, 2: Short)
            - inverse: Futures trading (coin margin)
                * positionIdx is required (1: Long, 2: Short)
        symbol (str): Symbol (e.g., BTCUSDT)
        side (str): Order direction (Buy, Sell)
        orderType (str): Order type (Market, Limit)
        qty (str): Order quantity
            - Market Buy: qty should be input in USDT units (e.g., "10" = 10 USDT)
            - Market Sell: qty should be input in BTC units (e.g., "0.000100" = 0.0001 BTC, up to 6 decimal places)
            - Limit: qty should be input in BTC units (e.g., "0.000100" = 0.0001 BTC, up to 6 decimal places)
        price (Optional[str]): Order price (for limit orders)
        positionIdx (Optional[str]): Position index
            - Required for futures (linear/inverse) trading
            - "1": Long position
            - "2": Short position
            - Not used for spot trading
        timeInForce (Optional[str]): Order validity period
            - GTC: Good Till Cancel (default, for limit orders)
            - IOC: Immediate or Cancel (market order)
            - FOK: Fill or Kill
            - PostOnly: Post Only
        orderLinkId (Optional[str]): Order link ID (unique value)
        isLeverage (Optional[int]): Use leverage (0: No, 1: Yes)
        orderFilter (Optional[str]): Order filter
            - Order: Regular order (default)
            - tpslOrder: TP/SL order
            - StopOrder: Stop order
        triggerPrice (Optional[str]): Trigger price for conditional orders
        triggerBy (Optional[str]): Trigger basis (LastPrice, MarkPrice, IndexPrice)
        triggerDirection (Optional[int]): Conditional order trigger direction.
            REQUIRED for conditional/stop orders (orderFilter=StopOrder).
            - 1: Triggered when LAST PRICE RISES through triggerPrice
                 (e.g., short hedge entry above current market)
            - 2: Triggered when LAST PRICE FALLS through triggerPrice
                 (e.g., stop-loss exit below current market for long position)
        orderIv (Optional[str]): Order volatility
        takeProfit (Optional[str]): Take profit price
        stopLoss (Optional[str]): Stop loss price
        tpTriggerBy (Optional[str]): Take profit trigger basis
        slTriggerBy (Optional[str]): Stop loss trigger basis
        tpLimitPrice (Optional[str]): Take profit limit price
        slLimitPrice (Optional[str]): Stop loss limit price
        tpOrderType (Optional[str]): Take profit order type (Market, Limit)
        slOrderType (Optional[str]): Stop loss order type (Market, Limit)
        tpslMode (Optional[str]): TP/SL mode for futures positions
            - "Full": TP/SL closes entire position (default for hedge mode)
            - "Partial": TP/SL closes part of position (requires explicit qty)
        reduceOnly (Optional[bool]): If True, order only reduces position size.
            Critical for hedge closes (e.g., closing short hedge with buy).
            Prevents accidental position opening.
        closeOnTrigger (Optional[bool]): If True, conditional order will close
            the position when triggered (used for TP/SL on existing positions).

    Returns:
        Dict: Order result

    Example:
        # Spot trading (SPOT account balance required)
        place_order("spot", "BTCUSDT", "Buy", "Market", "10")  # Buy market price for 10 USDT
        place_order("spot", "BTCUSDT", "Sell", "Market", "0.000100")  # Sell market price for 0.0001 BTC
        place_order("spot", "BTCUSDT", "Buy", "Limit", "0.000100", price="50000")  # Buy limit order for 0.0001 BTC

        # Spot trading - limit order + TP/SL
        place_order("spot", "BTCUSDT", "Buy", "Limit", "0.000100", price="50000",
                   takeProfit="55000", stopLoss="45000",  # TP/SL setting
                   tpOrderType="Market", slOrderType="Market")  # Execute TP/SL as market order

        # Futures trading
        place_order("linear", "BTCUSDT", "Buy", "Market", "0.001", positionIdx="1")  # Buy market price for long position
        place_order("linear", "BTCUSDT", "Sell", "Market", "0.001", positionIdx="2")  # Sell market price for short position

        # Conditional Stop-Limit Order (HIDDEN from order book — stealth advantage)
        # Short hedge entry above current price ($0.55 → trigger at $0.70):
        place_order("linear", "BSBUSDT", "Sell", "Limit", "13000",
                   price="0.7020",                # Limit price (fill)
                   triggerPrice="0.7015",          # Trigger price (activation)
                   triggerDirection=1,             # 1 = price rises through trigger
                   triggerBy="LastPrice",
                   orderFilter="StopOrder",        # Makes it conditional (hidden)
                   positionIdx="2",                # Short hedge
                   takeProfit="0.5950",            # Auto-attached TP after fill
                   tpTriggerBy="LastPrice")

        # Conditional Stop-Loss (below current price, closes long position):
        place_order("linear", "BTCUSDT", "Sell", "Market", "0.001",
                   triggerPrice="60000",
                   triggerDirection=2,             # 2 = price falls through trigger
                   triggerBy="MarkPrice",
                   orderFilter="StopOrder",
                   positionIdx="1",
                   reduceOnly=True,                # Only closes position
                   closeOnTrigger=True)            # Position close on trigger

    Notes:
        1. Spot trading order quantity restrictions:
            - Minimum order quantity: 0.000011 BTC
            - Minimum order amount: 5 USDT
            - BTC quantity is only allowed up to 6 decimal places (e.g., 0.000100 O, 0.0001234 X)
        2. Pay attention to unit when buying/selling at market price:
            - Buying: qty should be input in USDT units (e.g., "10" = 10 USDT)
            - Selling: qty should be input in BTC units (e.g., "0.000100" = 0.0001 BTC)
        3. Futures trading requires positionIdx:
            - Long position: positionIdx="1"
            - Short position: positionIdx="2"
        4. positionIdx is not used for spot trading

    Reference:
        https://bybit-exchange.github.io/docs/v5/order/create-order
    """
    try:
        # BEZPIECZENSTWO: Trading musi byc jawnie wlaczony
        if not Config.TRADING_ENABLED:
            return {"error": "Trading is DISABLED. Set TRADING_ENABLED=true to enable."}

        # BEZPIECZENSTWO: Walidacja inputow
        if side not in ("Buy", "Sell"):
            return {"error": f"Invalid side: {side}. Must be 'Buy' or 'Sell'."}
        if orderType not in ("Market", "Limit"):
            return {"error": f"Invalid orderType: {orderType}. Must be 'Market' or 'Limit'."}
        if category not in ("spot", "linear", "inverse", "option"):
            return {"error": f"Invalid category: {category}. Must be 'spot', 'linear', 'inverse', or 'option'."}

        # BEZPIECZENSTWO: Max order size check
        from config import MAX_ORDER_SIZE_USDT
        try:
            qty_float = float(qty)
            if category == "spot" and side == "Buy" and orderType == "Market":
                # Market buy na spot -- qty jest w USDT
                if qty_float > MAX_ORDER_SIZE_USDT:
                    return {"error": f"Order size {qty} USDT exceeds max {MAX_ORDER_SIZE_USDT} USDT. Adjust MAX_ORDER_SIZE_USDT env var."}
        except ValueError:
            return {"error": f"Invalid qty: {qty}. Must be a number."}

        result = bybit_service.place_order(
            category=category, symbol=symbol, side=side, orderType=orderType,
            qty=qty, price=price, positionIdx=positionIdx,
            timeInForce=timeInForce, orderLinkId=orderLinkId,
            isLeverage=isLeverage, orderFilter=orderFilter,
            triggerPrice=triggerPrice, triggerBy=triggerBy,
            triggerDirection=triggerDirection, orderIv=orderIv,
            takeProfit=takeProfit, stopLoss=stopLoss,
            tpTriggerBy=tpTriggerBy, slTriggerBy=slTriggerBy,
            tpLimitPrice=tpLimitPrice, slLimitPrice=slLimitPrice,
            tpOrderType=tpOrderType, slOrderType=slOrderType,
            tpslMode=tpslMode, reduceOnly=reduceOnly,
            closeOnTrigger=closeOnTrigger
        )
        if result.get("retCode") != 0:
            logger.error(f"Failed to place order: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to place order: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def cancel_order(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    orderId: Optional[str] = Field(default=None, description="Order ID"),
    orderLinkId: Optional[str] = Field(default=None, description="Order link ID"),
    orderFilter: Optional[str] = Field(default=None, description="Order filter")
) -> Dict:
    """
    Cancel order

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)
        orderId (Optional[str]): Order ID
        orderLinkId (Optional[str]): Order link ID
        orderFilter (Optional[str]): Order filter

    Returns:
        Dict: Cancel result

    Example:
        cancel_order("spot", "BTCUSDT", "123456789")

    Reference:
        https://bybit-exchange.github.io/docs/v5/order/cancel-order
    """
    try:
        if not Config.TRADING_ENABLED:
            return {"error": "Trading is DISABLED. Set TRADING_ENABLED=true to enable."}
        result = bybit_service.cancel_order(category, symbol, orderId, orderLinkId, orderFilter)
        if result.get("retCode") != 0:
            logger.error(f"Failed to cancel order: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to cancel order: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_order_history(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: Optional[str] = Field(default=None, description="Symbol (e.g., BTCUSDT)"),
    orderId: Optional[str] = Field(default=None, description="Order ID"),
    orderLinkId: Optional[str] = Field(default=None, description="Order link ID"),
    orderFilter: Optional[str] = Field(default=None, description="Order filter"),
    orderStatus: Optional[str] = Field(default=None, description="Order status"),
    startTime: Optional[int] = Field(default=None, description="Start time in milliseconds"),
    endTime: Optional[int] = Field(default=None, description="End time in milliseconds"),
    limit: int = Field(default=50, description="Number of orders to retrieve"),
    settleCoin: Optional[str] = Field(default=None, description="Settle coin (e.g., USDT) — list all orders settled in this coin (alternative to symbol)."),
    baseCoin: Optional[str] = Field(default=None, description="Base coin (e.g., BTC) — list all orders whose base asset matches.")
) -> Dict:
    """
    Get order history

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (Optional[str]): Symbol (e.g., BTCUSDT)
        orderId (Optional[str]): Order ID
        orderLinkId (Optional[str]): Order link ID
        orderFilter (Optional[str]): Order filter
        orderStatus (Optional[str]): Order status
        startTime (Optional[int]): Start time in milliseconds
        endTime (Optional[int]): End time in milliseconds
        limit (int): Number of orders to retrieve
        settleCoin (Optional[str]): Settle coin (e.g., USDT)
        baseCoin (Optional[str]): Base coin (e.g., BTC)

    Returns:
        Dict: Order history

    Example:
        get_order_history("linear", settleCoin="USDT", limit=50)
        get_order_history("spot", "BTCUSDT", "123456789")

    Reference:
        https://bybit-exchange.github.io/docs/v5/order/order-list
    """
    try:
        result = bybit_service.get_order_history(
            category, symbol, orderId, orderLinkId,
            orderFilter, orderStatus, startTime, endTime, limit,
            settleCoin, baseCoin
        )
        if result.get("retCode") != 0:
            logger.error(f"Failed to get order history: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get order history: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_open_orders(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: Optional[str] = Field(default=None, description="Symbol (e.g., BTCUSDT)"),
    orderId: Optional[str] = Field(default=None, description="Order ID"),
    orderLinkId: Optional[str] = Field(default=None, description="Order link ID"),
    orderFilter: Optional[str] = Field(default=None, description="Order filter"),
    limit: int = Field(default=50, description="Number of orders to retrieve"),
    settleCoin: Optional[str] = Field(default=None, description="Settle coin (e.g., USDT) — list all open orders settled in this coin (alternative to symbol). Use this to see ALL pending orders in one call."),
    baseCoin: Optional[str] = Field(default=None, description="Base coin (e.g., BTC) — list all open orders whose base asset matches.")
) -> Dict:
    """
    Get open orders

    For linear/inverse categories Bybit requires one of: symbol, settleCoin, or baseCoin.
    Use settleCoin="USDT" to list every pending order in a single call.

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (Optional[str]): Symbol (e.g., BTCUSDT)
        orderId (Optional[str]): Order ID
        orderLinkId (Optional[str]): Order link ID
        orderFilter (Optional[str]): Order filter
        limit (int): Number of orders to retrieve
        settleCoin (Optional[str]): Settle coin (e.g., USDT)
        baseCoin (Optional[str]): Base coin (e.g., BTC)

    Returns:
        Dict: Open orders

    Example:
        get_open_orders("linear", settleCoin="USDT")   # all pending USDT-perp orders
        get_open_orders("spot", "BTCUSDT")             # specific symbol

    Reference:
        https://bybit-exchange.github.io/docs/v5/order/open-order
    """
    try:
        result = bybit_service.get_open_orders(
            category, symbol, orderId, orderLinkId, orderFilter, limit,
            settleCoin, baseCoin
        )
        if result.get("retCode") != 0:
            logger.error(f"Failed to get open orders: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get open orders: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def set_trading_stop(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    takeProfit: Optional[str] = Field(default=None, description="Take profit price"),
    stopLoss: Optional[str] = Field(default=None, description="Stop loss price"),
    trailingStop: Optional[str] = Field(default=None, description="Trailing stop"),
    positionIdx: Optional[int] = Field(default=None, description="Position index")
) -> Dict:
    """
    Set trading stop

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)
        takeProfit (Optional[str]): Take profit price
        stopLoss (Optional[str]): Stop loss price
        trailingStop (Optional[str]): Trailing stop
        positionIdx (Optional[int]): Position index

    Returns:
        Dict: Setting result

    Example:
        set_trading_stop("spot", "BTCUSDT", "55000", "45000", "1000", 0)

    Reference:
        https://bybit-exchange.github.io/docs/v5/position/trading-stop
    """
    try:
        result = bybit_service.set_trading_stop(
            category, symbol, takeProfit, stopLoss, trailingStop, positionIdx
        )
        if result.get("retCode") != 0:
            logger.error(f"Failed to set trading stop: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to set trading stop: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def set_margin_mode(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    tradeMode: int = Field(description="Trading mode (0: Isolated, 1: Cross)"),
    buyLeverage: str = Field(description="Buying leverage"),
    sellLeverage: str = Field(description="Selling leverage")
) -> Dict:
    """
    Set margin mode

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)
        tradeMode (int): Trading mode (0: Isolated, 1: Cross)
        buyLeverage (str): Buying leverage
        sellLeverage (str): Selling leverage

    Returns:
        Dict: Setting result

    Example:
        set_margin_mode("spot", "BTCUSDT", 0, "10", "10")

    Reference:
        https://bybit-exchange.github.io/docs/v5/account/set-margin-mode
    """
    try:
        result = bybit_service.set_margin_mode(
            category, symbol, tradeMode, buyLeverage, sellLeverage
        )
        if result.get("retCode") != 0:
            logger.error(f"Failed to set margin mode: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to set margin mode: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_api_key_information() -> Dict:
    """
    Get API key information

    Returns:
        Dict: API key information

    Example:
        get_api_key_information()

    Reference:
        https://bybit-exchange.github.io/docs/v5/user/apikey-info
    """
    try:
        result = bybit_service.get_api_key_information()
        if result.get("retCode") != 0:
            logger.error(f"Failed to get API key information: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get API key information: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_risk_limit(
    category: str = Field(description="Category ('linear' for USDT-perp, 'inverse' for coin-margined perp)"),
    symbol: Optional[str] = Field(default=None, description="Symbol (e.g., BTCUSDT). If omitted, returns all symbols in category.")
) -> Dict:
    """
    Get risk limit tiers for Bybit perpetual contracts.

    Each tier defines maximum position notional (USD), maintenance margin rate
    (MMR), initial margin rate (IMR), and maximum leverage. As a position's
    notional grows, Bybit auto-promotes it to higher tiers with worse margin
    terms (higher IM/MM, lower max leverage). Critical for position sizing.

    Args:
        category (str): 'linear' | 'inverse'
        symbol (Optional[str]): Symbol like 'BTCUSDT' or 'BSBUSDT'. Omit for all.

    Returns:
        Dict: List of tier dicts with id, riskLimitValue, maintenanceMargin,
              initialMargin, maxLeverage, isLowestRisk.

    Example:
        get_risk_limit("linear", "BSBUSDT")
        # Returns: 30 tiers ranging from $5K @ 25x to $2.5M @ 1x

    Reference:
        https://bybit-exchange.github.io/docs/v5/market/risk-limit
    """
    try:
        result = bybit_service.get_risk_limit(category, symbol)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get risk limit: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get risk limit: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def get_instruments_info(
    category: str = Field(description="Category (spot, linear, inverse, etc.)"),
    symbol: str = Field(description="Symbol (e.g., BTCUSDT)"),
    status: Optional[str] = Field(default=None, description="Status"),
    baseCoin: Optional[str] = Field(default=None, description="Base coin")
) -> Dict:
    """
    Get exchange information

    Args:
        category (str): Category (spot, linear, inverse, etc.)
        symbol (str): Symbol (e.g., BTCUSDT)
        status (Optional[str]): Status
        baseCoin (Optional[str]): Base coin

    Returns:
        Dict: Exchange information

    Example:
        get_instruments_info("spot", "BTCUSDT", "Trading", "BTC")

    Reference:
        https://bybit-exchange.github.io/docs/v5/market/instrument
    """
    try:
        result = bybit_service.get_instruments_info(category, symbol, status, baseCoin)
        if result.get("retCode") != 0:
            logger.error(f"Failed to get instruments information: {result.get('retMsg')}")
            return {"error": result.get("retMsg")}
        return result
    except Exception as e:
        logger.error(f"Failed to get instruments information: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.prompt()
def prompt(message: str) -> str:
    return f"""
You are an AI assistant providing access to Bybit API functionalities through available tools.
Analyze user requests and utilize the appropriate tools to fetch data, manage account information, or execute/manage orders as requested.

Available tools:
- get_orderbook(category, symbol, limit) - Get orderbook: Retrieve orderbook information for a specific category and symbol. limit parameter can be used to specify the number of orderbook entries to retrieve.
- get_kline(category, symbol, interval, start, end, limit) - Get K-line data: Retrieve K-line data for a specific category and symbol. interval, start, end, and limit parameters can be used to specify the retrieval range and number of records.
- get_tickers(category, symbol) - Get ticker information: Retrieve ticker information for a specific category and symbol.
- get_trades(category, symbol, limit) - Get recent trade history: Retrieve recent trade history for a specific category and symbol. limit parameter can be used to specify the number of trades to retrieve.
- get_wallet_balance(accountType, coin) - Get wallet balance: Retrieve wallet balance information for a specific account type and coin.
- get_positions(category, symbol) - Get position information: Retrieve position information for a specific category and symbol.
- place_order(category, symbol, side, orderType, qty, price, timeInForce, orderLinkId, isLeverage, orderFilter, triggerPrice, triggerBy, triggerDirection, orderIv, positionIdx, takeProfit, stopLoss, tpTriggerBy, slTriggerBy, tpLimitPrice, slLimitPrice, tpOrderType, slOrderType, tpslMode, reduceOnly, closeOnTrigger) - Execute order: Execute an order. Supports regular limit/market orders, conditional/stop-limit orders (orderFilter=StopOrder + triggerPrice + triggerDirection), and attached TP/SL. Critical for hedge cycles: use triggerDirection=1 for short entry above market, =2 for stop-loss below market. reduceOnly=True for hedge closes.
- cancel_order(category, symbol, orderId, orderLinkId, orderFilter) - Cancel order: Cancel a specific order. orderId, orderLinkId, and orderFilter parameters can be used to specify the order to cancel.
- get_order_history(category, symbol, orderId, orderLinkId, orderFilter, orderStatus, startTime, endTime, limit) - Get order history: Retrieve order history. Various parameters can be used to specify the retrieval range and conditions.
- get_open_orders(category, symbol, orderId, orderLinkId, orderFilter, limit) - Get open orders: Retrieve open orders. limit parameter can be used to specify the number of orders to retrieve.
- get_leverage_info(category, symbol) - Get leverage information: Retrieve leverage information for a specific category and symbol.
- set_trading_stop(category, symbol, takeProfit, stopLoss, trailingStop, positionIdx) - Set trading stop: Set trading stop. takeProfit, stopLoss, trailingStop, and positionIdx parameters can be used to specify the settings.
- set_margin_mode(category, symbol, tradeMode, buyLeverage, sellLeverage) - Set margin mode: Set margin mode. tradeMode, buyLeverage, and sellLeverage parameters can be used to specify the settings.
- get_api_key_information() - Get API key information: Retrieve API key information.
- get_instruments_info(category, symbol, status, baseCoin) - Get exchange information: Retrieve exchange information. status and baseCoin parameters can be used to specify the retrieval conditions.
- get_risk_limit(category, symbol) - Get risk limit tiers: Retrieve all risk-limit tiers (max notional, MMR, IMR, max leverage) for a perpetual contract. Critical for position sizing.

Note: This tool executes a backtest simulation, it does not interact with the live Bybit API for trading.
Invokes the `run_strategy` function from `backtest.py`.

Args:
    start_time: Start time for the backtest period (millisecond timestamp).
    end_time: End time for the backtest period (millisecond timestamp).
    strategy_vars: A dictionary containing the strategy definition.
                   Refer to the `run_strategy` function in `backtest.py` for the expected structure.
                   This includes initial balance, indicator settings, buy/sell conditions, and position settings.

Returns:
    Dict: The results of the backtest, including performance metrics and trade history.
             Returns an error dictionary if the backtest fails.

User message: {message}
"""


def main():
    try:
        logger.info("MCP server starting...")
        print("MCP server starting...", file=sys.stderr)

        # BEZPIECZENSTWO: NIE logujemy kluczy API

        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(e)
        print(f"Server execution failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()