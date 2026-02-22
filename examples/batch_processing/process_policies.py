#!/usr/bin/env python3
"""Example script for batch processing multiple policy documents."""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
from ai_governance_tool import ComplianceAnalyzer

def process_directory(input_dir: str, output_dir: str, min_score: float = 0.6):
    """Process all policy files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Initialize analyzer
    analyzer = ComplianceAnalyzer()

    # Track results for summary
    results = []

    # Process each policy file
    for policy_file in input_path.glob("**/*.md"):
        print(f"Processing: {policy_file}")

        try:
            # Read and analyze policy
            with open(policy_file, 'r') as f:
                content = f.read()

            result = analyzer.check_compliance(content, min_score=min_score)

            # Generate report name
            report_name = output_path / f"{policy_file.stem}_report.pdf"

            # Generate PDF report
            from ai_governance_tool.report import generate_pdf_report
            generate_pdf_report(result, analyzer, str(report_name))

            # Store results for summary
            results.append({
                'file': policy_file.name,
                'score': result.score,
                'status': 'PASS' if result.is_compliant else 'FAIL',
                'report': report_name.name,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            print(f"Error processing {policy_file}: {str(e)}")
            results.append({
                'file': policy_file.name,
                'score': 0.0,
                'status': 'ERROR',
                'report': None,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })

    # Create summary report
    df = pd.DataFrame(results)
    summary_file = output_path / 'compliance_summary.xlsx'
    df.to_excel(summary_file, index=False)

    print(f"\nProcessing complete!")
    print(f"Processed {len(results)} files")
    print(f"Summary saved to: {summary_file}")
    print("\nCompliance Summary:")
    print(f"PASS: {len(df[df['status'] == 'PASS'])}")
    print(f"FAIL: {len(df[df['status'] == 'FAIL'])}")
    print(f"ERROR: {len(df[df['status'] == 'ERROR'])}")

def main():
    parser = argparse.ArgumentParser(description='Batch process policy files')
    parser.add_argument('input_dir', help='Directory containing policy files')
    parser.add_argument('--output-dir', '-o', default='reports',
                       help='Output directory for reports')
    parser.add_argument('--min-score', '-m', type=float, default=0.6,
                       help='Minimum compliance score (0.0-1.0)')

    args = parser.parse_args()
    process_directory(args.input_dir, args.output_dir, args.min_score)

if __name__ == '__main__':
    main()