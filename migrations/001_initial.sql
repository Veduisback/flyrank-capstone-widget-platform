CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS widgets (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    widget_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    fields JSONB NOT NULL,
    button_text TEXT NOT NULL DEFAULT 'Submit',
    display_options JSONB NOT NULL DEFAULT '{}'::jsonb,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY,
    widget_id UUID NOT NULL REFERENCES widgets(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    ip_address INET,
    country TEXT,
    city TEXT,
    geo_provider TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    idempotency_key TEXT
);

CREATE TABLE IF NOT EXISTS notification_jobs (
    id UUID PRIMARY KEY,
    submission_id UUID NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
    attempts INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_submission_idempotency
ON submissions(widget_id, idempotency_key)
WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_widgets_tenant
ON widgets(tenant_id);

CREATE INDEX IF NOT EXISTS idx_submissions_tenant
ON submissions(tenant_id);

CREATE INDEX IF NOT EXISTS idx_submissions_widget
ON submissions(widget_id);

CREATE INDEX IF NOT EXISTS idx_submissions_created
ON submissions(created_at);

CREATE INDEX IF NOT EXISTS idx_jobs_status
ON notification_jobs(status, created_at);