#!/usr/bin/env python3
"""
Analyze test response quality and generate metrics
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_code_quality(content: str) -> Dict[str, float]:
    """Analyze code quality metrics"""
    metrics = {
        'has_docstrings': 0,
        'has_type_hints': 0,
        'has_error_handling': 0,
        'has_tests': 0,
        'code_blocks': 0,
        'completeness': 0
    }
    
    # Check for code blocks
    code_blocks = re.findall(r'```(?:python|py)?\n(.*?)```', content, re.DOTALL)
    metrics['code_blocks'] = len(code_blocks)
    
    if code_blocks:
        full_code = '\n'.join(code_blocks)
        
        # Check for docstrings
        if re.search(r'""".*?"""', full_code, re.DOTALL) or re.search(r"'''.*?'''", full_code, re.DOTALL):
            metrics['has_docstrings'] = 1
        
        # Check for type hints
        if re.search(r':\s*(?:int|str|float|bool|List|Dict|Optional|Any|Tuple)', full_code):
            metrics['has_type_hints'] = 1
        
        # Check for error handling
        if re.search(r'\b(?:try|except|raise|ValueError|TypeError|Exception)\b', full_code):
            metrics['has_error_handling'] = 1
        
        # Check for tests
        if re.search(r'\b(?:test_|unittest|TestCase|assert|def test)', full_code):
            metrics['has_tests'] = 1
    
    # Overall completeness score
    metrics['completeness'] = sum([
        metrics['has_docstrings'],
        metrics['has_type_hints'],
        metrics['has_error_handling'],
        metrics['has_tests'],
        min(metrics['code_blocks'] / 2, 1)  # Normalize code blocks
    ]) / 5
    
    return metrics

def analyze_response(response_file: Path, test_type: str) -> Dict[str, any]:
    """Analyze a single test response"""
    if not response_file.exists():
        return {'error': 'File not found'}
    
    content = response_file.read_text()
    
    # Basic metrics
    metrics = {
        'file': response_file.name,
        'lines': len(content.splitlines()),
        'words': len(content.split()),
        'characters': len(content)
    }
    
    # Test-specific analysis
    if 'test_1' in response_file.name or 'test_2' in response_file.name:
        # Code generation/debugging tests
        code_metrics = analyze_code_quality(content)
        metrics.update(code_metrics)
        
    elif 'test_3' in response_file.name:
        # Math tests
        metrics['has_solution'] = 1 if re.search(r'\b(?:solution|answer|result)\b', content, re.I) else 0
        metrics['has_explanation'] = 1 if re.search(r'\b(?:because|therefore|thus|since)\b', content, re.I) else 0
        metrics['has_code'] = 1 if '```' in content else 0
        
    elif 'test_4' in response_file.name:
        # Research tests
        metrics['has_comparison'] = 1 if re.search(r'\|.*\|.*\|', content) else 0
        metrics['has_recommendation'] = 1 if re.search(r'\b(?:recommend|suggest|best|choose)\b', content, re.I) else 0
        metrics['sections'] = len(re.findall(r'^#+\s+', content, re.MULTILINE))
    
    return metrics

def calculate_quality_score(metrics: Dict[str, any]) -> float:
    """Calculate overall quality score (0-10)"""
    score = 5.0  # Base score
    
    # Size bonus (up to 1 point)
    if metrics.get('words', 0) > 200:
        score += min(metrics['words'] / 500, 1.0)
    
    # Code quality bonus (up to 2 points)
    if 'completeness' in metrics:
        score += metrics['completeness'] * 2
    
    # Structure bonus (up to 1 point)
    if metrics.get('sections', 0) > 2:
        score += min(metrics['sections'] / 5, 1.0)
    
    # Specific feature bonus (up to 1 point)
    feature_score = sum([
        metrics.get('has_tests', 0) * 0.25,
        metrics.get('has_error_handling', 0) * 0.25,
        metrics.get('has_recommendation', 0) * 0.25,
        metrics.get('has_comparison', 0) * 0.25
    ])
    score += feature_score
    
    return min(score, 10.0)

def generate_report(test_dir: Path, test_level: str = 'simple'):
    """Generate quality analysis report"""
    print(f"\n📊 Quality Analysis Report")
    print(f"Directory: {test_dir}")
    print(f"Test Level: {test_level.upper()}\n")
    
    results = []
    total_score = 0
    test_count = 0
    
    # Analyze each test response
    for i in range(1, 5):
        suffix = 'a' if test_level == 'simple' else 'b'
        response_file = test_dir / f"test_{i}{suffix}_response.txt"
        
        if response_file.exists():
            metrics = analyze_response(response_file, test_level)
            quality_score = calculate_quality_score(metrics)
            metrics['quality_score'] = quality_score
            
            print(f"Test {i}{suffix}:")
            print(f"  - Size: {metrics['words']} words, {metrics['lines']} lines")
            print(f"  - Quality Score: {quality_score:.1f}/10")
            
            if 'completeness' in metrics:
                print(f"  - Code Quality: {metrics['completeness']*100:.0f}%")
            
            total_score += quality_score
            test_count += 1
            results.append(metrics)
            print()
    
    if test_count > 0:
        avg_score = total_score / test_count
        print(f"📈 Overall Results:")
        print(f"  - Average Quality Score: {avg_score:.1f}/10")
        print(f"  - Tests Completed: {test_count}/4")
        
        # Generate updated summary
        summary_file = test_dir / f"baseline_{'moderate_' if test_level == 'moderate' else ''}summary_analyzed.md"
        with open(summary_file, 'w') as f:
            f.write(f"# Automated Quality Analysis\n\n")
            f.write(f"## Overall Metrics\n")
            f.write(f"- Average Quality Score: {avg_score:.1f}/10\n")
            f.write(f"- Tests Completed: {test_count}/4\n\n")
            
            f.write(f"## Individual Test Scores\n")
            for i, result in enumerate(results, 1):
                suffix = 'a' if test_level == 'simple' else 'b'
                f.write(f"\n### Test {i}{suffix}\n")
                f.write(f"- Quality Score: {result['quality_score']:.1f}/10\n")
                f.write(f"- Response Size: {result['words']} words\n")
                
                if 'completeness' in result:
                    f.write(f"- Code Completeness: {result['completeness']*100:.0f}%\n")
                    f.write(f"  - Docstrings: {'✓' if result['has_docstrings'] else '✗'}\n")
                    f.write(f"  - Type Hints: {'✓' if result['has_type_hints'] else '✗'}\n")
                    f.write(f"  - Error Handling: {'✓' if result['has_error_handling'] else '✗'}\n")
                    f.write(f"  - Tests: {'✓' if result['has_tests'] else '✗'}\n")
        
        print(f"\n✅ Analysis saved to: {summary_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze-test-quality.py <test-results-directory> [simple|moderate]")
        sys.exit(1)
    
    test_dir = Path(sys.argv[1])
    test_level = sys.argv[2] if len(sys.argv) > 2 else 'simple'
    
    if not test_dir.exists():
        print(f"❌ Directory not found: {test_dir}")
        sys.exit(1)
    
    generate_report(test_dir, test_level)