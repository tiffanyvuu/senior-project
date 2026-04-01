BEGIN;

ALTER TABLE event_logs.parsed_events
    ADD COLUMN IF NOT EXISTS playground_data_json JSONB,
    ADD COLUMN IF NOT EXISTS source_log_id BIGINT,
    ADD COLUMN IF NOT EXISTS source_received_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS source_queue TEXT;

CREATE INDEX IF NOT EXISTS idx_parsed_events_source_log_id
    ON event_logs.parsed_events (source_log_id);

COMMIT;
