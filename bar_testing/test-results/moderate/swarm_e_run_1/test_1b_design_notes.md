# TaskQueue Design Notes

## Design Decisions

1. **Data Structure**: Used Python's `heapq` module for efficient priority queue operations with O(log n) insertion and removal.

2. **Thread Safety**: Implemented using `threading.Lock` to ensure all operations are atomic and thread-safe.

3. **FIFO Within Priority**: Added an internal counter to maintain insertion order for tasks with the same priority level.

4. **Priority Enum**: Used `IntEnum` for clear priority definitions while maintaining compatibility with integer comparisons.

5. **Error Handling**: Validates priority values and raises `ValueError` for invalid inputs.

## Key Features

- Thread-safe implementation protects against race conditions
- Efficient O(log n) operations using heap data structure
- Maintains FIFO ordering within same priority level
- Clear API with type hints and comprehensive docstrings
- Robust error handling for invalid inputs
- Additional helper methods: `size()` and `clear()`

## Test Coverage

- Empty queue behavior
- Single task operations
- Priority ordering verification
- FIFO ordering within same priority
- Invalid input handling
- Thread safety with concurrent producers/consumers
- Queue clearing functionality

## Performance Characteristics

- **Time Complexity**:
  - `add_task()`: O(log n)
  - `get_next_task()`: O(log n)
  - `peek()`: O(1)
  - `is_empty()`: O(1)
  - `size()`: O(1)

- **Space Complexity**: O(n) where n is the number of tasks in the queue

## Thread Safety Verification

The thread safety test creates multiple producer and consumer threads that concurrently add and remove tasks, verifying that no race conditions occur and all tasks are properly processed.