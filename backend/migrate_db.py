import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

queries = [
    "ALTER TABLE chat_messages ADD COLUMN file_url VARCHAR(500) NULL;",
    "ALTER TABLE chat_messages ADD COLUMN file_type VARCHAR(50) NULL;",
    "ALTER TABLE ai_chat_messages ADD COLUMN file_url VARCHAR(500) NULL;",
    "ALTER TABLE ai_chat_messages ADD COLUMN file_type VARCHAR(50) NULL;"
]

with engine.connect() as conn:
    for query in queries:
        try:
            conn.execute(text(query))
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Skipped {query} - maybe already exists? Error: {e}")
    try:
        conn.commit()
    except Exception:
        pass
    print("Migration complete!")
