# standard.py - AI-Enhanced Conservative Growth (2-5% Daily)
import random
import math
from datetime import datetime

class StandardBot:
    def __init__(self, capital, risk_mode="standard", **kwargs):
        self.capital = capital
        self.initial_capital = capital
        self.target_return = kwargs.get('target_return', 0.02)  # 2% minimum
        self.max_target_return = kwargs.get('max_target_return', 0.05)  # 5% maximum
        self.max_dd = kwargs.get('max_drawdown', 0.05)  # 5% max drawdown
        self.daily_profit = 0
        self.stop_loss = kwargs.get('stop_loss', 0.01)  # 1% stop loss
        self.max_risk_per_trade = kwargs.get('max_risk', 0.03)  # 3% max risk
        self.trades_today = 0
        self.max_trades_daily = kwargs.get('max_daily_trades', 12)
        
        # Tighter risk controls
        self.emergency_stop_dd = 0.045  # Emergency stop at 4.5%
        self.size_reduction_dd = 0.035  # Start reducing size at 3.5%
        
        # AI enhancements
        self.use_ai_sizing = kwargs.get('adaptive_sizing', True)
        self.confidence_threshold = kwargs.get('confidence_threshold', 0.65)
        self.regime_adaptation = kwargs.get('regime_adaptation', True)
        
        # Performance tracking
        self.trade_history = []
        self.daily_pnl_history = []
        self.best_daily_return = 0
        self.worst_daily_return = 0
        self.peak_capital = capital
        
    def check_trade_conditions(self, signal):
        """Enhanced signal validation with AI"""
        score = signal.get('score', 0)
        volatility = signal.get('volatility', 0)
        trend = signal.get('trend', 0)
        support_resistance = signal.get('support_resistance', 0)
        ai_confidence = signal.get('ai_confidence', 0.5)
        regime = signal.get('regime', 'unknown')
        
        # Base conditions
        score_ok = score > 0.6
        vol_ok = 0.015 < volatility < 0.12  # Conservative volatility range
        trend_ok = abs(trend) > 0.35
        sr_ok = support_resistance > 0.5
        confidence_ok = ai_confidence >= self.confidence_threshold
        
        # Regime-specific adjustments
        if self.regime_adaptation:
            regime_requirements = {
                'trending_bull': {'min_score': 0.55, 'min_trend': 0.3},
                'trending_bear': {'min_score': 0.65, 'min_trend': 0.4},
                'sideways': {'min_score': 0.75, 'min_trend': 0.5},
                'high_volatility': {'min_score': 0.8, 'min_trend': 0.6},
                'low_volatility': {'min_score': 0.5, 'min_trend': 0.25}
            }
            
            regime_req = regime_requirements.get(regime, {'min_score': 0.6, 'min_trend': 0.35})
            score_ok = score > regime_req['min_score']
            trend_ok = abs(trend) > regime_req['min_trend']
        
        # Additional filters for conservative approach
        volume_ok = signal.get('volume_ratio', 1.0) > 0.8
        spread_ok = signal.get('spread', 0.001) < 0.005
        
        return all([score_ok, vol_ok, trend_ok, sr_ok, confidence_ok, volume_ok, spread_ok])
    
    def calculate_position_size(self, signal):
        """Advanced position sizing with Kelly Criterion and AI"""
        if self.use_ai_sizing and 'position_size' in signal:
            base_size = signal['position_size'] * self.capital
        else:
            # Kelly Criterion approach
            win_rate = signal.get('win_probability', 0.65)
            avg_win = signal.get('avg_win', 0.025)
            avg_loss = self.stop_loss
            
            # Kelly fraction
            kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly = max(0.01, min(kelly, self.max_risk_per_trade))
            
            base_size = self.capital * kelly
        
        # Conservative adjustments
        confidence = signal.get('ai_confidence', 0.5)
        confidence_mult = 0.5 + (confidence * 0.5)  # 50-100% based on confidence
        
        # Daily target achievement check
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        if daily_return >= self.target_return * 0.8:  # 80% of target reached
            daily_mult = 0.5  # Cut size in half
        elif daily_return >= self.target_return * 0.6:  # 60% of target
            daily_mult = 0.7
        else:
            daily_mult = 1.0
        
        # Drawdown protection
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        dd_mult = max(0.5, 1 - (current_dd * 2))
        
        # Peak distance protection
        peak_distance = (self.peak_capital - self.capital) / self.peak_capital if self.peak_capital > 0 else 0
        peak_mult = max(0.6, 1 - peak_distance)
        
        # Size reduction factor for approaching drawdown limit
        if current_dd > self.size_reduction_dd:
            size_reduction_factor = 0.6  # Reduce size by 40%
        else:
            size_reduction_factor = 1.0
        
        final_size = base_size * confidence_mult * dd_mult * peak_mult * size_reduction_factor
        
        # Tighter conservative bounds for StandardBot
        final_size = min(final_size, self.capital * 0.04)  # Max 4% per trade
        final_size = max(final_size, self.capital * 0.005) # Min 0.5% per trade
        
        return final_size
    
    def trade(self, signal):
        """Execute conservative trade with AI enhancements"""
        if self.trades_today >= self.max_trades_daily:
            return "⏸️ Daily trade limit reached"
            
        # Check daily target achievement
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        target_achieved = daily_return >= self.target_return
        
        if target_achieved and daily_return < self.max_target_return:
            return f"✅ Minimum target achieved: {daily_return:.1%} (continuing to max target: {self.max_target_return:.1%})"
        elif daily_return >= self.max_target_return:
            return f"🎯 Maximum daily target achieved: {daily_return:.1%}"
        
        # Tighter drawdown check
        current_dd = (self.initial_capital - self.capital) / self.initial_capital
        if current_dd > self.max_dd:
            return f"🛑 Drawdown limit exceeded: {current_dd:.1%} (Max: {self.max_dd:.1%})"
        
        # Signal validation
        if not self.check_trade_conditions(signal):
            return "🔍 Skipped: Conservative filters not met"
        
        # Position sizing
        position_size = self.calculate_position_size(signal)
        
        # Trade execution with conservative probabilities
        confidence = signal.get('ai_confidence', 0.5)
        momentum = signal.get('momentum', 0.5)
        regime = signal.get('regime', 'unknown')
        
        # Conservative success probability (higher baseline)
        base_success_prob = 0.55 + (confidence * 0.25)  # 55-80% range
        
        # Regime adjustments for conservative strategy
        regime_adjustments = {
            'trending_bull': 1.1,
            'trending_bear': 1.05,
            'sideways': 0.95,
            'high_volatility': 0.85,
            'low_volatility': 1.15
        }
        
        success_prob = base_success_prob * regime_adjustments.get(regime, 1.0)
        success_prob = min(0.85, max(0.50, success_prob))  # Conservative bounds
        
        # Execute trade
        if random.random() < success_prob:
            # Winning trade - conservative profit range
            base_profit_pct = random.uniform(0.015, 0.035)
            
            # Confidence and regime bonuses (smaller than aggressive strategies)
            confidence_bonus = 1 + ((confidence - 0.5) * 0.2)
            
            regime_profit_bonus = {
                'trending_bull': 1.2,
                'trending_bear': 1.1,
                'sideways': 0.9,
                'high_volatility': 1.1,
                'low_volatility': 1.0
            }
            
            final_profit_pct = base_profit_pct * confidence_bonus * regime_profit_bonus.get(regime, 1.0)
            final_profit_pct = min(0.045, final_profit_pct)  # Cap at 4.5%
            
            profit = position_size * final_profit_pct
            self.capital += profit
            self.daily_profit += profit
            
            # Update tracking
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
            
            self.trades_today += 1
            
            # Log trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'WIN',
                'size': position_size,
                'profit': profit,
                'profit_pct': final_profit_pct,
                'confidence': confidence,
                'regime': regime
            }
            self.trade_history.append(trade_record)
            
            return f"✅ Standard WIN | +${profit:.2f} ({final_profit_pct:.1%}) | Capital: ${self.capital:.2f} | Daily: {(self.daily_profit/self.capital):.1%}"
            
        else:
            # Losing trade - conservative stop loss
            base_loss_pct = self.stop_loss
            
            # Regime-adjusted stop loss (tighter in volatile markets)
            regime_loss_adj = {
                'trending_bull': 0.9,
                'trending_bear': 1.0,
                'sideways': 1.1,
                'high_volatility': 1.3,
                'low_volatility': 0.8
            }
            
            adjusted_loss_pct = base_loss_pct * regime_loss_adj.get(regime, 1.0)
            adjusted_loss_pct = min(0.025, adjusted_loss_pct)  # Cap loss at 2.5%
            
            loss = position_size * adjusted_loss_pct
            self.capital -= loss
            self.daily_profit -= loss
            self.trades_today += 1
            
            # Log trade
            trade_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'LOSS',
                'size': position_size,
                'loss': loss,
                'loss_pct': adjusted_loss_pct,
                'confidence': confidence,
                'regime': regime
            }
            self.trade_history.append(trade_record)
            
            return f"❌ Standard LOSS | -${loss:.2f} ({adjusted_loss_pct:.1%}) | Capital: ${self.capital:.2f} | Daily: {(self.daily_profit/self.capital):.1%}"
    
    def reset_daily_stats(self):
        """Reset daily tracking and update history"""
        if self.capital > 0:
            daily_return = self.daily_profit / self.capital
            self.daily_pnl_history.append({
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'return': daily_return,
                'profit': self.daily_profit,
                'trades': self.trades_today
            })
            
            # Update best/worst
            self.best_daily_return = max(self.best_daily_return, daily_return)
            self.worst_daily_return = min(self.worst_daily_return, daily_return)
        
        self.daily_profit = 0
        self.trades_today = 0
    
    def get_status(self):
        """Comprehensive status for conservative strategy"""
        current_dd = (self.initial_capital - self.capital) / self.initial_capital if self.initial_capital > 0 else 0
        total_return = (self.capital - self.initial_capital) / self.initial_capital if self.initial_capital > 0 else 0
        daily_return = self.daily_profit / self.capital if self.capital > 0 else 0
        
        # Calculate win rate
        recent_trades = self.trade_history[-30:] if len(self.trade_history) >= 30 else self.trade_history
        wins = len([t for t in recent_trades if t['type'] == 'WIN'])
        win_rate = wins / len(recent_trades) if recent_trades else 0
        
        # Calculate average daily return
        avg_daily_return = sum(d['return'] for d in self.daily_pnl_history) / len(self.daily_pnl_history) if self.daily_pnl_history else 0
        
        return {
            "strategy": "StandardBot",
            "capital": self.capital,
            "initial_capital": self.initial_capital,
            "total_return": f"{total_return:.1%}",
            "daily_return": f"{daily_return:.1%}",
            "daily_min_target": f"{self.target_return:.1%}",
            "daily_max_target": f"{self.max_target_return:.1%}",
            "target_progress": f"{(daily_return/self.target_return)*100:.0f}%" if self.target_return > 0 else "0%",
            "drawdown": f"{current_dd:.1%}",
            "trades_today": self.trades_today,
            "total_trades": len(self.trade_history),
            "win_rate": f"{win_rate:.1%}",
            "avg_daily_return": f"{avg_daily_return:.1%}",
            "best_daily": f"{self.best_daily_return:.1%}",
            "worst_daily": f"{self.worst_daily_return:.1%}",
            "peak_capital": self.peak_capital,
            "ai_enhanced": True,
            "risk_level": "conservative",
            "timestamp": datetime.utcnow().isoformat()
        }
