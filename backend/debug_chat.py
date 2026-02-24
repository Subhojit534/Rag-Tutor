from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()


def run_query(query_str, file_handle):
    file_handle.write(f"\n=== QUERY: {query_str} ===\n")
    try:
        results = db.execute(text(query_str)).fetchall()
        for r in results:
            file_handle.write(str(r) + "\n")
    except Exception as e:
        file_handle.write(f"Error: {e}\n")

with open("debug_result.txt", "w") as f:
    run_query("SELECT id, full_name, role, email FROM users", f)
    run_query("SELECT id, user_id, roll_number FROM student_profiles", f)
    run_query("SELECT id, user_id, employee_id FROM teacher_profiles", f)
    run_query("SELECT id, student_id, teacher_id FROM chat_conversations", f)
    run_query("SELECT id, conversation_id, sender_role, message FROM chat_messages WHERE conversation_id = 1", f)

db.close()
