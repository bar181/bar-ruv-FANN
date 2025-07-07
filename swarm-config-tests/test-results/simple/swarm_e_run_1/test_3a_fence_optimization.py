import matplotlib.pyplot as plt
import numpy as np

def maximize_enclosure(fence_length):
    """
    Find optimal dimensions for a rectangular enclosure against a wall.
    
    Given a fence length, calculate the width and length that maximize
    the enclosed area when one side is against a wall (only 3 sides need fencing).
    
    Args:
        fence_length: Total length of available fencing (positive number)
        
    Returns:
        Tuple of (width, length, area) where:
        - width: Distance perpendicular to the wall
        - length: Distance parallel to the wall
        - area: Maximum enclosed area
    """
    if fence_length <= 0:
        raise ValueError("Fence length must be positive")
    
    # Mathematical derivation:
    # Let width = w (perpendicular to wall), length = l (parallel to wall)
    # Constraint: 2w + l = fence_length (only 3 sides need fencing)
    # Therefore: l = fence_length - 2w
    # Area = w * l = w * (fence_length - 2w) = fence_length*w - 2w²
    # To maximize, take derivative and set to 0:
    # dA/dw = fence_length - 4w = 0
    # Therefore: w = fence_length / 4
    
    width = fence_length / 4
    length = fence_length - 2 * width  # = fence_length / 2
    area = width * length
    
    return width, length, area


def plot_area_vs_width(fence_length):
    """Create a visualization showing area vs. width relationship"""
    # Generate width values from 0 to fence_length/2
    # (at w = fence_length/2, length would be 0)
    widths = np.linspace(0.01, fence_length/2 - 0.01, 100)
    areas = []
    
    for w in widths:
        l = fence_length - 2*w
        area = w * l
        areas.append(area)
    
    # Find optimal point
    optimal_w, optimal_l, optimal_area = maximize_enclosure(fence_length)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(widths, areas, 'b-', linewidth=2, label='Area = w × (L - 2w)')
    plt.plot(optimal_w, optimal_area, 'ro', markersize=10, 
             label=f'Optimal: w={optimal_w:.1f}, area={optimal_area:.1f}')
    
    plt.xlabel('Width (meters)', fontsize=12)
    plt.ylabel('Area (square meters)', fontsize=12)
    plt.title(f'Area vs. Width for Fence Length = {fence_length}m', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # Add annotation
    plt.annotate(f'Maximum area = {optimal_area:.1f} m²\nWidth = {optimal_w:.1f} m\nLength = {optimal_l:.1f} m',
                xy=(optimal_w, optimal_area), xytext=(optimal_w + 5, optimal_area - 100),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('/workspaces/ruv-FANN/bar_testing/test-results/simple/swarm_e_run_1/test_3a_optimization_plot.png', dpi=150)
    print("Plot saved as test_3a_optimization_plot.png")


# Mathematical proof
print("### Mathematical Proof of Optimality ###")
print("Given: Fence length L, rectangular enclosure against a wall")
print("Variables: width = w (perpendicular to wall), length = l (parallel to wall)")
print("\nConstraint: 2w + l = L (only 3 sides need fencing)")
print("Express l in terms of w: l = L - 2w")
print("\nArea function: A(w) = w × l = w × (L - 2w) = Lw - 2w²")
print("\nTo find maximum, take derivative and set to 0:")
print("dA/dw = L - 4w = 0")
print("Solving: w = L/4")
print("\nSecond derivative test: d²A/dw² = -4 < 0")
print("Since second derivative is negative, this is indeed a maximum.")
print("\nOptimal dimensions:")
print("- Width: w = L/4")
print("- Length: l = L - 2w = L - 2(L/4) = L/2")
print("- Maximum area: A = w × l = (L/4) × (L/2) = L²/8")

# Test the function
print("\n### Function Tests ###")

# Test case from example
w, l, a = maximize_enclosure(100)
print(f"\nmaximize_enclosure(100):")
print(f"  Width: {w} meters")
print(f"  Length: {l} meters")
print(f"  Area: {a} square meters")
assert w == 25 and l == 50 and a == 1250, "Example test case failed"
print("✓ Example test case passed")

# Additional test cases
test_cases = [50, 200, 1000]
for fence in test_cases:
    w, l, a = maximize_enclosure(fence)
    expected_w = fence / 4
    expected_l = fence / 2
    expected_a = fence * fence / 8
    
    assert abs(w - expected_w) < 0.001, f"Width calculation failed for {fence}m"
    assert abs(l - expected_l) < 0.001, f"Length calculation failed for {fence}m"
    assert abs(a - expected_a) < 0.001, f"Area calculation failed for {fence}m"
    
    print(f"\nmaximize_enclosure({fence}):")
    print(f"  Width: {w} meters")
    print(f"  Length: {l} meters")
    print(f"  Area: {a} square meters")
    print(f"✓ Test passed")

# Test error handling
try:
    maximize_enclosure(0)
    print("\n✗ Error handling test failed - should raise ValueError for 0")
except ValueError as e:
    print(f"\n✓ Error handling test passed: {e}")

try:
    maximize_enclosure(-10)
    print("✗ Error handling test failed - should raise ValueError for negative")
except ValueError as e:
    print(f"✓ Error handling test passed: {e}")

# Create visualization
print("\n### Creating Visualization ###")
plot_area_vs_width(100)

print("\nAll tests completed successfully! ✨")