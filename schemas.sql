-- tags///////////////////
CREATE TABLE IF NOT EXISTS tags (id SERIAL, name TEXT, content TEXT, owner_id BIGINT, uses INTEGER DEFAULT (0), location_id BIGINT, 
created_at TIMESTAMP DEFAULT (now() at time zone 'utc'), PRIMARY KEY (id));
CREATE INDEX IF NOT EXISTS tags_location_id_idx ON tags (location_id);
CREATE INDEX IF NOT EXISTS tags_name_trgm_idx ON tags USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tags_name_lower_idx ON tags (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tags_uniq_idx ON tags (LOWER(name), location_id);

CREATE TABLE IF NOT EXISTS tag_lookup (id SERIAL, name TEXT, location_id BIGINT, owner_id BIGINT, created_at TIMESTAMP DEFAULT (now() at time zone 'utc'), tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE ON UPDATE NO ACTION, PRIMARY KEY (id));
CREATE INDEX IF NOT EXISTS tag_lookup_name_idx ON tag_lookup (name);
CREATE INDEX IF NOT EXISTS tag_lookup_location_id_idx ON tag_lookup (location_id);
CREATE INDEX IF NOT EXISTS tag_lookup_name_trgm_idx ON tag_lookup USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS tag_lookup_name_lower_idx ON tag_lookup (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS tag_lookup_uniq_idx ON tag_lookup (LOWER(name), location_id);