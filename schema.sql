
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  image_path TEXT NOT NULL UNIQUE,
  question TEXT NOT NULL,
  gemini_answer TEXT,
  consensus_answer TEXT,
  debate_history TEXT,
  is_reviewed INTEGER NOT NULL DEFAULT 0,
  human_verdict TEXT,
  human_answer TEXT,
  human_analysis TEXT,
  reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
