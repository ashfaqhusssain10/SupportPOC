-- Initialize database tables for Support-Led Ordering System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Incidences table (core entity)
CREATE TABLE IF NOT EXISTS incidences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    order_id VARCHAR(255),
    conversation_id VARCHAR(255) UNIQUE,
    
    -- Classification
    stage VARCHAR(20) NOT NULL CHECK (stage IN ('PRE_ORDER', 'POST_ORDER')),
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('IN_APP_CHAT', 'CALL', 'WHATSAPP')),
    trigger VARCHAR(20) NOT NULL CHECK (trigger IN ('USER_INITIATED', 'SYSTEM_INITIATED')),
    
    -- Context at creation
    app_screen VARCHAR(100),
    cart_value DECIMAL(10,2) DEFAULT 0,
    guest_count INTEGER,
    event_type VARCHAR(50),
    friction_score DECIMAL(5,2) DEFAULT 0,
    
    -- Resolution
    outcome VARCHAR(20) DEFAULT 'IN_PROGRESS' CHECK (outcome IN ('IN_PROGRESS', 'RESOLVED', 'DROPPED', 'CONVERTED')),
    issue_category VARCHAR(100),
    root_cause TEXT,
    resolution_type VARCHAR(100),
    order_impact VARCHAR(20) CHECK (order_impact IN ('PLACED', 'MODIFIED', 'LOST', 'NONE')),
    
    -- Metadata
    agent_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    time_to_resolve_seconds INTEGER
);

-- Incidence timeline (chat/action history)
CREATE TABLE IF NOT EXISTS incidence_timeline (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incidence_id UUID REFERENCES incidences(id) ON DELETE CASCADE,
    
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(20) NOT NULL CHECK (actor IN ('USER', 'AGENT', 'SYSTEM')),
    content TEXT,
    event_metadata JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Friction signals
CREATE TABLE IF NOT EXISTS friction_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    
    signal_type VARCHAR(50) NOT NULL,
    value DECIMAL(10,2),
    screen VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Daily analytics (pre-computed)
CREATE TABLE IF NOT EXISTS analytics_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE UNIQUE NOT NULL,
    
    total_orders INTEGER DEFAULT 0,
    orders_without_help INTEGER DEFAULT 0,
    orders_with_help INTEGER DEFAULT 0,
    
    total_incidences INTEGER DEFAULT 0,
    avg_time_to_resolve_seconds INTEGER DEFAULT 0,
    
    top_issue_categories JSONB,
    top_friction_screens JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_incidences_user_id ON incidences(user_id);
CREATE INDEX IF NOT EXISTS idx_incidences_created_at ON incidences(created_at);
CREATE INDEX IF NOT EXISTS idx_incidences_outcome ON incidences(outcome);
CREATE INDEX IF NOT EXISTS idx_incidences_conversation_id ON incidences(conversation_id);
CREATE INDEX IF NOT EXISTS idx_timeline_incidence_id ON incidence_timeline(incidence_id);
CREATE INDEX IF NOT EXISTS idx_friction_user_session ON friction_signals(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics_daily(date);
