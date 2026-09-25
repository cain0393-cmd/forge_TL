import uuid
from enum import Enum
from typing import List, Dict, Optional, Callable
import pandas as pd
from datetime import datetime

class OrderType(Enum):
    MARKET = 1
    LIMIT = 2

class OrderSide(Enum):
    BUY = 1
    SELL = 2

class OrderStatus(Enum):
    PENDING = 1
    FILLED = 2
    CANCELLED = 4
    REJECTED = 5

class Order:
    def __init__(self, symbol: str, side: OrderSide, quantity: int, order_type: OrderType, created_at: pd.Timestamp, limit_price: Optional[float] = None, eligible_at: Optional[pd.Timestamp] = None):
        self.order_id = "" # Assigned by engine
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.created_at = created_at
        self.limit_price = limit_price
        self.eligible_at = eligible_at
        self.status = OrderStatus.PENDING

class Trade:
    """Represents a completed round-trip trade."""
    def __init__(self, symbol: str, entry_timestamp: pd.Timestamp, entry_price: float, entry_quantity: int, exit_timestamp: pd.Timestamp, exit_price: float, entry_cost: float, exit_cost: float):
        self.trade_id = "" # Assigned by engine
        self.symbol = symbol
        self.entry_timestamp = entry_timestamp
        self.entry_price = entry_price
        self.entry_quantity = entry_quantity
        self.exit_timestamp = exit_timestamp
        self.exit_price = exit_price
        self.entry_cost = entry_cost
        self.exit_cost = exit_cost
        self.transaction_cost = entry_cost + exit_cost
        
        gross_entry = self.entry_price * self.entry_quantity
        gross_exit = self.exit_price * self.entry_quantity
        
        self.gross_pnl = gross_exit - gross_entry
        self.net_pnl = self.gross_pnl - self.transaction_cost
        self.return_pct = self.net_pnl / gross_entry if gross_entry > 0 else 0.0

class Position:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity: int = 0
        self.average_entry_price: float = 0.0
        self.market_value: float = 0.0
        self.unrealized_pnl: float = 0.0
        self.gross_realized_pnl: float = 0.0
        self.entry_timestamp: Optional[pd.Timestamp] = None
        self.total_entry_cost: float = 0.0
        
    def add(self, quantity: int, price: float, timestamp: pd.Timestamp, cost: float):
        if self.quantity == 0:
            self.entry_timestamp = timestamp
        total_cost = (self.quantity * self.average_entry_price) + (quantity * price)
        self.quantity += quantity
        self.average_entry_price = total_cost / self.quantity if self.quantity > 0 else 0.0
        self.total_entry_cost += cost
        
    def remove(self, quantity: int, exit_price: float) -> (float, float):
        """Returns (gross_realized_pnl, pro_rata_entry_cost)"""
        pro_rata_cost = (quantity / self.quantity) * self.total_entry_cost if self.quantity > 0 else 0.0
        gross_pnl = (exit_price - self.average_entry_price) * quantity
        self.gross_realized_pnl += gross_pnl
        
        self.quantity -= quantity
        self.total_entry_cost -= pro_rata_cost
        if self.quantity == 0:
            self.average_entry_price = 0.0
            self.total_entry_cost = 0.0
            
        return gross_pnl, pro_rata_cost
        
    def update_valuation(self, current_price: float):
        self.market_value = self.quantity * current_price
        self.unrealized_pnl = self.market_value - (self.quantity * self.average_entry_price)

class TransactionCostModel:
    def __init__(self, brokerage_pct=0.0, stt_pct=0.0, exchange_pct=0.0, sebi_pct=0.0, stamp_pct=0.0, gst_pct=0.0, dp_charges=0.0):
        self.brokerage_pct = brokerage_pct
        self.stt_pct = stt_pct
        self.exchange_pct = exchange_pct
        self.sebi_pct = sebi_pct
        self.stamp_pct = stamp_pct
        self.gst_pct = gst_pct
        self.dp_charges = dp_charges
        
    def calculate(self, side: OrderSide, price: float, quantity: int) -> float:
        value = price * quantity
        brokerage = value * self.brokerage_pct
        stt = value * self.stt_pct if side == OrderSide.SELL else 0.0 # simplified, usually STT on both for delivery
        exchange = value * self.exchange_pct
        sebi = value * self.sebi_pct
        stamp = value * self.stamp_pct if side == OrderSide.BUY else 0.0
        gst = (brokerage + exchange + sebi) * self.gst_pct
        dp = self.dp_charges if side == OrderSide.SELL else 0.0
        return brokerage + stt + exchange + sebi + stamp + gst + dp

class SlippageModel:
    def __init__(self, slippage_pct: float = 0.0):
        self.slippage_pct = slippage_pct
        
    def apply(self, side: OrderSide, price: float) -> float:
        if side == OrderSide.BUY:
            return price * (1.0 + self.slippage_pct)
        else:
            return price * (1.0 - self.slippage_pct)

class BacktestPortfolio:
    def __init__(self, initial_capital: float):
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.equity = initial_capital
        
    def update_valuation(self, current_prices: Dict[str, float]):
        market_value = 0.0
        for symbol, pos in list(self.positions.items()):
            if symbol in current_prices:
                pos.update_valuation(current_prices[symbol])
            market_value += pos.market_value
            if pos.quantity == 0:
                del self.positions[symbol]
        self.equity = self.cash + market_value

class Strategy:
    def on_bar(self, timestamp: pd.Timestamp, bars: Dict[str, dict], engine: 'BacktestEngine'):
        pass

class BacktestEngine:
    """
    Partial fills are unsupported in Task 4.
    Current order execution is all-or-nothing.
    Partial-fill modeling is reserved for a future execution-layer task.
    """
    def __init__(self, df: pd.DataFrame, initial_capital: float = 50000.0, 
                 cost_model: TransactionCostModel = None, slippage_model: SlippageModel = None):
        self.df = df
        self.portfolio = BacktestPortfolio(initial_capital)
        self.cost_model = cost_model or TransactionCostModel()
        self.slippage_model = slippage_model or SlippageModel()
        self.strategy: Optional[Strategy] = None
        
        self.pending_orders: List[Order] = []
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.equity_curve: List[dict] = []
        
        self.order_counter = 0
        self.trade_counter = 0
        
        # Fast chronological iteration
        if not self.df.empty:
            self.df = self.df.sort_values(by=['timestamp', 'symbol'])
            
        self._current_timestamp = None
        
    def set_strategy(self, strategy: Strategy):
        self.strategy = strategy
        
    def submit_order(self, order: Order):
        self.order_counter += 1
        order.order_id = f"ORDER-{self.order_counter:06d}"
        
        # Determine explicit eligibility
        if order.eligible_at is None:
            order.eligible_at = order.created_at + pd.Timedelta(microseconds=1)
            
        # Reject invalid eligibility (same-bar or backwards)
        if order.eligible_at <= order.created_at:
            order.status = OrderStatus.REJECTED
            self.orders.append(order)
            return
            
        self.pending_orders.append(order)
        self.orders.append(order)
        
    def _simulate_fill(self, order: Order, bar: dict) -> (bool, float):
        fill_price = 0.0
        if order.order_type == OrderType.MARKET:
            fill_price = bar['open']
            return True, fill_price
            
        elif order.order_type == OrderType.LIMIT:
            L = order.limit_price
            if order.side == OrderSide.BUY:
                if bar['open'] <= L:
                    return True, bar['open']
                elif bar['low'] <= L:
                    return True, L
            elif order.side == OrderSide.SELL:
                if bar['open'] >= L:
                    return True, bar['open']
                elif bar['high'] >= L:
                    return True, L
        return False, 0.0
        
    def run(self) -> dict:
        import time
        t0 = time.monotonic()
        
        if self.df.empty:
            return self._generate_report(0.0)
            
        # Group by timestamp to process chronologically
        grouped = self.df.groupby('timestamp')
        
        for ts, group in grouped:
            self._current_timestamp = ts
            
            # Dictionary of symbol -> bar dict for quick lookup
            # Use itertuples for faster iteration than iterrows
            bars = {}
            for row in group.itertuples(index=False):
                bars[row.symbol] = {
                    'timestamp': row.timestamp,
                    'symbol': row.symbol,
                    'open': row.open,
                    'high': row.high,
                    'low': row.low,
                    'close': row.close,
                    'volume': row.volume
                }
            
            # 1. Process pending orders against new bars
            still_pending = []
            for order in self.pending_orders:
                if order.status != OrderStatus.PENDING:
                    continue
                    
                # Look-ahead protection: explicitly check eligible_at
                if ts < order.eligible_at:
                    still_pending.append(order)
                    continue
                    
                if order.symbol in bars:
                    bar = bars[order.symbol]
                    filled, raw_fill_price = self._simulate_fill(order, bar)
                    
                    if filled:
                        fill_price = self.slippage_model.apply(order.side, raw_fill_price)
                        cost = self.cost_model.calculate(order.side, fill_price, order.quantity)
                        
                        gross_value = fill_price * order.quantity
                        
                        if order.side == OrderSide.BUY:
                            if self.portfolio.cash >= (gross_value + cost):
                                # Fill BUY
                                self.portfolio.cash -= (gross_value + cost)
                                if order.symbol not in self.portfolio.positions:
                                    self.portfolio.positions[order.symbol] = Position(order.symbol)
                                self.portfolio.positions[order.symbol].add(order.quantity, fill_price, ts, cost)
                                order.status = OrderStatus.FILLED
                            else:
                                order.status = OrderStatus.REJECTED
                        elif order.side == OrderSide.SELL:
                            pos = self.portfolio.positions.get(order.symbol)
                            if pos and pos.quantity >= order.quantity:
                                # Track trade for ledger
                                entry_price = pos.average_entry_price
                                entry_timestamp = pos.entry_timestamp
                                entry_quantity = order.quantity # FIFO assumed for now, matching exact
                                
                                self.portfolio.cash += (gross_value - cost)
                                
                                gross_pnl, entry_cost = pos.remove(order.quantity, fill_price)
                                
                                # Log trade
                                self.trade_counter += 1
                                tr = Trade(
                                    symbol=order.symbol,
                                    entry_timestamp=entry_timestamp,
                                    entry_price=entry_price,
                                    entry_quantity=entry_quantity,
                                    exit_timestamp=ts,
                                    exit_price=fill_price,
                                    entry_cost=entry_cost,
                                    exit_cost=cost
                                )
                                tr.trade_id = f"TRADE-{self.trade_counter:06d}"
                                self.trades.append(tr)
                                
                                order.status = OrderStatus.FILLED
                            else:
                                order.status = OrderStatus.REJECTED
                    else:
                        still_pending.append(order)
                else:
                    still_pending.append(order)
            
            self.pending_orders = still_pending
            
            # 2. Update valuation using current close prices
            current_close_prices = {sym: b['close'] for sym, b in bars.items()}
            self.portfolio.update_valuation(current_close_prices)
            
            # 3. Log equity curve
            self.equity_curve.append({
                'timestamp': ts,
                'cash': self.portfolio.cash,
                'gross_position_value': self.portfolio.equity - self.portfolio.cash,
                'equity': self.portfolio.equity
            })
            
            # 4. Provide bar to Strategy (which can place new orders)
            if self.strategy:
                self.strategy.on_bar(ts, bars, self)
                
        t1 = time.monotonic()
        return self._generate_report(t1 - t0)
        
    def _generate_report(self, runtime_seconds: float) -> dict:
        import numpy as np
        
        equity_df = pd.DataFrame(self.equity_curve)
        
        sharpe = 0.0
        sortino = 0.0
        
        if not equity_df.empty:
            equity_df.set_index('timestamp', inplace=True)
            peak_equity = equity_df['equity'].cummax()
            drawdown = equity_df['equity'] - peak_equity
            drawdown_pct = (equity_df['equity'] / peak_equity) - 1.0
            max_drawdown = drawdown.min()
            max_drawdown_pct = drawdown_pct.min()
            final_equity = equity_df['equity'].iloc[-1]
            total_return = (final_equity / self.portfolio.initial_capital) - 1.0
            net_pnl = final_equity - self.portfolio.initial_capital
            
            # Metrics calculation
            returns = equity_df['equity'].pct_change().dropna()
            if not returns.empty:
                std_dev = returns.std()
                if std_dev > 0:
                    sharpe = np.sqrt(252) * returns.mean() / std_dev
                    
                downside = returns[returns < 0]
                if not downside.empty:
                    downside_std = downside.std() # Wait, downside deviation uses root mean square of negative returns
                    # More rigorous downside deviation: sqrt(mean(min(R, 0)^2))
                    downside_dev = np.sqrt((np.minimum(returns, 0)**2).mean())
                    if downside_dev > 0:
                        sortino = np.sqrt(252) * returns.mean() / downside_dev
                else:
                    # No downside
                    sortino = float('inf') if returns.mean() > 0 else 0.0
        else:
            max_drawdown = 0.0
            max_drawdown_pct = 0.0
            final_equity = self.portfolio.initial_capital
            total_return = 0.0
            net_pnl = 0.0
            
        winning_trades = [t for t in self.trades if t.net_pnl > 0]
        losing_trades = [t for t in self.trades if t.net_pnl <= 0]
        gross_profit = sum(t.net_pnl for t in winning_trades)
        gross_loss = sum(abs(t.net_pnl) for t in losing_trades)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        gross_realized_pnl = sum(t.gross_pnl for t in self.trades)
        net_realized_pnl = sum(t.net_pnl for t in self.trades)
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.portfolio.positions.values()) 
        
        metrics = {
            'final_equity': final_equity,
            'final_cash': self.portfolio.cash,
            'net_pnl': net_pnl,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'gross_realized_pnl': gross_realized_pnl,
            'net_realized_pnl': net_realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'number_of_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.trades) if self.trades else 0.0,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'runtime_seconds': runtime_seconds,
            'rows_processed': len(self.df),
            'rows_per_second': len(self.df) / runtime_seconds if runtime_seconds > 0 else 0.0
        }
        
        return {
            'equity_curve': equity_df,
            'trades': self.trades,
            'orders': self.orders,
            'metrics': metrics
        }
