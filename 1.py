import concurrent.futures
import time

def task(identifier, duration):
    time.sleep(duration)
    return f"Task {identifier} completed in {duration} seconds"

# List of task durations
durations = [5, 3, 6, 2]

with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit tasks to the executor
    futures = [executor.submit(task, i, duration) for i, duration in enumerate(durations)]
    
    # Process tasks as they complete
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        print(result)
        
        # Cancel remaining futures
        for future in futures:
                future.cancel()
        break  # Exit the loop after the first task completes
