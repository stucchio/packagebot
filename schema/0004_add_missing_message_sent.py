step("""
ALTER TABLE tracking_requests
  ADD COLUMN sent_could_not_find BOOLEAN DEFAULT FALSE;
""", """
ALTER TABLE tracking_requests
  DROP COLUMN sent_could_not_find;
"""
    )
