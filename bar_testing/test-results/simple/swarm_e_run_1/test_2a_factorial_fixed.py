def factorial(n):
    """Calculate factorial of n (n!)"""
    if n < 0:
        return "Error: Negative number"
    
    # Bug 1 Fixed: Changed initial value from 0 to 1
    # Factorial of any number involves multiplication, and multiplying by 0 gives 0
    result = 1
    
    # Bug 2 Fixed: Changed range(1, n) to range(1, n+1)
    # We need to include n in the multiplication
    for i in range(1, n + 1):
        result *= i
    
    return result


# Original test cases
assert factorial(0) == 1  # 0! = 1 by definition
assert factorial(5) == 120  # 5! = 5*4*3*2*1 = 120
assert factorial(1) == 1  # 1! = 1

# Additional test cases
assert factorial(3) == 6  # 3! = 3*2*1 = 6
assert factorial(10) == 3628800  # 10! = 3628800
assert factorial(-5) == "Error: Negative number"  # Negative numbers don't have factorial
assert factorial(6) == 720  # 6! = 6*5*4*3*2*1 = 720

print("All test cases passed! ✅")

# Explanation of bugs
print("\n### Bug Analysis ###")
print("Bug 1: result = 0")
print("  - Problem: Starting with 0 means all multiplications result in 0")
print("  - Fix: Initialize result to 1 (multiplicative identity)")
print("  - Example: 0 * 1 * 2 * 3 = 0 (wrong) vs 1 * 1 * 2 * 3 = 6 (correct)")

print("\nBug 2: range(1, n)")
print("  - Problem: Python's range excludes the end value, missing n itself")
print("  - Fix: Use range(1, n+1) to include n in the calculation")
print("  - Example: factorial(5) would calculate 1*2*3*4 = 24 instead of 1*2*3*4*5 = 120")

print("\n### Edge Cases Handled ###")
print("- factorial(0) = 1 (by mathematical definition)")
print("- factorial(1) = 1 (base case)")
print("- Negative numbers return error message")
print("- Large numbers work correctly (tested with 10!)")

# Demonstrate the function
print("\n### Function Demonstration ###")
for n in [0, 1, 2, 3, 4, 5, 6, 7]:
    print(f"factorial({n}) = {factorial(n)}")