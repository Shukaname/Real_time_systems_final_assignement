import random
import time
import numpy as np


def measureMultiplicationTime() -> int:
    n: int = random.getrandbits(int(5E4))
    m: int = random.getrandbits(int(5E4))
    
    t0: float = time.perf_counter()
    n*m
    tf: float = time.perf_counter()
    return (tf-t0)*1000 #to get in ms

iter_num = 10_000
times: list[int] = [measureMultiplicationTime() for _ in range(iter_num)]
times = np.array(times)
print(f"Average time to multiply two large number : {np.mean(times)} ms")
print(f"Minimal time to multiply two large number : {np.min(times)} ms")
print(f"Maximal time to multiply two large number : {np.max(times)} ms")
print(f"Q1 : {np.percentile(times, 25)} ms")
print(f"Q2 : {np.median(times)} ms")
print(f"Q3 : {np.percentile(times, 75)} ms")
print(f"WCET : {np.max(times)*1.3} ms") #30% margin
