"""
Test 2a: Debugging - Fix Factorial Function
Engineering Team Implementation
"""

# Original buggy code (commented for reference)
"""
def factorial(n):
    # Calculate factorial of n (n!)
    if n < 0:
        return "Error: Negative number"
    
    result = 0  # Bug 1: Should be 1
    for i in range(1, n):  # Bug 2: Should be range(1, n+1)
        result *= i
    
    return result
"""

# Fixed implementation
def factorial(n):
    """
    Calculate factorial of n (n!)
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n, or error message for negative numbers
        
    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
        >>> factorial(-1)
        'Error: Negative number'
    """
    if n < 0:
        return "Error: Negative number"
    
    # Bug Fix 1: Initialize result to 1 instead of 0
    # (0 * anything = 0, so original always returned 0)
    result = 1
    
    # Bug Fix 2: Use range(1, n+1) to include n in the multiplication
    # (original stopped at n-1, missing the final multiplication)
    for i in range(1, n + 1):
        result *= i
    
    return result


def test_factorial():
    """Comprehensive tests for factorial function."""
    
    # Original test cases
    assert factorial(0) == 1, f"factorial(0) = {factorial(0)}, expected 1"
    assert factorial(5) == 120, f"factorial(5) = {factorial(5)}, expected 120"
    assert factorial(1) == 1, f"factorial(1) = {factorial(1)}, expected 1"
    print("✓ Original test cases passed")
    
    # Additional test cases
    assert factorial(3) == 6, f"factorial(3) = {factorial(3)}, expected 6"
    assert factorial(4) == 24, f"factorial(4) = {factorial(4)}, expected 24"
    assert factorial(10) == 3628800, f"factorial(10) = {factorial(10)}, expected 3628800"
    print("✓ Additional positive number tests passed")
    
    # Edge case tests
    assert factorial(-1) == "Error: Negative number"
    assert factorial(-100) == "Error: Negative number"
    print("✓ Negative number tests passed")
    
    print("\nAll tests passed! ✅")


def explain_bugs():
    """Detailed explanation of the bugs found and fixed."""
    
    print("BUG ANALYSIS REPORT")
    print("=" * 50)
    print("\nBug 1: Incorrect initialization")
    print("- Original: result = 0")
    print("- Problem: 0 multiplied by any number equals 0")
    print("- Fix: result = 1 (multiplicative identity)")
    print("- Impact: All factorials returned 0")
    
    print("\nBug 2: Off-by-one error in range")
    print("- Original: range(1, n)")
    print("- Problem: range(1, n) generates numbers from 1 to n-1")
    print("- Fix: range(1, n+1) to include n")
    print("- Impact: Result was missing multiplication by n")
    print("- Example: factorial(5) would calculate 1*2*3*4 instead of 1*2*3*4*5")
    
    print("\nSpecial Case Handling:")
    print("- factorial(0) = 1 (by mathematical definition)")
    print("- This works correctly because range(1, 1) is empty")
    print("- So the loop doesn't execute and result remains 1")


if __name__ == "__main__":
    # Run tests
    print("Running factorial tests...\n")
    test_factorial()
    
    # Explain the bugs
    print("\n")
    explain_bugs()
    
    # Demonstrate the fixed function
    print("\n" + "=" * 50)
    print("DEMONSTRATION OF FIXED FUNCTION:")
    for n in [0, 1, 3, 5, 10]:
        print(f"factorial({n}) = {factorial(n)}")
    print(f"factorial(-5) = {factorial(-5)}")