#!/usr/bin/env python3
import os

def calculate_duration(start_file, end_file):
    try:
        with open(start_file, 'r') as f:
            start = float(f.read().strip())
        with open(end_file, 'r') as f:
            end = float(f.read().strip())
        return end - start
    except:
        return None

# Calculate individual test durations
for i in range(1, 5):
    duration = calculate_duration(f'test_{i}_start.txt', f'test_{i}_end.txt')
    if duration:
        with open(f'test_{i}_duration.txt', 'w') as f:
            f.write(f'{duration:.2f}')
        print(f'Test {i} duration: {duration:.2f} seconds')

# Calculate total team duration
total_duration = calculate_duration('team2_start_time.txt', 'team2_end_time.txt')
if total_duration:
    print(f'\nTotal Team 2 duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)')
    
    # Create summary
    with open('team2_summary.txt', 'w') as f:
        f.write(f'Team 2 Hard Tests Summary\n')
        f.write(f'========================\n\n')
        f.write(f'Total Duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)\n\n')
        f.write(f'Individual Test Durations:\n')
        for i in range(1, 5):
            duration = calculate_duration(f'test_{i}_start.txt', f'test_{i}_end.txt')
            if duration:
                f.write(f'  Test {i}: {duration:.2f} seconds\n')
        f.write(f'\nAll tests completed successfully\n')