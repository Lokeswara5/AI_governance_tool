import argparse
import sys
from pathlib import Path
from .analyzer import ComplianceAnalyzer
from .report_generator import generate_pdf_report, generate_comparison_report

def main():
    parser = argparse.ArgumentParser(
        description="AI Governance Policy Compliance Checker"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check a single policy file")
    check_parser.add_argument("policy_file", help="Path to the policy file to check")
    check_parser.add_argument(
        "--output", "-o",
        help="Output PDF report path (default: compliance_report.pdf)",
        default="compliance_report.pdf"
    )
    check_parser.add_argument(
        "--min-score", "-m",
        help="Minimum score for compliance (default: 0.6)",
        type=float,
        default=0.6
    )

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two policy files")
    compare_parser.add_argument("policy1", help="First policy file")
    compare_parser.add_argument("policy2", help="Second policy file")
    compare_parser.add_argument(
        "--output", "-o",
        help="Output PDF report path (default: compliance_comparison.pdf)",
        default="compliance_comparison.pdf"
    )

    # Batch check command
    batch_parser = subparsers.add_parser("batch", help="Check multiple policy files")
    batch_parser.add_argument("directory", help="Directory containing policy files")
    batch_parser.add_argument(
        "--pattern", "-p",
        help="File pattern to match (default: *.txt)",
        default="*.txt"
    )
    batch_parser.add_argument(
        "--output-dir", "-o",
        help="Output directory for reports (default: reports)",
        default="reports"
    )

    args = parser.parse_args()

    if args.command == "check":
        check_single_policy(args)
    elif args.command == "compare":
        compare_policies(args)
    elif args.command == "batch":
        check_batch_policies(args)
    else:
        parser.print_help()
        sys.exit(1)

def check_single_policy(args):
    try:
        analyzer = ComplianceAnalyzer()

        print(f"Analyzing policy file: {args.policy_file}")
        print("=" * 50)

        with open(args.policy_file, 'r') as f:
            policy_text = f.read()

        result = analyzer.check_compliance(policy_text, min_score=args.min_score)

        # Print console report
        print("\nISO 42001 Compliance Check Results:")
        print("-" * 50)
        print(f"Overall Score: {result.score:.2f}")
        print(f"Compliance Status: {'PASS' if result.is_compliant else 'FAIL'}")

        print("\nCategory Analysis:")
        for category, score in result.category_scores.items():
            print(f"\n{category} Score: {score:.2f}")
            if category in result.found_patterns:
                print("Found patterns:")
                for pattern, match in result.found_patterns[category]:
                    print(f"  - {match}")

        # Generate PDF report
        generate_pdf_report(result, analyzer, args.output)
        print(f"\nDetailed report saved to: {args.output}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def compare_policies(args):
    try:
        print(f"Comparing policies:\n1. {args.policy1}\n2. {args.policy2}")
        generate_comparison_report(args.policy1, args.policy2, args.output)
        print(f"\nComparison report saved to: {args.output}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def check_batch_policies(args):
    try:
        analyzer = ComplianceAnalyzer()
        directory = Path(args.directory)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)

        policies = list(directory.glob(args.pattern))
        if not policies:
            print(f"No files matching pattern '{args.pattern}' found in {directory}")
            sys.exit(1)

        print(f"Found {len(policies)} policy files to analyze")
        print("=" * 50)

        for policy_file in policies:
            print(f"\nAnalyzing: {policy_file.name}")
            try:
                with open(policy_file, 'r') as f:
                    policy_text = f.read()

                result = analyzer.check_compliance(policy_text)
                output_file = output_dir / f"{policy_file.stem}_report.pdf"
                generate_pdf_report(result, analyzer, str(output_file))

                print(f"Score: {result.score:.2f} ({'PASS' if result.is_compliant else 'FAIL'})")
                print(f"Report saved to: {output_file}")

            except Exception as e:
                print(f"Error processing {policy_file.name}: {str(e)}")
                continue

        print(f"\nAll reports saved to: {output_dir}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()