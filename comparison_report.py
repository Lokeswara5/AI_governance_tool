from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import numpy as np
from main import ComplianceAnalyzer  # Import your main analyzer

def generate_comparison_report(failing_policy_path: str, passing_policy_path: str, output_path: str):
    # Initialize analyzer
    analyzer = ComplianceAnalyzer()

    # Analyze both policies
    with open(failing_policy_path, 'r') as f:
        failing_result = analyzer.check_compliance(f.read())

    with open(passing_policy_path, 'r') as f:
        passing_result = analyzer.check_compliance(f.read())

    # Create the PDF
    doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )

    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10
    )

    # Title
    story.append(Paragraph("ISO 42001 Compliance Comparison Report", title_style))
    story.append(Spacer(1, 20))

    # Overall Comparison Table
    overall_data = [
        ["Metric", "Non-Compliant Policy", "Compliant Policy"],
        ["Overall Score", f"{failing_result.score:.2f}", f"{passing_result.score:.2f}"],
        ["Status", "FAIL" if not failing_result.is_compliant else "PASS",
         "FAIL" if not passing_result.is_compliant else "PASS"],
    ]

    table = Table(overall_data, colWidths=[2*inch, 3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Category Comparison
    story.append(Paragraph("Category Analysis", heading2_style))

    categories_data = [
        ["Category", "Non-Compliant Score", "Compliant Score", "Difference"],
    ]

    for category in failing_result.category_scores.keys():
        fail_score = failing_result.category_scores[category]
        pass_score = passing_result.category_scores[category]
        diff = pass_score - fail_score
        categories_data.append([
            category,
            f"{fail_score:.2f}",
            f"{pass_score:.2f}",
            f"{diff:+.2f}"
        ])

    table = Table(categories_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))

    # Create comparison chart
    plt.figure(figsize=(8, 4))
    categories = list(failing_result.category_scores.keys())
    fail_scores = [failing_result.category_scores[cat] for cat in categories]
    pass_scores = [passing_result.category_scores[cat] for cat in categories]

    x = np.arange(len(categories))
    width = 0.35

    plt.bar(x - width/2, fail_scores, width, label='Non-Compliant')
    plt.bar(x + width/2, pass_scores, width, label='Compliant')

    plt.ylabel('Score')
    plt.title('Category Comparison')
    plt.xticks(x, categories, rotation=45)
    plt.legend()
    plt.tight_layout()

    # Save chart
    chart_path = 'comparison_chart.png'
    plt.savefig(chart_path)
    story.append(Image(chart_path, width=400, height=200))
    story.append(Spacer(1, 20))

    # Pattern Analysis
    story.append(Paragraph("Pattern Matches", heading2_style))

    # Combine all patterns
    all_patterns = set()
    for patterns in failing_result.found_patterns.values():
        all_patterns.update(p[0] for p in patterns)
    for patterns in passing_result.found_patterns.values():
        all_patterns.update(p[0] for p in patterns)

    pattern_data = [
        ["Pattern", "Non-Compliant", "Compliant"]
    ]

    for pattern in sorted(all_patterns):
        in_failing = "✘"
        in_passing = "✘"

        # Check if pattern is in failing policy
        for patterns in failing_result.found_patterns.values():
            if any(p[0] == pattern for p in patterns):
                in_failing = "✓"
                break

        # Check if pattern is in passing policy
        for patterns in passing_result.found_patterns.values():
            if any(p[0] == pattern for p in patterns):
                in_passing = "✓"
                break

        pattern_data.append([pattern, in_failing, in_passing])

    table = Table(pattern_data, colWidths=[3*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)

    # Build the PDF
    doc.build(story)

    # Clean up
    plt.close('all')
    import os
    if os.path.exists(chart_path):
        os.remove(chart_path)

if __name__ == "__main__":
    # Generate comparison report
    generate_comparison_report(
        "test_non_compliant.md",
        "test_compliant_fixed.md",
        "compliance_comparison.pdf"
    )