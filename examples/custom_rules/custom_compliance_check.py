#!/usr/bin/env python3
"""Example of extending the compliance checker with custom rules."""

from typing import Dict, List, Tuple
from ai_governance_tool import ComplianceAnalyzer, CompliancePattern, ComplianceCategory

class CustomComplianceAnalyzer(ComplianceAnalyzer):
    """Custom analyzer with organization-specific rules."""

    def __init__(self, db_path: str = "custom_compliance_history.db"):
        super().__init__(db_path)

        # Add custom categories and patterns
        self.categories.extend([
            ComplianceCategory(
                name="Data Protection",
                patterns=[
                    CompliancePattern(
                        pattern=r"GDPR\s+compliance",
                        weight=0.4,
                        category="Data Protection",
                        description="GDPR Compliance"
                    ),
                    CompliancePattern(
                        pattern=r"data\s+encryption",
                        weight=0.3,
                        category="Data Protection",
                        description="Data Encryption"
                    ),
                    CompliancePattern(
                        pattern=r"data\s+retention",
                        weight=0.3,
                        category="Data Protection",
                        description="Data Retention"
                    )
                ],
                required_score=0.6,
                weight=0.3
            ),
            ComplianceCategory(
                name="Model Governance",
                patterns=[
                    CompliancePattern(
                        pattern=r"model\s+validation",
                        weight=0.3,
                        category="Model Governance",
                        description="Model Validation"
                    ),
                    CompliancePattern(
                        pattern=r"version\s+control",
                        weight=0.3,
                        category="Model Governance",
                        description="Version Control"
                    ),
                    CompliancePattern(
                        pattern=r"model\s+documentation",
                        weight=0.4,
                        category="Model Governance",
                        description="Model Documentation"
                    )
                ],
                required_score=0.5,
                weight=0.3
            )
        ])

def main():
    # Example policy text
    policy_text = """
    Our AI system follows strict GDPR compliance guidelines and implements
    comprehensive data encryption protocols. All models undergo regular
    model validation checks and are subject to version control. We maintain
    detailed model documentation and enforce data retention policies.
    """

    # Initialize custom analyzer
    analyzer = CustomComplianceAnalyzer()

    # Check compliance
    result = analyzer.check_compliance(policy_text)

    # Print results
    print("\nCustom Compliance Check Results:")
    print("-" * 50)
    print(f"Overall Score: {result.score:.2f}")
    print(f"Status: {'PASS' if result.is_compliant else 'FAIL'}")

    # Print category results
    print("\nCategory Analysis:")
    for category, score in result.category_scores.items():
        print(f"\n{category} Score: {score:.2f}")
        if category in result.found_patterns:
            print("Found patterns:")
            for pattern, match in result.found_patterns[category]:
                print(f"  - {match}")

if __name__ == '__main__':
    main()