BEGIN;

CREATE SCHEMA IF NOT EXISTS messages;

CREATE TABLE IF NOT EXISTS messages.chat_messages (
    id UUID PRIMARY KEY,
    session_id UUID,
    student_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'assistant')),
    source TEXT CHECK (source IN ('chat', 'help_button')),
    parent_message_id UUID REFERENCES messages.chat_messages(id) ON DELETE SET NULL,
    message_text TEXT NOT NULL DEFAULT '',
    feedback_classes TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
    feedback_thumb TEXT CHECK (feedback_thumb IN ('up', 'down')),
    feedback_comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_student_created
    ON messages.chat_messages (student_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created
    ON messages.chat_messages (session_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_parent
    ON messages.chat_messages (parent_message_id);

COMMIT;
