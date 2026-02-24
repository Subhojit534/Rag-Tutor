import asyncio
from app.routers.chat import get_conversations
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.id == 4).first()

async def test():
    print(f"Testing for User: {user.full_name} ({user.id}) Role: {user.role}")
    try:
        results = await get_conversations(db=db, current_user=user)
        print("Results:", results)
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
