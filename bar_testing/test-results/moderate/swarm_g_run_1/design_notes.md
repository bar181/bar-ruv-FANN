# TaskQueue Design Notes

## Architecture Decisions

### 1. Data Structure Choice
- **heapq**: Python's built-in heap implementation for efficient O(log n) insertion and removal
- **Tuple storage**: Each item is stored as `(priority, counter, task)` to enable:
  - Priority-based ordering (first element)
  - FIFO within same priority (counter as tiebreaker)
  - Actual task data (third element)

### 2. Thread Safety
- **Single Lock**: Uses one `threading.Lock` for all operations
- **Coarse-grained locking**: Entire methods are protected for simplicity
- **No deadlock risk**: Single lock prevents circular dependencies

### 3. Priority System
- **IntEnum**: Type-safe priority constants (HIGH=1, MEDIUM=2, LOW=3)
- **Lower numbers = higher priority**: Natural for heap implementation
- **Validation**: Runtime checks prevent invalid priority values

### 4. FIFO Guarantee
- **Monotonic counter**: Increments for each task added
- **Heap comparison**: Python's heapq compares tuples element by element
- **Result**: Tasks with same priority are ordered by insertion time

### 5. Error Handling
- **Invalid priorities**: Raises ValueError with clear message
- **Empty queue**: Returns None (not exception) for better usability
- **Type hints**: Helps catch errors at development time

## Performance Characteristics

- **add_task**: O(log n) - heap insertion
- **get_next_task**: O(log n) - heap removal
- **peek**: O(1) - direct access to heap top
- **is_empty**: O(1) - length check
- **Memory**: O(n) - stores all tasks

## Trade-offs

1. **Lock granularity**: Chose simplicity over maximum concurrency
2. **None vs Exception**: Returning None for empty queue is more pythonic
3. **Counter overflow**: In practice, Python integers have arbitrary precision
4. **Task comparison**: Tasks themselves don't need to be comparable

## Potential Enhancements

1. **Condition variables**: For blocking get operations
2. **Maximum size limit**: Prevent unbounded growth
3. **Task cancellation**: Mark tasks as cancelled without removal
4. **Priority boost**: Dynamic priority adjustment
5. **Persistence**: Save/load queue state