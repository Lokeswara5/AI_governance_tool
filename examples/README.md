# AI Governance Tool Examples

This directory contains example workflows and use cases for the AI Governance Tool.

## 1. CI/CD Workflow
Location: `ci_workflow/`

Demonstrates how to integrate policy checks into your CI/CD pipeline:
- Automatic policy checking on pull requests
- Policy validation before deployment
- Report generation and archiving

Usage:
```bash
# Copy github_workflow.yml to your .github/workflows/ directory
cp ci_workflow/github_workflow.yml ../.github/workflows/policy-check.yml
```

## 2. Batch Processing
Location: `batch_processing/`

Shows how to process multiple policy files in bulk:
- Process entire directories of policies
- Generate summary reports
- Export results to Excel

Usage:
```bash
python process_policies.py ./policies --output-dir ./reports
```

## 3. Custom Rules
Location: `custom_rules/`

Examples of extending the tool with custom compliance rules:
- Add organization-specific requirements
- Custom pattern matching
- Additional compliance categories

Usage:
```bash
python custom_compliance_check.py
```

## 4. Real-Time Monitoring
Location: `real_time_monitoring/`

Demonstrates real-time policy monitoring:
- Watch directories for policy changes
- Automatic compliance checking
- Webhook notifications
- History tracking

Usage:
```bash
# Monitor a directory and send notifications to a webhook
python policy_monitor.py ./policies --webhook https://your-webhook-url

# Monitor without notifications
python policy_monitor.py ./policies
```

## Requirements

Each example may have additional requirements. Install them with:
```bash
pip install -r requirements.txt
```

## Notes

- Adjust paths and settings according to your environment
- Examples can be combined or modified for your needs
- See individual example directories for detailed documentation