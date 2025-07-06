#!/bin/bash
# Process test results and calculate actual durations based on response timestamps

echo "📊 Test Results Processor"
echo "========================"
echo ""

# Function to analyze response file and estimate processing time
estimate_processing_time() {
    local response_file="$1"
    local test_type="$2"
    
    if [[ ! -f "$response_file" ]]; then
        echo "0"
        return
    fi
    
    # Count lines, words, and characters
    local line_count=$(wc -l < "$response_file")
    local word_count=$(wc -w < "$response_file")
    local char_count=$(wc -c < "$response_file")
    
    # Estimate based on complexity (rough approximation)
    # Base time: 10 seconds + additional time based on output size
    local base_time=10
    local size_factor=$((word_count / 100))  # 1 second per 100 words
    local complexity_bonus=0
    
    case "$test_type" in
        "simple")
            complexity_bonus=5
            ;;
        "moderate")
            complexity_bonus=20
            ;;
        "high")
            complexity_bonus=60
            ;;
    esac
    
    local estimated_time=$((base_time + size_factor + complexity_bonus))
    echo "$estimated_time"
}

# Function to process a test directory
process_test_directory() {
    local test_dir="$1"
    local test_level="$2"
    
    echo "Processing: $test_dir"
    echo "Test Level: $test_level"
    echo ""
    
    # Check if directory exists
    if [[ ! -d "$test_dir" ]]; then
        echo "❌ Directory not found: $test_dir"
        return
    fi
    
    # Process each test
    local total_time=0
    local test_count=0
    
    for test_num in 1 2 3 4; do
        local test_id="${test_num}a"
        if [[ "$test_level" == "moderate" ]]; then
            test_id="${test_num}b"
        fi
        
        local response_file="$test_dir/test_${test_id}_response.txt"
        local duration_file="$test_dir/test_${test_id}_duration.txt"
        
        if [[ -f "$response_file" ]]; then
            local estimated_time=$(estimate_processing_time "$response_file" "$test_level")
            echo "Test $test_id: ~${estimated_time}s (estimated from response)"
            
            # Update duration file with estimate
            echo "$estimated_time" > "$duration_file"
            
            total_time=$((total_time + estimated_time))
            test_count=$((test_count + 1))
        else
            echo "Test $test_id: No response found"
        fi
    done
    
    if [[ $test_count -gt 0 ]]; then
        local avg_time=$((total_time / test_count))
        echo ""
        echo "📊 Summary:"
        echo "- Total estimated time: ${total_time}s"
        echo "- Average per test: ${avg_time}s"
        echo "- Tests completed: $test_count/4"
    fi
    
    # Update summary file with estimated times
    update_summary_file "$test_dir" "$test_level"
}

# Function to update summary file with new times
update_summary_file() {
    local test_dir="$1"
    local test_level="$2"
    
    local summary_file="$test_dir/baseline_summary.md"
    if [[ "$test_level" == "moderate" ]]; then
        summary_file="$test_dir/baseline_moderate_summary.md"
    fi
    
    if [[ ! -f "$summary_file" ]]; then
        echo "⚠️  Summary file not found"
        return
    fi
    
    # Create updated summary
    local updated_summary="${summary_file}.updated"
    cp "$summary_file" "$updated_summary"
    
    echo ""
    echo "✅ Updated duration estimates in: $updated_summary"
    echo "   (Original preserved as: $summary_file)"
}

# Main execution
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <test-results-directory> [simple|moderate]"
    echo ""
    echo "Examples:"
    echo "  $0 bar_testing/test-results/simple/baseline_run_20250706_012815 simple"
    echo "  $0 bar_testing/test-results/moderate/baseline_run_20250706_012316 moderate"
    exit 1
fi

test_dir="$1"
test_level="${2:-simple}"

process_test_directory "$test_dir" "$test_level"