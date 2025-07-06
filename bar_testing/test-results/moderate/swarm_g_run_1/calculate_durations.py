"""
Calculate test durations for QA team moderate tests.
"""

from datetime import datetime
import os

def parse_time(time_str):
    """Parse time string to datetime object."""
    return datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M:%S")

def calculate_duration(start_file, end_file):
    """Calculate duration between start and end times."""
    if not os.path.exists(start_file) or not os.path.exists(end_file):
        return None
    
    with open(start_file, 'r') as f:
        start_time = parse_time(f.read())
    
    with open(end_file, 'r') as f:
        end_time = parse_time(f.read())
    
    duration = end_time - start_time
    return duration.total_seconds() / 60  # Convert to minutes

def main():
    print("=== QA Team Moderate Test Duration Analysis ===\n")
    
    # Calculate individual test durations
    tests = [
        ("Test 1 (TaskQueue)", "test_1_start.txt", "test_1_end.txt"),
        ("Test 2 (Race Condition)", "test_2_start.txt", "test_2_end.txt"),
        ("Test 3 (Dijkstra)", "test_3_start.txt", "test_3_end.txt"),
        ("Test 4 (Caching Strategy)", "test_4_start.txt", "test_4_end.txt")
    ]
    
    total_duration = 0
    
    for test_name, start_file, end_file in tests:
        duration = calculate_duration(start_file, end_file)
        if duration:
            print(f"{test_name}: {duration:.2f} minutes")
            total_duration += duration
            
            # Save individual duration
            test_num = test_name.split()[1]
            with open(f"test_{test_num}_duration.txt", 'w') as f:
                f.write(f"{duration:.2f}")
        else:
            print(f"{test_name}: Unable to calculate (missing files)")
    
    # Calculate overall team duration
    team_duration = calculate_duration("team_start_time.txt", "test_4_end.txt")
    if team_duration:
        print(f"\nTotal QA Team Duration: {team_duration:.2f} minutes")
        
        # Save overall duration
        with open("team_duration.txt", 'w') as f:
            f.write(f"{team_duration:.2f}")
        
        print(f"Sum of individual tests: {total_duration:.2f} minutes")
        print(f"Overhead/coordination time: {(team_duration - total_duration):.2f} minutes")
    else:
        print(f"\nSum of individual tests: {total_duration:.2f} minutes")
        print("Unable to calculate total team duration (missing team start time)")

if __name__ == "__main__":
    main()