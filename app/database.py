import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

Base = declarative_base()

IS_MONGODB = settings.DATABASE_URL.startswith("mongodb://") or settings.DATABASE_URL.startswith("mongodb+srv://")
mongo_client = None

if IS_MONGODB:
    try:
        import certifi
        import dns.resolver
        
        # Configure public fallback DNS for reliable MongoDB SRV resolution on Windows
        try:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
        except Exception:
            pass

        from pymongo import MongoClient
        from app.mongo_adapter import MongoSession
        
        mongo_client = MongoClient(
            settings.DATABASE_URL,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        # Test connection ping
        mongo_client.admin.command('ping')
        print("[Database] Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"[Database Warning] Could not connect to MongoDB Atlas ({e}).")
        print("[Database Tip] Ensure your current IP is whitelisted in MongoDB Atlas -> Network Access (allow 0.0.0.0/0 for anywhere).")
        print("[Database Fallback] Using local database engine so you can continue running smoothly.")
        IS_MONGODB = False
        mongo_client = None

if IS_MONGODB and mongo_client:
    engine = None
    SessionLocal = None

    def get_db():
        session = MongoSession(mongo_client, db_name="career_agentic_ai")
        try:
            yield session
        finally:
            session.close()
else:
    # Standard SQLite / PostgreSQL
    sqlite_url = f"sqlite:///{settings.UPLOAD_DIR}/../career_platform.db" if not settings.DATABASE_URL.startswith("sqlite") and not settings.DATABASE_URL.startswith("postgresql") else settings.DATABASE_URL
    connect_args = {"check_same_thread": False} if sqlite_url.startswith("sqlite") else {}

    engine = create_engine(sqlite_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
