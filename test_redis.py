import redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_redis_connection():
    try:
        # Create Redis client
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Test connection
        response = redis_client.ping()
        print("Redis connection test:", "SUCCESS" if response else "FAILED")
        
        # Test basic operations
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        print("Redis test value:", value)
        
    except redis.ConnectionError as e:
        print("Failed to connect to Redis:", str(e))
    except Exception as e:
        print("Unexpected error:", str(e))

if __name__ == "__main__":
    test_redis_connection()