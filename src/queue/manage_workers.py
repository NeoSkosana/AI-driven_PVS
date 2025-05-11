"""
Script for managing validation task workers.
"""
import argparse
import subprocess
import signal
import time
import os
import sys
from typing import List
from pathlib import Path

def start_workers(num_workers: int = 2):
    """Start multiple worker processes."""
    worker_script = str(Path(__file__).parent / "task_worker.py")
    processes: List[subprocess.Popen] = []
    
    def handle_shutdown(signum, frame):
        print("\nShutting down workers...")
        for p in processes:
            if p.poll() is None:  # If process is still running
                p.send_signal(signal.SIGTERM)
        time.sleep(2)  # Give workers time to cleanup
        sys.exit(0)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        # Start worker processes
        for i in range(num_workers):
            process = subprocess.Popen(
                [sys.executable, worker_script],
                env=os.environ.copy()
            )
            processes.append(process)
            print(f"Started worker {i+1}")
        
        # Monitor worker processes
        while True:
            for i, p in enumerate(processes):
                if p.poll() is not None:  # Process has terminated
                    print(f"Worker {i+1} died, restarting...")
                    p = subprocess.Popen(
                        [sys.executable, worker_script],
                        env=os.environ.copy()
                    )
                    processes[i] = p
            time.sleep(5)
    
    except KeyboardInterrupt:
        handle_shutdown(None, None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage validation task workers")
    parser.add_argument(
        "--workers",
        type=int,
        default=2,
        help="Number of worker processes to start"
    )
    args = parser.parse_args()
    start_workers(args.workers)
