"""
Test 3a: Mathematical Problem - Fence Optimization
Engineering Team Implementation
"""

import matplotlib.pyplot as plt
import numpy as np


def maximize_enclosure(fence_length):
    """
    Find optimal dimensions for rectangular enclosure against a wall.
    
    Given a fence length, determines the width and length that maximize
    the enclosed area when one side is against a wall (only 3 sides need fencing).
    
    Args:
        fence_length: Total length of available fencing (positive number)
        
    Returns:
        tuple: (width, length, area) where width is perpendicular to wall
        
    Mathematical derivation:
        Let w = width (perpendicular to wall)
        Let l = length (parallel to wall)
        
        Constraint: 2w + l = fence_length
        Therefore: l = fence_length - 2w
        
        Area = w * l = w * (fence_length - 2w) = fence_length*w - 2w²
        
        To maximize, take derivative and set to 0:
        dA/dw = fence_length - 4w = 0
        Therefore: w = fence_length/4
        
        And: l = fence_length - 2w = fence_length/2
    """
    if fence_length <= 0:
        raise ValueError("Fence length must be positive")
    
    # Optimal dimensions from calculus
    optimal_width = fence_length / 4
    optimal_length = fence_length / 2
    max_area = optimal_width * optimal_length
    
    return (optimal_width, optimal_length, max_area)


def prove_optimality(fence_length):
    """
    Mathematical proof that w = fence_length/4 maximizes area.
    """
    print("MATHEMATICAL PROOF OF OPTIMALITY")
    print("=" * 50)
    print(f"\nGiven: {fence_length}m of fencing, one side against wall")
    print("\nSetup:")
    print("- Let w = width (perpendicular to wall)")
    print("- Let l = length (parallel to wall)")
    print("- Constraint: 2w + l = fence_length (only 3 sides need fencing)")
    print(f"- Therefore: l = {fence_length} - 2w")
    
    print("\nArea function:")
    print("- A(w) = w × l = w × (fence_length - 2w)")
    print("- A(w) = fence_length×w - 2w²")
    
    print("\nFind critical points:")
    print("- dA/dw = fence_length - 4w")
    print("- Set dA/dw = 0: fence_length - 4w = 0")
    print(f"- Solve: w = fence_length/4 = {fence_length}/4 = {fence_length/4}")
    
    print("\nVerify it's a maximum:")
    print("- d²A/dw² = -4 < 0")
    print("- Since second derivative is negative, this is a maximum")
    
    print("\nOptimal dimensions:")
    w_opt = fence_length / 4
    l_opt = fence_length / 2
    area_opt = w_opt * l_opt
    print(f"- Width: {w_opt}m")
    print(f"- Length: {l_opt}m") 
    print(f"- Maximum area: {area_opt}m²")
    
    return True


def visualize_area_relationship(fence_length):
    """
    Create visualization showing area vs width relationship.
    """
    # Generate width values from 0 to fence_length/2
    # (width can't exceed fence_length/2, otherwise length would be negative)
    widths = np.linspace(0.1, fence_length/2 - 0.1, 100)
    areas = []
    
    for w in widths:
        l = fence_length - 2*w
        if l > 0:  # Valid configuration
            areas.append(w * l)
        else:
            areas.append(0)
    
    # Find optimal point
    w_opt = fence_length / 4
    l_opt = fence_length / 2
    area_opt = w_opt * l_opt
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(widths, areas, 'b-', linewidth=2, label='Area function')
    plt.plot(w_opt, area_opt, 'ro', markersize=10, label=f'Maximum at w={w_opt}')
    
    # Add labels and formatting
    plt.xlabel('Width (m)', fontsize=12)
    plt.ylabel('Area (m²)', fontsize=12)
    plt.title(f'Area vs Width for {fence_length}m of Fencing', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # Add annotation for maximum
    plt.annotate(f'Max Area = {area_opt:.1f}m²\nWidth = {w_opt:.1f}m\nLength = {l_opt:.1f}m',
                xy=(w_opt, area_opt), xytext=(w_opt + fence_length/10, area_opt - area_opt/10),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('fence_optimization_plot.png', dpi=150)
    plt.close()
    
    print(f"\nVisualization saved as 'fence_optimization_plot.png'")


def test_maximize_enclosure():
    """Test cases for the optimization function."""
    print("\nRUNNING TEST CASES")
    print("=" * 50)
    
    # Test 1: Example case
    width, length, area = maximize_enclosure(100)
    assert width == 25.0, f"Expected width=25, got {width}"
    assert length == 50.0, f"Expected length=50, got {length}"
    assert area == 1250.0, f"Expected area=1250, got {area}"
    print("✓ Test 1 passed: maximize_enclosure(100) = (25, 50, 1250)")
    
    # Test 2: Different fence length
    width, length, area = maximize_enclosure(60)
    assert width == 15.0, f"Expected width=15, got {width}"
    assert length == 30.0, f"Expected length=30, got {length}"
    assert area == 450.0, f"Expected area=450, got {area}"
    print("✓ Test 2 passed: maximize_enclosure(60) = (15, 30, 450)")
    
    # Test 3: Small fence length
    width, length, area = maximize_enclosure(20)
    assert width == 5.0, f"Expected width=5, got {width}"
    assert length == 10.0, f"Expected length=10, got {length}"
    assert area == 50.0, f"Expected area=50, got {area}"
    print("✓ Test 3 passed: maximize_enclosure(20) = (5, 10, 50)")
    
    # Test 4: Invalid input
    try:
        maximize_enclosure(0)
        assert False, "Should raise ValueError for zero fence length"
    except ValueError:
        print("✓ Test 4 passed: Correctly rejects zero fence length")
    
    try:
        maximize_enclosure(-10)
        assert False, "Should raise ValueError for negative fence length"
    except ValueError:
        print("✓ Test 5 passed: Correctly rejects negative fence length")
    
    print("\nAll tests passed! ✅")


if __name__ == "__main__":
    # Run tests
    test_maximize_enclosure()
    
    # Prove optimality for the example case
    print("\n")
    prove_optimality(100)
    
    # Create visualization
    print("\n")
    visualize_area_relationship(100)
    
    # Show some example calculations
    print("\n\nEXAMPLE CALCULATIONS:")
    print("=" * 50)
    for fence in [50, 100, 200]:
        w, l, a = maximize_enclosure(fence)
        print(f"Fence length: {fence}m → Width: {w}m, Length: {l}m, Area: {a}m²")