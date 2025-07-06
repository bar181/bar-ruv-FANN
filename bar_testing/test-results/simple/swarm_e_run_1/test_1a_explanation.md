# Test 1a: Merge Sorted Lists - Implementation

## Approach

I implemented the `merge_sorted_lists` function using a two-pointer technique, which is the optimal approach for merging sorted lists:

1. **Edge Case Handling**: First handle None values and empty lists
2. **Two-Pointer Merge**: Use pointers to track positions in both lists, always selecting the smaller element
3. **Cleanup**: Add any remaining elements from either list

## Time Complexity
- O(n + m) where n and m are the lengths of the input lists

## Space Complexity  
- O(n + m) for the result list

## Key Features
- Proper type hints with Optional[List[int]]
- Comprehensive docstring with examples
- Handles all edge cases (None, empty lists)
- Preserves duplicates correctly
- 5 comprehensive unit tests covering various scenarios

The implementation is efficient, readable, and production-ready.