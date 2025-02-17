from fastapi import FastAPI, HTTPException
import redis
from datetime import datetime

app = FastAPI()

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.get("/")
async def root():
    return {
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "user": "gerryjekova"
    }

@app.get("/redis-test")
async def test_redis():
    try:
        # Test Redis connection
        redis_client.ping()
        
        # Set a test value
        test_key = "test_timestamp"
        test_value = datetime.utcnow().isoformat()
        redis_client.set(test_key, test_value)
        
        # Get the value back
        retrieved_value = redis_client.get(test_key)
        
        return {
            "status": "success",
            "redis_connected": True,
            "test_value_set": test_value,
            "test_value_retrieved": retrieved_value
        }
    except redis.ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health_check():
    redis_status = "connected"
    try:
        redis_client.ping()
    except:
        redis_status = "disconnected"
    
    return {
        "status": "healthy",
        "redis_status": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }