from ortools.sat.python import cp_model

# Task data (Times multiplied by 1000 to use integers: microseconds)
# Format: { "id": Task Name, "C": Execution Time, "T": Period }
tasks = [
    {"id": "T1", "C": 2552, "T": 10000},  # C1 = 2.552 ms
    {"id": "T2", "C": 3000, "T": 10000},
    {"id": "T3", "C": 2000, "T": 20000},
    {"id": "T4", "C": 2000, "T": 20000},
    {"id": "T5", "C": 2000, "T": 40000},
    {"id": "T6", "C": 2000, "T": 40000},
    {"id": "T7", "C": 3000, "T": 80000}
]

HYPERPERIOD = 80000  # 80 ms

def solve_schedule(allow_miss_t5=False):
    model = cp_model.CpModel()
    
    # 1. Generate all jobs over the hyperperiod
    jobs = []
    job_index = 0
    for task in tasks:
        num_jobs = HYPERPERIOD // task["T"]
        for j in range(num_jobs):
            arrival = j * task["T"]
            deadline = arrival + task["T"]
            jobs.append({
                "job_id": f"{task['id']}_job{j+1}",
                "task_id": task['id'],
                "arrival": arrival,
                "C": task["C"],
                "deadline": deadline,
                "index": job_index
            })
            job_index += 1

    # 2. Create model variables
    # start_vars: start time of each job
    # end_vars: end time of each job
    # intervals: interval variable required by OR-Tools to handle non-overlapping
    start_vars = {}
    end_vars = {}
    intervals = []
    
    for job in jobs:
        idx = job["index"]
        # The job cannot start before its arrival, and cannot end after the hyperperiod (or beyond)
        start_vars[idx] = model.NewIntVar(job["arrival"], HYPERPERIOD * 2, f"start_{idx}")
        end_vars[idx] = model.NewIntVar(job["arrival"], HYPERPERIOD * 2, f"end_{idx}")
        
        # end = start + C
        model.Add(end_vars[idx] == start_vars[idx] + job["C"])
        
        # Non-preemption and job duration constraint
        interval = model.NewIntervalVar(start_vars[idx], job["C"], end_vars[idx], f"interval_{idx}")
        intervals.append(interval)
        
        # Deadline constraints
        if allow_miss_t5 and job["task_id"] == "T5":
            # We allow T5 to miss its deadline, but still bound it to prevent infinite loops
            pass 
        else:
            # For all others (or everyone if allow_miss_t5 is False), strict deadline!
            model.Add(end_vars[idx] <= job["deadline"])

    # 3. Main constraint: the processor can only execute one job at a time (no overlap)
    model.AddNoOverlap(intervals)

    # 4. Objective Function: Minimize total waiting time
    # Waiting time of a job = start - arrival
    total_waiting_time = sum(start_vars[job["index"]] - job["arrival"] for job in jobs)
    model.Minimize(total_waiting_time)

    # 5. Resolution
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # 6. Display results
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("\n" + "="*60)
        print(f"SCENARIO: {'T5 Allowed to miss deadline' if allow_miss_t5 else 'Strict (No deadline misses)'}")
        print("="*60)
        
        total_wait = solver.ObjectiveValue()
        print(f"Objective: Total waiting time minimized = {total_wait / 1000.0:.3f} ms\n")
        
        print(f"{'Job ID':<12} | {'Arrival':<8} | {'Start':<8} | {'End':<8} | {'Wait Time':<10} | {'Resp. Time':<10} | {'Deadline':<8} | {'Met?'}")
        print("-" * 90)
        
        for job in jobs:
            idx = job["index"]
            start_val = solver.Value(start_vars[idx])
            end_val = solver.Value(end_vars[idx])
            wait_val = start_val - job["arrival"]
            resp_time = end_val - job["arrival"]
            met = "YES" if end_val <= job["deadline"] else "NO !!!"
            
            # Conversion to milliseconds for display
            print(f"{job['job_id']:<12} | {job['arrival']/1000.0:<8.1f} | {start_val/1000.0:<8.3f} | {end_val/1000.0:<8.3f} | {wait_val/1000.0:<10.3f} | {resp_time/1000.0:<10.3f} | {job['deadline']/1000.0:<8.1f} | {met}")
            
    else:
        print("No solution found. The system might not be schedulable under these constraints.")

# Execute both scenarios
solve_schedule(allow_miss_t5=False)
solve_schedule(allow_miss_t5=True)