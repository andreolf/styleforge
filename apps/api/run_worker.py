#!/usr/bin/env python3
"""Worker runner script with macOS fork fix."""

import multiprocessing
import os
import sys

# Fix for macOS fork crash - MUST be set before importing anything else
if sys.platform == 'darwin':
    multiprocessing.set_start_method('spawn', force=True)
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

from redis import Redis
from rq import Worker, Queue

from app.config import get_settings


def main():
    settings = get_settings()
    
    # Connect to Redis
    redis_conn = Redis.from_url(settings.redis_url)
    
    # Create queue
    queue = Queue('styleforge', connection=redis_conn)
    
    # Start worker
    worker = Worker([queue], connection=redis_conn)
    
    print(f"Starting StyleForge worker...")
    print(f"Generator: {settings.image_generator}")
    print(f"Listening on queue: styleforge")
    
    worker.work(with_scheduler=True)


if __name__ == '__main__':
    main()
