step("""
CREATE TABLE messages_viewed(
  update_id BIGINT NOT NULL PRIMARY KEY,
  last_update TIMESTAMP NOT NULL
);
""", """
DROP TABLE messages_viewed;
"""
    )
