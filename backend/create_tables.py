from database import Base, engine
from models import Document

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")