-- Initial development schema. Use versioned migrations before production rollout.
CREATE TABLE IF NOT EXISTS prices (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    crop TEXT NOT NULL,
    market TEXT NOT NULL,
    price DOUBLE PRECISION NOT NULL CHECK (price > 0 AND price < 'Infinity'::float8),
    unit TEXT NOT NULL DEFAULT 'kg',
    currency TEXT NOT NULL DEFAULT 'RWF',
    reported_on TEXT NOT NULL DEFAULT ''
);
