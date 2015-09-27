step("""
CREATE TABLE tracking_requests(
  id BIGSERIAL PRIMARY KEY NOT NULL,
  tracking_code VARCHAR(64) NOT NULL,
  chat_id BIGINT NOT NULL,
  value VARCHAR(256),
  last_update TIMESTAMP,
  requested_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE (chat_id, tracking_code)
);
""", """
DROP TABLE tracking_requests;
"""
    )
