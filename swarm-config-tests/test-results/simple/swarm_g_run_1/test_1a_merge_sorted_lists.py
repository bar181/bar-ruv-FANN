"""
Test 1a: Code Generation - Merge Sorted Lists
Engineering Team Implementation
"""

from typing import List, Optional


def merge_sorted_lists(list1: Optional[List[int]], list2: Optional[List[int]]) -> List[int]:
    """
    Merge two sorted lists of integers into a single sorted list.
    
    Args:
        list1: First sorted list of integers (can be None)
        list2: Second sorted list of integers (can be None)
    
    Returns:
        A single sorted list containing all elements from both input lists
        
    Examples:
        >>> merge_sorted_lists([1, 3, 5], [2, 4, 6])
        [1, 2, 3, 4, 5, 6]
        >>> merge_sorted_lists([], [1, 2, 3])
        [1, 2, 3]
        >>> merge_sorted_lists(None, [1, 2, 3])
        [1, 2, 3]
    """
    # Handle None values
    if list1 is None:
        list1 = []
    if list2 is None:
        list2 = []
    
    # Handle empty lists
    if not list1:
        return list2.copy()
    if not list2:
        return list1.copy()
    
    # Merge the sorted lists
    result = []
    i, j = 0, 0
    
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    
    # Add remaining elements
    result.extend(list1[i:])
    result.extend(list2[j:])
    
    return result


# Unit Tests
def test_merge_sorted_lists():
    """Unit tests for merge_sorted_lists function."""
    
    # Test 1: Basic merge
    assert merge_sorted_lists([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
    print("✓ Test 1 passed: Basic merge")
    
    # Test 2: Empty lists
    assert merge_sorted_lists([], [1, 2, 3]) == [1, 2, 3]
    assert merge_sorted_lists([1, 2, 3], []) == [1, 2, 3]
    assert merge_sorted_lists([], []) == []
    print("✓ Test 2 passed: Empty lists")
    
    # Test 3: None values
    assert merge_sorted_lists(None, [1, 2, 3]) == [1, 2, 3]
    assert merge_sorted_lists([1, 2, 3], None) == [1, 2, 3]
    assert merge_sorted_lists(None, None) == []
    print("✓ Test 3 passed: None values")
    
    # Test 4: Lists with duplicates
    assert merge_sorted_lists([1, 2, 2, 3], [2, 3, 4]) == [1, 2, 2, 2, 3, 3, 4]
    print("✓ Test 4 passed: Duplicates")
    
    # Test 5: Lists of different lengths
    assert merge_sorted_lists([1, 2], [3, 4, 5, 6, 7]) == [1, 2, 3, 4, 5, 6, 7]
    assert merge_sorted_lists([5, 6, 7], [1, 2]) == [1, 2, 5, 6, 7]
    print("✓ Test 5 passed: Different lengths")
    
    print("\nAll tests passed! ✅")


if __name__ == "__main__":
    # Run tests
    test_merge_sorted_lists()
    
    # Demonstrate usage
    print("\nExample usage:")
    result = merge_sorted_lists([1, 3, 5], [2, 4, 6])
    print(f"merge_sorted_lists([1, 3, 5], [2, 4, 6]) = {result}")