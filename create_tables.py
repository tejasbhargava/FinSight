from backend.db.database import engine, Base
from backend.db.model import User, ChatSession, Message, Report



def create_all_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created:")
    print("- users")
    print("- chat_sessions")
    print("- messages")
    print("- reports")


if __name__ == "__main__":
    create_all_tables()