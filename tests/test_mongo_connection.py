from app import create_app
from app.extensions import mongo
from app.utils.log import get_logger

logger = get_logger(__name__)

def test_mongo_connection():
    """
    Test MongoDB connection
    """
    app = create_app('development')
    with app.app_context():
        try:
            # Try to get server info to verify connection
            mongo.cx.server_info()
            logger.info("MongoDB connection successful")
            print("MongoDB connection successful")
            
            # List all collections
            collections = mongo.db.list_collection_names()
            logger.info(f"Available collections: {collections}")
            print(f"Available collections: {collections}")
            
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            print(f"MongoDB connection failed: {str(e)}")
            return False

if __name__ == "__main__":
    test_mongo_connection()
