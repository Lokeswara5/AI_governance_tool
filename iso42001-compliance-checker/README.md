# ISO 42001 Compliance Checker

A Python-based policy engine that analyzes text for compliance with ISO 42001 AI Management System requirements.

## Features

- **Advanced Pattern Matching**: Uses regex patterns to identify key ISO 42001 compliance terms
- **Proximity Analysis**: Measures relationships between compliance concepts in text
- **Historical Tracking**: SQLite database for tracking compliance history
- **Rich Reporting**: Generates detailed PDF reports with charts and trends
- **Comprehensive Testing**: Full test suite for reliability

## Categories Analyzed

1. **Core Principles**
   - Transparency
   - Accountability
   - Ethical Considerations

2. **Risk Management**
   - Risk Assessment
   - Security Measures
   - Monitoring Systems
   - Governance Frameworks

3. **Fairness & Privacy**
   - Fairness Measures
   - Privacy Protection
   - Bias Prevention

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the compliance checker:
```bash
python main.py
```

3. Check the generated reports:
- Console output shows immediate results
- `compliance_report.pdf` contains detailed analysis with charts
- SQLite database tracks historical compliance

## Example Output

```
ISO 42001 Compliance Check Results:
--------------------------------------------------
Overall Score: 0.91
Compliance Status: PASS

Category Analysis:
Core Principles Score: 1.00
Risk Management Score: 1.00
Fairness & Privacy Score: 0.70

Pattern Proximity Analysis:
- Risk assessment and management - Security measures: 0.33
- System monitoring - Governance framework: 0.33
...
```

## Testing

Run the test suite:
```bash
python -m unittest test_compliance.py -v
```

## Requirements

- Python 3.6+
- matplotlib
- reportlab
- numpy