CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY,
  dt TEXT NOT NULL,
  message TEXT NOT NULL,
  sender TEXT NOT NULL
);