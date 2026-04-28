tasks_definition = [
    {"id": 1, "C": 3, "T": 10},
    {"id": 2, "C": 3, "T": 10}, 
    {"id": 3, "C": 2, "T": 20}, 
    {"id": 4, "C": 2, "T": 20}, 
    {"id": 5, "C": 2, "T": 40}, 
    {"id": 6, "C": 2, "T": 40}, 
    {"id": 7, "C": 3, "T": 80}, 
]

hyperperiod = 80 
jobs = []

for t in tasks_definition:
    for i in range(hyperperiod // t["T"]):
        jobs.append({
            "id": f"T{t['id']}_J{i+1}",
            "task_id": t["id"],
            "r": i * t["T"],      # Release time (Causality)
            "C": t["C"],          # Temps d'éxécution
            "d": (i + 1) * t["T"] # Deadline
        })


jobs.sort(key=lambda x: x["r"])

print(f"Nombre de jobs générés : {len(jobs)}")

def run_v1_scheduler(job_list):
    """
    Non-preemptive scheduler 
    Goal: No deadlines missed  + Minimize waiting 
    Strategy: Earliest Deadline First (EDF) among ready jobs
    """
    current_time = 0
    schedule = []
    remaining = list(job_list)
    
    total_waiting = 0
    total_idle = 0

    print(f"{'Job':<8} | {'Arrival':<8} | {'Start':<8} | {'End':<8} | {'Deadline':<8} | {'Status'}")
    print("-" * 70)

    while remaining:
        # 1. Filter by Causality: Only jobs that have already arrived
        ready_jobs = [j for j in remaining if j['r'] <= current_time]
        
        if not ready_jobs:
            # CPU is Idle: Jump to the next job arrival
            next_arrival = min(j['r'] for j in remaining)
            total_idle += (next_arrival - current_time)
            current_time = next_arrival
            continue

        # 2. Optimization: Pick the earliest deadline job among ready jobs (EDF) 
        ready_jobs.sort(key=lambda x: x['d'])
        job = ready_jobs[0]

        # 3. Execution (Non-preemptive) 
        start_time = current_time
        end_time = start_time + job['C']
        waiting_time = start_time - job['r']
        
        # 4. Schedulability Check 
        status = "✅ OK"
        if end_time > job['d']:
            status = "❌ MISSED" # 

        # Log results
        print(f"{job['id']:<8} | {job['r']:<8.1f} | {start_time:<8.1f} | {end_time:<8.1f} | {job['d']:<8.1f} | {status}")
        
        schedule.append(job)
        total_waiting += waiting_time
        current_time = end_time
        remaining.remove(job)

    return total_waiting, total_idle

# --- STEP 3: EXECUTION ---
print("--- VERSION 1: NO DEADLINE MISSES ---")
total_wait, total_idle = run_v1_scheduler(jobs)

print("-" * 70)
print(f"Total Waiting Time: {total_wait:.2f} ms") # 
print(f"Total Idle Time: {total_idle:.2f} ms")    #