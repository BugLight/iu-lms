from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from courses.settings import settings

engine = create_engine(settings.POSTGRES_URI, echo=True)
SessionLocal = sessionmaker(bind=engine)
