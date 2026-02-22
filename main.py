from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import numpy as np
from collections import defaultdict

@dataclass
class CompliancePattern:
    pattern: str
    weight: float
    category: str
    description: str

@dataclass
class ComplianceCategory:
    name: str
    patterns: List[CompliancePattern]
    required_score: float
    weight: float

@dataclass
class ComplianceResult:
    is_compliant: bool
    score: float
    category_scores: Dict[str, float]
    found_patterns: Dict[str, List[Tuple[str, str]]]  # category -> [(pattern, matched_text)]
    timestamp: str
    proximity_scores: Dict[str, float]

class ComplianceAnalyzer:
    def __init__(self, db_path: str = "compliance_history.db"):
        self.db_path = db_path
        self.initialize_db()

        # Define compliance patterns with regex and proximity requirements
        self.categories = [
            ComplianceCategory(
                name="Core Principles",
                patterns=[
                    CompliancePattern(
                        pattern=r"transparen(?:t|cy)",
                        weight=0.4,
                        category="Core Principles",
                        description="Transparency in AI systems"
                    ),
                    CompliancePattern(
                        pattern=r"accountab(?:le|ility)",
                        weight=0.3,
                        category="Core Principles",
                        description="Accountability measures"
                    ),
                    CompliancePattern(
                        pattern=r"ethical(?:ly)?",
                        weight=0.3,
                        category="Core Principles",
                        description="Ethical considerations"
                    )
                ],
                required_score=0.6,
                weight=0.4
            ),
            ComplianceCategory(
                name="Risk Management",
                patterns=[
                    CompliancePattern(
                        pattern=r"risk\s+(?:assess|manag|mitigat)",
                        weight=0.3,
                        category="Risk Management",
                        description="Risk assessment and management"
                    ),
                    CompliancePattern(
                        pattern=r"secur(?:e|ity)",
                        weight=0.3,
                        category="Risk Management",
                        description="Security measures"
                    ),
                    CompliancePattern(
                        pattern=r"monitor(?:ing)?",
                        weight=0.2,
                        category="Risk Management",
                        description="System monitoring"
                    ),
                    CompliancePattern(
                        pattern=r"govern(?:ance)?",
                        weight=0.2,
                        category="Risk Management",
                        description="Governance framework"
                    )
                ],
                required_score=0.5,
                weight=0.3
            ),
            ComplianceCategory(
                name="Fairness & Privacy",
                patterns=[
                    CompliancePattern(
                        pattern=r"fair(?:ly|ness)",
                        weight=0.3,
                        category="Fairness & Privacy",
                        description="Fairness in AI systems"
                    ),
                    CompliancePattern(
                        pattern=r"privacy",
                        weight=0.3,
                        category="Fairness & Privacy",
                        description="Privacy protection"
                    ),
                    CompliancePattern(
                        pattern=r"bias|discriminat(?:ion|e)",
                        weight=0.4,
                        category="Fairness & Privacy",
                        description="Bias and discrimination prevention"
                    )
                ],
                required_score=0.5,
                weight=0.3
            )
        ]

    def initialize_db(self):
        """Initialize SQLite database for historical tracking."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
        CREATE TABLE IF NOT EXISTS compliance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            overall_score REAL,
            is_compliant INTEGER,
            category_scores TEXT,
            found_patterns TEXT
        )
        ''')

        conn.commit()
        conn.close()

    def calculate_proximity_score(self, text: str, pattern1: str, pattern2: str) -> float:
        """Calculate how close two patterns appear in the text."""
        matches1 = list(re.finditer(pattern1, text, re.IGNORECASE))
        matches2 = list(re.finditer(pattern2, text, re.IGNORECASE))

        if not matches1 or not matches2:
            return 0.0

        # Find minimum word distance between any two matches
        min_distance = float('inf')
        for m1 in matches1:
            for m2 in matches2:
                start1, end1 = m1.span()
                start2, end2 = m2.span()

                # Count words between matches
                between_text = text[min(end1, end2):max(start1, start2)]
                word_distance = len(between_text.split())

                min_distance = min(min_distance, word_distance)

        # Convert distance to score (closer = higher score)
        if min_distance == float('inf'):
            return 0.0
        return 1.0 / (1.0 + min_distance)

    def check_compliance(self, text: str, min_score: float = 0.6) -> ComplianceResult:
        """Perform comprehensive compliance analysis with pattern matching and proximity scoring."""
        category_scores = {}
        found_patterns = defaultdict(list)
        proximity_scores = {}

        # Pattern matching within categories
        for category in self.categories:
            category_score = 0.0
            max_possible_score = sum(p.weight for p in category.patterns)

            for pattern in category.patterns:
                matches = list(re.finditer(pattern.pattern, text, re.IGNORECASE))
                if matches:
                    matched_text = [text[m.start():m.end()] for m in matches]
                    found_patterns[category.name].append((pattern.pattern, matched_text[0]))
                    category_score += pattern.weight

            # Normalize category score to 0-1 range
            category_scores[category.name] = category_score / max_possible_score if max_possible_score > 0 else 0.0

        # Calculate proximity scores between related patterns
        for category in self.categories:
            patterns = category.patterns
            for i in range(len(patterns)):
                for j in range(i + 1, len(patterns)):
                    key = f"{patterns[i].description} - {patterns[j].description}"
                    proximity_scores[key] = self.calculate_proximity_score(
                        text, patterns[i].pattern, patterns[j].pattern
                    )

        # Calculate overall score
        total_score = sum(
            score * next(cat.weight for cat in self.categories if cat.name == category)
            for category, score in category_scores.items()
        )

        is_compliant = total_score >= min_score

        result = ComplianceResult(
            is_compliant=is_compliant,
            score=total_score,
            category_scores=category_scores,
            found_patterns=dict(found_patterns),
            timestamp=datetime.now().isoformat(),
            proximity_scores=proximity_scores
        )

        # Store result in database
        self.store_result(result)

        return result

    def store_result(self, result: ComplianceResult):
        """Store compliance result in SQLite database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
        INSERT INTO compliance_history
        (timestamp, overall_score, is_compliant, category_scores, found_patterns)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            result.timestamp,
            result.score,
            1 if result.is_compliant else 0,
            json.dumps(result.category_scores),
            json.dumps(result.found_patterns)
        ))

        conn.commit()
        conn.close()

    def get_historical_trends(self) -> Dict:
        """Retrieve historical compliance data for trending."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
        SELECT timestamp, overall_score, category_scores
        FROM compliance_history
        ORDER BY timestamp DESC
        LIMIT 10
        ''')

        results = c.fetchall()
        conn.close()

        if not results:
            return {}

        trends = {
            'timestamps': [],
            'overall_scores': [],
            'category_scores': defaultdict(list)
        }

        for timestamp, score, category_scores in results:
            trends['timestamps'].append(timestamp)
            trends['overall_scores'].append(score)

            cat_scores = json.loads(category_scores)
            for category, cat_score in cat_scores.items():
                trends['category_scores'][category].append(cat_score)

        return trends

def generate_pdf_report(result: ComplianceResult, analyzer: ComplianceAnalyzer, output_path: str):
    """Generate a detailed PDF report with charts and analysis."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("ISO 42001 Compliance Report", title_style))
    story.append(Spacer(1, 12))

    # Overall Results
    story.append(Paragraph(f"Overall Compliance: {'PASS' if result.is_compliant else 'FAIL'}", styles['Heading2']))
    story.append(Paragraph(f"Score: {result.score:.2f}", styles['Normal']))
    story.append(Paragraph(f"Timestamp: {result.timestamp}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Category Results
    story.append(Paragraph("Category Analysis", styles['Heading2']))
    for category, score in result.category_scores.items():
        story.append(Paragraph(f"{category}: {score:.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Pattern Matches
    story.append(Paragraph("Detected Patterns", styles['Heading2']))
    for category, patterns in result.found_patterns.items():
        story.append(Paragraph(f"{category}:", styles['Heading3']))
        for pattern, match in patterns:
            story.append(Paragraph(f"- Pattern '{pattern}' matched: '{match}'", styles['Normal']))
    story.append(Spacer(1, 12))

    # Proximity Analysis
    story.append(Paragraph("Pattern Proximity Analysis", styles['Heading2']))
    proximity_data = []
    for key, score in result.proximity_scores.items():
        if score > 0:
            proximity_data.append([key, f"{score:.2f}"])

    if proximity_data:
        t = Table(proximity_data)
        t.setStyle(TableStyle([
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
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
    story.append(Spacer(1, 12))

    # Historical Trends
    story.append(Paragraph("Historical Trends", styles['Heading2']))
    trends = analyzer.get_historical_trends()

    if trends:
        # Create trend charts using matplotlib
        plt.figure(figsize=(8, 4))
        plt.plot(range(len(trends['overall_scores'])), trends['overall_scores'], marker='o')
        plt.title('Overall Compliance Score Trend')
        plt.xlabel('Assessment Number')
        plt.ylabel('Score')
        plt.grid(True)

        # Save plot to file and add to PDF
        trend_path = 'trend_chart.png'
        plt.savefig(trend_path)
        story.append(Image(trend_path))

        # Category trends
        plt.figure(figsize=(8, 4))
        for category, scores in trends['category_scores'].items():
            plt.plot(range(len(scores)), scores, marker='o', label=category)
        plt.title('Category Score Trends')
        plt.xlabel('Assessment Number')
        plt.ylabel('Score')
        plt.legend()
        plt.grid(True)

        category_trend_path = 'category_trends.png'
        plt.savefig(category_trend_path)
        story.append(Image(category_trend_path))

    doc.build(story)

    # Cleanup temporary files
    if Path('trend_chart.png').exists():
        Path('trend_chart.png').unlink()
    if Path('category_trends.png').exists():
        Path('category_trends.png').unlink()

if __name__ == "__main__":
    sample_response = """
    Our AI system prioritizes ethical decision-making and transparent operations.
    We conduct regular risk assessments and maintain strict security protocols.
    Privacy is paramount in our system, with fairness measures built into every
    process. Accountability is ensured through continuous monitoring and robust
    governance frameworks. We actively work to identify and eliminate potential
    biases, while our risk management system provides comprehensive oversight
    of all operations.
    """

    analyzer = ComplianceAnalyzer()
    result = analyzer.check_compliance(sample_response)

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

    print("\nPattern Proximity Analysis:")
    for key, score in result.proximity_scores.items():
        if score > 0:
            print(f"{key}: {score:.2f}")

    # Export reports
    generate_pdf_report(result, analyzer, "compliance_report.pdf")