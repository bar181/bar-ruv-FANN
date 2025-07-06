#!/usr/bin/env python3
"""
Calculate test durations for Research Team Hard Tests
"""

def read_timestamp(filename):
    """Read timestamp from file"""
    try:
        with open(filename, 'r') as f:
            return float(f.read().strip())
    except:
        return None

def calculate_duration(start_file, end_file):
    """Calculate duration between start and end timestamps"""
    start = read_timestamp(start_file)
    end = read_timestamp(end_file)
    
    if start is None or end is None:
        return None
    
    return end - start

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds is None:
        return "N/A"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {remaining_seconds}s"
    else:
        return f"{remaining_seconds}s"

# Calculate individual test durations
test_1_duration = calculate_duration("test_1_start.txt", "test_1_end.txt")
test_2_duration = calculate_duration("test_2_start.txt", "test_2_end.txt")
test_3_duration = calculate_duration("test_3_start.txt", "test_3_end.txt")
test_4_duration = calculate_duration("test_4_start.txt", "test_4_end.txt")

# Calculate total duration
team_start = read_timestamp("team3_start_time.txt")
team_end = read_timestamp("test_4_end.txt")
total_duration = team_end - team_start if team_start and team_end else None

# Save individual durations
durations = {
    "test_1": test_1_duration,
    "test_2": test_2_duration, 
    "test_3": test_3_duration,
    "test_4": test_4_duration
}

for test, duration in durations.items():
    if duration is not None:
        with open(f"{test}_duration.txt", "w") as f:
            f.write(str(int(duration)))

# Print results
print("Research Team Hard Tests - Duration Summary")
print("=" * 50)
print(f"Test 1 (API Client): {format_duration(test_1_duration)}")
print(f"Test 2 (Debugging): {format_duration(test_2_duration)}")
print(f"Test 3 (Math Optimization): {format_duration(test_3_duration)}")
print(f"Test 4 (Research Analysis): {format_duration(test_4_duration)}")
print(f"Total Duration: {format_duration(total_duration)}")

# Calculate average
valid_durations = [d for d in durations.values() if d is not None]
if valid_durations:
    avg_duration = sum(valid_durations) / len(valid_durations)
    print(f"Average Test Duration: {format_duration(avg_duration)}")