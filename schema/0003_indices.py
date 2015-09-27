step("""
CREATE INDEX idx_tracking_requests_worker ON tracking_requests (requested_at, last_update, value);
""", """
DROP INDEX idx_tracking_requests_worker;
"""
    )
