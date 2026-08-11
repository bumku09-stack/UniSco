ALTER TABLE scholarship ADD COLUMN IF NOT EXISTS excluded_special_status TEXT[] NOT NULL DEFAULT '{}';
