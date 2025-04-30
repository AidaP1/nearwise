from app import app, db
import logging
from sqlalchemy import inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        with app.app_context():
            # Check if tables already exist
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                logger.info("No existing tables found. Creating database tables...")
                db.create_all()
                logger.info("Database tables created successfully!")
            else:
                logger.info("Tables already exist in the database.")
                
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == '__main__':
    init_db() 