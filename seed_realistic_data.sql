-- Seed Realistic Politician Trading Data
-- Creates realistic cyclical trading patterns for testing ML models

-- 1. Create politicians
INSERT INTO politicians (id, name, chamber, party, state, bioguide_id) VALUES
(gen_random_uuid(), 'Nancy Pelosi', 'house', 'Democratic', 'CA', 'P000197'),
(gen_random_uuid(), 'Paul Pelosi', 'house', 'Democratic', 'CA', 'P000197S'),  -- Spouse
(gen_random_uuid(), 'Dan Crenshaw', 'house', 'Republican', 'TX', 'C001120'),
(gen_random_uuid(), 'Josh Gottheimer', 'house', 'Democratic', 'NJ', 'G000583');

-- Store politician IDs for use in trades
DO $$
DECLARE
    pelosi_id UUID;
    paul_id UUID;
    crenshaw_id UUID;
    gottheimer_id UUID;
    trade_date DATE;
    disc_date DATE;
    day_num INT := 0;
    cycle_phase FLOAT;
    trade_prob FLOAT;
BEGIN
    -- Get politician IDs
    SELECT id INTO pelosi_id FROM politicians WHERE name = 'Nancy Pelosi';
    SELECT id INTO paul_id FROM politicians WHERE name = 'Paul Pelosi';
    SELECT id INTO crenshaw_id FROM politicians WHERE name = 'Dan Crenshaw';
    SELECT id INTO gottheimer_id FROM politicians WHERE name = 'Josh Gottheimer';

    -- Generate trades from 2022-01-01 to 2024-11-14 (1050 days)
    FOR i IN 0..1049 LOOP
        trade_date := '2022-01-01'::DATE + i;

        -- Skip weekends
        IF EXTRACT(DOW FROM trade_date) NOT IN (0, 6) THEN
            day_num := day_num + 1;

            -- Nancy Pelosi - 21-day cycle, focused on NVDA/MSFT/AAPL
            cycle_phase := (day_num % 21)::FLOAT / 21.0;
            IF (random() < 0.12 * (1 + sin(2 * pi() * cycle_phase))) THEN
                disc_date := trade_date + INTERVAL '30 days';
                INSERT INTO trades (id, politician_id, ticker, transaction_type, amount_min, amount_max, transaction_date, disclosure_date)
                VALUES (gen_random_uuid(), pelosi_id,
                    (ARRAY['NVDA', 'MSFT', 'AAPL'])[floor(random() * 3 + 1)],
                    (CASE WHEN random() < 0.7 THEN 'buy' ELSE 'sell' END),
                    50000, 100000, trade_date, disc_date);
            END IF;

            -- Paul Pelosi - 28-day cycle, more frequent
            cycle_phase := (day_num % 28)::FLOAT / 28.0;
            IF (random() < 0.18 * (1 + 1.5 * sin(2 * pi() * cycle_phase))) THEN
                disc_date := trade_date + INTERVAL '35 days';
                INSERT INTO trades (id, politician_id, ticker, transaction_type, amount_min, amount_max, transaction_date, disclosure_date)
                VALUES (gen_random_uuid(), paul_id,
                    (ARRAY['NVDA', 'TSLA', 'GOOGL', 'META'])[floor(random() * 4 + 1)],
                    (CASE WHEN random() < 0.65 THEN 'buy' ELSE 'sell' END),
                    100000, 500000, trade_date, disc_date);
            END IF;

            -- Dan Crenshaw - 60-day cycle, less frequent
            cycle_phase := (day_num % 60)::FLOAT / 60.0;
            IF (random() < 0.06 * (1 + sin(2 * pi() * cycle_phase))) THEN
                disc_date := trade_date + INTERVAL '25 days';
                INSERT INTO trades (id, politician_id, ticker, transaction_type, amount_min, amount_max, transaction_date, disclosure_date)
                VALUES (gen_random_uuid(), crenshaw_id,
                    (ARRAY['SPY', 'MSFT', 'AAPL'])[floor(random() * 3 + 1)],
                    (CASE WHEN random() < 0.6 THEN 'buy' ELSE 'sell' END),
                    15000, 50000, trade_date, disc_date);
            END IF;

            -- Josh Gottheimer - 45-day cycle
            cycle_phase := (day_num % 45)::FLOAT / 45.0;
            IF (random() < 0.08 * (1 + sin(2 * pi() * cycle_phase))) THEN
                disc_date := trade_date + INTERVAL '40 days';
                INSERT INTO trades (id, politician_id, ticker, transaction_type, amount_min, amount_max, transaction_date, disclosure_date)
                VALUES (gen_random_uuid(), gottheimer_id,
                    (ARRAY['META', 'GOOGL', 'MSFT', 'AAPL'])[floor(random() * 4 + 1)],
                    (CASE WHEN random() < 0.6 THEN 'buy' ELSE 'sell' END),
                    25000, 75000, trade_date, disc_date);
            END IF;
        END IF;

        -- Progress indicator every 100 days
        IF i % 100 = 0 THEN
            RAISE NOTICE 'Generated trades through day %', i;
        END IF;
    END LOOP;
END $$;

-- Show summary
SELECT 'Summary Statistics:' AS info;
SELECT p.name, COUNT(t.id) AS trade_count
FROM politicians p
LEFT JOIN trades t ON p.id = t.politician_id
GROUP BY p.name
ORDER BY trade_count DESC;

SELECT ticker, COUNT(*) AS trade_count
FROM trades
GROUP BY ticker
ORDER BY trade_count DESC;

SELECT COUNT(*) AS total_trades FROM trades;
