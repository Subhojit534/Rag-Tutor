import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

queries = [
    "ALTER TABLE chat_messages DROP COLUMN file_url;",
    "ALTER TABLE chat_messages DROP COLUMN file_type;",
    "ALTER TABLE ai_chat_messages DROP COLUMN file_url;",
    "ALTER TABLE ai_chat_messages DROP COLUMN file_type;"
]

with engine.connect() as conn:
    for query in queries:
        try:
            conn.execute(text(query))
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Skipped {query} - Error: {e}")
    try:
        conn.commit()
    except Exception:
        pass
    print("Reversion complete!")
