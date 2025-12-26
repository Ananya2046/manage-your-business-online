-- Supabase Tables for RetailPulse AI

-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    shop_name VARCHAR(255) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    plan VARCHAR(50) DEFAULT 'Basic',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Purchases table
CREATE TABLE purchases (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    shop_name VARCHAR(255) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    items JSONB NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    processing_mode VARCHAR(20) DEFAULT 'ai',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory table
CREATE TABLE inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    shop_name VARCHAR(255) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 0,
    unit_price DECIMAL(10,2) DEFAULT 0,
    category VARCHAR(100),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, item_name)
);

-- AI Insights table
CREATE TABLE ai_insights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    shop_name VARCHAR(255) NOT NULL,
    sector VARCHAR(50) NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    insight_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_purchases_user_id ON purchases(user_id);
CREATE INDEX idx_purchases_created_at ON purchases(created_at DESC);
CREATE INDEX idx_inventory_user_id ON inventory(user_id);
CREATE INDEX idx_ai_insights_user_id ON ai_insights(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;

-- Create policies for secure access
CREATE POLICY "Users can view own data" ON users FOR ALL USING (auth.uid() = id);
CREATE POLICY "Users can view own purchases" ON purchases FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own inventory" ON inventory FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "Users can view own insights" ON ai_insights FOR ALL USING (auth.uid() = user_id);
