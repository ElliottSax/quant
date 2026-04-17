---
title: 'Database Design for Trading Systems: Schema and Optimization'
slug: database-design-for-trading-systems
author: Dr. James Chen
category: Algo Trading
date: '2026-03-16'
quality_score: 90
seo_optimized: true
published_date: '2026-04-17'
last_updated: '2026-04-17'
---

# Database Design for Trading Systems: Schema and Optimization

**Author:** Dr. James Chen
**Category:** Algo Trading
**Date:** 2026-03-16

## Introduction

Effective database design is fundamental to high-performance trading systems. Trading systems generate high-frequency data writes, require sub-millisecond query performance for position tracking, and demand perfect data consistency for regulatory compliance. This guide covers designing databases optimized for trading workloads.

## Core Trading Database Schema

```sql
-- Create trading schema
CREATE SCHEMA trading;

-- Accounts table
CREATE TABLE trading.accounts (
    account_id BIGSERIAL PRIMARY KEY,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- 'cash', 'margin', 'futures'
    balance DECIMAL(18, 8) NOT NULL,
    buying_power DECIMAL(18, 8) NOT NULL,
    margin_used DECIMAL(18, 8) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounts_type ON trading.accounts(account_type);

-- Securities master data
CREATE TABLE trading.securities (
    security_id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255),
    security_type VARCHAR(50) NOT NULL, -- 'equity', 'option', 'future'
    exchange VARCHAR(20),
    currency VARCHAR(3),
    tick_size DECIMAL(18, 8),
    contract_multiplier INT DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_securities_symbol ON trading.securities(symbol);
CREATE INDEX idx_securities_type ON trading.securities(security_type);

-- Positions table (denormalized for query speed)
CREATE TABLE trading.positions (
    position_id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES trading.accounts(account_id),
    security_id BIGINT NOT NULL REFERENCES trading.securities(security_id),
    quantity INT NOT NULL,
    entry_price DECIMAL(18, 8) NOT NULL,
    current_price DECIMAL(18, 8),
    unrealized_pnl DECIMAL(18, 8),
    entry_date DATE NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_id, security_id)
);

CREATE INDEX idx_positions_account ON trading.positions(account_id);
CREATE INDEX idx_positions_security ON trading.positions(security_id);
CREATE INDEX idx_positions_updated ON trading.positions(last_updated);

-- Orders table (immutable event log)
CREATE TABLE trading.orders (
    order_id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES trading.accounts(account_id),
    security_id BIGINT NOT NULL REFERENCES trading.securities(security_id),
    order_type VARCHAR(50) NOT NULL, -- 'market', 'limit', 'stop'
    side VARCHAR(10) NOT NULL, -- 'buy', 'sell'
    quantity INT NOT NULL,
    limit_price DECIMAL(18, 8),
    stop_price DECIMAL(18, 8),
    status VARCHAR(50) NOT NULL, -- 'pending', 'filled', 'cancelled'
    submitted_at TIMESTAMP NOT NULL,
    filled_at TIMESTAMP,
    expiration_date DATE,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'partial', 'filled', 'cancelled', 'rejected'))
);

CREATE INDEX idx_orders_account ON trading.orders(account_id);
CREATE INDEX idx_orders_security ON trading.orders(security_id);
CREATE INDEX idx_orders_status ON trading.orders(status) WHERE status IN ('pending', 'partial');
CREATE INDEX idx_orders_submitted ON trading.orders(submitted_at DESC);

-- Fills table (granular execution records)
CREATE TABLE trading.fills (
    fill_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES trading.orders(order_id),
    fill_quantity INT NOT NULL,
    fill_price DECIMAL(18, 8) NOT NULL,
    commission DECIMAL(18, 8) NOT NULL,
    filled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    counterparty VARCHAR(255)
);

CREATE INDEX idx_fills_order ON trading.fills(order_id);
CREATE INDEX idx_fills_timestamp ON trading.fills(filled_at DESC);

-- Trades table (closed P&L tracking)
CREATE TABLE trading.trades (
    trade_id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES trading.accounts(account_id),
    security_id BIGINT NOT NULL REFERENCES trading.securities(security_id),
    entry_order_id BIGINT REFERENCES trading.orders(order_id),
    exit_order_id BIGINT REFERENCES trading.orders(order_id),
    quantity INT NOT NULL,
    entry_price DECIMAL(18, 8) NOT NULL,
    exit_price DECIMAL(18, 8) NOT NULL,
    realized_pnl DECIMAL(18, 8) NOT NULL,
    realized_pnl_pct DECIMAL(5, 4),
    entry_date DATE NOT NULL,
    exit_date DATE NOT NULL,
    duration_days INT
);

CREATE INDEX idx_trades_account ON trading.trades(account_id);
CREATE INDEX idx_trades_security ON trading.trades(security_id);
CREATE INDEX idx_trades_exit_date ON trading.trades(exit_date DESC);

-- Daily market data (OHLCV)
CREATE TABLE trading.market_data (
    market_data_id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES trading.securities(security_id),
    trade_date DATE NOT NULL,
    open_price DECIMAL(18, 8),
    high_price DECIMAL(18, 8),
    low_price DECIMAL(18, 8),
    close_price DECIMAL(18, 8) NOT NULL,
    volume BIGINT,
    UNIQUE(security_id, trade_date)
);

CREATE INDEX idx_market_data_security ON trading.market_data(security_id);
CREATE INDEX idx_market_data_date ON trading.market_data(trade_date DESC);

-- Tick data (high-frequency)
CREATE TABLE trading.tick_data (
    tick_id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES trading.securities(security_id),
    tick_timestamp TIMESTAMP NOT NULL,
    bid_price DECIMAL(18, 8),
    bid_size INT,
    ask_price DECIMAL(18, 8),
    ask_size INT,
    last_price DECIMAL(18, 8),
    last_size INT
);

CREATE INDEX idx_tick_data_security ON trading.tick_data(security_id);
CREATE INDEX idx_tick_data_timestamp ON trading.tick_data(tick_timestamp DESC);

-- Performance metrics
CREATE TABLE trading.performance_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL REFERENCES trading.accounts(account_id),
    metric_date DATE NOT NULL,
    daily_return DECIMAL(5, 4),
    cumulative_return DECIMAL(8, 4),
    sharpe_ratio DECIMAL(5, 3),
    max_drawdown DECIMAL(5, 4),
    total_trades INT,
    winning_trades INT,
    losing_trades INT,
    win_rate DECIMAL(3, 2),
    UNIQUE(account_id, metric_date)
);

CREATE INDEX idx_metrics_account ON trading.performance_metrics(account_id);
CREATE INDEX idx_metrics_date ON trading.performance_metrics(metric_date DESC);

-- Audit log for compliance
CREATE TABLE trading.audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    account_id BIGINT,
    changes JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_account ON trading.audit_log(account_id);
CREATE INDEX idx_audit_timestamp ON trading.audit_log(created_at DESC);
CREATE INDEX idx_audit_type ON trading.audit_log(event_type);
```

## Python ORM Implementation

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from decimal import Decimal

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'

    account_id = Column(Integer, primary_key=True)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)
    balance = Column(Float, nullable=False)
    buying_power = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    positions = relationship("Position", back_populates="account")
    orders = relationship("Order", back_populates="account")

class Security(Base):
    __tablename__ = 'securities'

    security_id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False)
    name = Column(String(255))
    security_type = Column(String(50), nullable=False)
    exchange = Column(String(20))

    positions = relationship("Position", back_populates="security")

class Position(Base):
    __tablename__ = 'positions'

    position_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    security_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float)

    account = relationship("Account", back_populates="positions")
    security = relationship("Security", back_populates="positions")

class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    account_id = Column(Integer, nullable=False)
    security_id = Column(Integer, nullable=False)
    order_type = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    limit_price = Column(Float)
    status = Column(String(50), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="orders")
    fills = relationship("Fill", back_populates="order")

class Fill(Base):
    __tablename__ = 'fills'

    fill_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    fill_quantity = Column(Integer, nullable=False)
    fill_price = Column(Float, nullable=False)
    commission = Column(Float)
    filled_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="fills")

class TradingDatabase:
    """Database abstraction layer for trading systems."""

    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_order(self, account_id: int, security_id: int,
                    order_type: str, side: str, quantity: int,
                    limit_price: float = None) -> Order:
        """Create new order."""
        session = self.Session()

        try:
            order = Order(
                account_id=account_id,
                security_id=security_id,
                order_type=order_type,
                side=side,
                quantity=quantity,
                limit_price=limit_price,
                status='pending'
            )

            session.add(order)
            session.commit()

            return order

        finally:
            session.close()

    def record_fill(self, order_id: int, fill_quantity: int,
                   fill_price: float, commission: float = 0.0) -> Fill:
        """Record order fill."""
        session = self.Session()

        try:
            fill = Fill(
                order_id=order_id,
                fill_quantity=fill_quantity,
                fill_price=fill_price,
                commission=commission
            )

            session.add(fill)

            # Update order status
            order = session.query(Order).get(order_id)
            if order:
                order.status = 'filled' if order.quantity == fill_quantity else 'partial'

            session.commit()

            return fill

        finally:
            session.close()

    def get_positions(self, account_id: int) -> list:
        """Get all positions for account."""
        session = self.Session()

        try:
            return session.query(Position).filter(
                Position.account_id == account_id
            ).all()

        finally:
            session.close()

    def get_account_performance(self, account_id: int) -> dict:
        """Get account performance metrics."""
        session = self.Session()

        try:
            account = session.query(Account).get(account_id)
            positions = session.query(Position).filter(
                Position.account_id == account_id
            ).all()

            total_pnl = sum(p.unrealized_pnl or 0 for p in positions)

            return {
                'account_id': account_id,
                'balance': account.balance,
                'positions': len(positions),
                'unrealized_pnl': total_pnl
            }

        finally:
            session.close()
```

## Optimization Strategies

### 1. Partitioning by Date
```sql
-- Partition large tables by date for performance
CREATE TABLE trading.orders_2024 PARTITION OF trading.orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 2. Materialized Views for Reporting
```sql
CREATE MATERIALIZED VIEW trading.daily_summary AS
SELECT
    account_id,
    DATE(submitted_at) as trade_date,
    COUNT(*) as total_orders,
    SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) as filled_orders,
    SUM(CASE WHEN side = 'buy' THEN quantity ELSE 0 END) as total_bought,
    SUM(CASE WHEN side = 'sell' THEN quantity ELSE 0 END) as total_sold
FROM trading.orders
GROUP BY account_id, DATE(submitted_at);

CREATE INDEX idx_daily_summary ON trading.daily_summary(account_id, trade_date);
```

### 3. Time-Series Optimization
Use specialized databases like TimescaleDB for tick data:
```sql
SELECT create_hypertable('trading.tick_data', 'tick_timestamp');
```

## Best Practices

1. **Denormalization**: Trade normalization for query speed
2. **Indexing Strategy**: Carefully index frequently filtered columns
3. **Partitioning**: Partition large tables by date
4. **Archival**: Archive old data to separate storage
5. **Connection Pooling**: Use connection pools for performance

## Conclusion

Proper database design is critical for trading system performance. The schema presented balances normalization, query performance, and compliance requirements for institutional-grade trading systems.
