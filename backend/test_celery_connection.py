"""
Quick test to check if Celery worker is running and can process tasks
"""
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.tasks.celery import celery
    
    # Create a simple test task
    @celery.task
    def test_task():
        return "Celery is working!"
    
    print("Testing Celery connection...")
    print("Sending test task...")
    
    # Send task
    result = test_task.delay()
    
    # Wait for result (with timeout)
    try:
        task_result = result.get(timeout=5)
        print(f"✅ Celery is RUNNING and processing tasks!")
        print(f"   Task result: {task_result}")
    except Exception as e:
        print(f"❌ Celery worker is NOT responding")
        print(f"   Error: {e}")
        print("\nMake sure Celery worker is running:")
        print("  celery -A app.tasks.celery worker --loglevel=info")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("  1. Redis is not running")
    print("  2. Celery configuration issue")
    print("  3. Dependencies not installed")

