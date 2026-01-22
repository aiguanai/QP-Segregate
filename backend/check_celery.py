"""
Script to check if Celery is running and show worker status
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.tasks.celery import celery
    
    # Try to inspect active workers
    inspect = celery.control.inspect()
    
    # Check active workers
    active_workers = inspect.active()
    if active_workers:
        print("✅ Celery is RUNNING")
        print(f"\nActive Workers: {len(active_workers)}")
        for worker_name, tasks in active_workers.items():
            print(f"  - {worker_name}: {len(tasks)} active task(s)")
            if tasks:
                for task in tasks:
                    print(f"    • {task.get('name', 'Unknown')} (ID: {task.get('id', 'N/A')})")
    else:
        print("❌ Celery is NOT RUNNING")
        print("\nNo active workers found.")
        print("\nTo start Celery, run:")
        print("  celery -A app.tasks.celery worker --loglevel=info")
    
    # Check registered workers
    registered = inspect.registered()
    if registered:
        print(f"\nRegistered Workers: {len(registered)}")
        for worker_name, tasks in registered.items():
            print(f"  - {worker_name}: {len(tasks)} registered task(s)")
    
    # Check stats
    stats = inspect.stats()
    if stats:
        print(f"\nWorker Statistics:")
        for worker_name, worker_stats in stats.items():
            print(f"  - {worker_name}:")
            print(f"    Pool: {worker_stats.get('pool', {}).get('implementation', 'N/A')}")
            print(f"    Processes: {worker_stats.get('pool', {}).get('processes', 'N/A')}")
            print(f"    Max concurrency: {worker_stats.get('pool', {}).get('max-concurrency', 'N/A')}")
    
except Exception as e:
    print(f"❌ Error checking Celery status: {e}")
    print("\nPossible issues:")
    print("  1. Celery worker is not running")
    print("  2. Redis is not running or not accessible")
    print("  3. Connection configuration issue")
    print("\nTo start Celery, run:")
    print("  celery -A app.tasks.celery worker --loglevel=info")

