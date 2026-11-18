CREATE UNIQUE INDEX IF NOT EXISTS versioned_resources_index on versioned_resources(resource_id, storage_id, version);
