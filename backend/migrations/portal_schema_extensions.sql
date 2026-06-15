-- Portal: market / promo pricing + requirement publish flags.
-- Applied automatically on app startup (see init_db.ensure_portal_schema_extensions).
-- Run manually only if needed (MySQL 8+):

-- ALTER TABLE service_type ADD COLUMN market_price DECIMAL(10,2) NULL AFTER price;
-- ALTER TABLE customer_requirement ADD COLUMN is_published INT NOT NULL DEFAULT 1 AFTER assigned_cleaner_id;
-- ALTER TABLE customer_requirement ADD COLUMN publish_time DATETIME NULL AFTER is_published;
