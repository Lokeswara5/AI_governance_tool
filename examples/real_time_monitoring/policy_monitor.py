#!/usr/bin/env python3
"""Example of real-time policy monitoring using watchdog."""

import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
from datetime import datetime
from ai_governance_tool import ComplianceAnalyzer

class PolicyMonitor(FileSystemEventHandler):
    def __init__(self, analyzer, webhook_url=None):
        self.analyzer = analyzer
        self.webhook_url = webhook_url
        self.history = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        if not any(event.src_path.endswith(ext)
                  for ext in ['.md', '.txt', '.policy']):
            return

        self.check_policy(event.src_path)

    def check_policy(self, policy_path):
        """Check a policy file for compliance."""
        try:
            print(f"\nChecking modified policy: {policy_path}")

            # Read and analyze policy
            with open(policy_path, 'r') as f:
                content = f.read()

            result = self.analyzer.check_compliance(content)

            # Store result in history
            self.history[policy_path] = {
                'timestamp': datetime.now().isoformat(),
                'score': result.score,
                'status': 'PASS' if result.is_compliant else 'FAIL'
            }

            # Print results
            print(f"Score: {result.score:.2f}")
            print(f"Status: {'PASS' if result.is_compliant else 'FAIL'}")

            # Generate report name
            report_path = Path(policy_path).with_suffix('.report.pdf')

            # Generate PDF report
            from ai_governance_tool.report import generate_pdf_report
            generate_pdf_report(result, self.analyzer, str(report_path))

            # Send notification if webhook configured
            if self.webhook_url and not result.is_compliant:
                self.send_notification(policy_path, result)

        except Exception as e:
            print(f"Error checking policy: {str(e)}")

    def send_notification(self, policy_path, result):
        """Send notification about non-compliant policy."""
        import requests

        notification = {
            'policy': policy_path,
            'score': result.score,
            'timestamp': datetime.now().isoformat(),
            'status': 'FAIL',
            'details': {
                cat: score for cat, score in result.category_scores.items()
            }
        }

        try:
            requests.post(self.webhook_url, json=notification)
        except Exception as e:
            print(f"Error sending notification: {str(e)}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Monitor policies for changes')
    parser.add_argument('watch_dir', help='Directory to monitor')
    parser.add_argument('--webhook', help='Webhook URL for notifications')
    args = parser.parse_args()

    # Initialize analyzer
    analyzer = ComplianceAnalyzer()

    # Create observer
    observer = Observer()
    monitor = PolicyMonitor(analyzer, args.webhook)
    observer.schedule(monitor, args.watch_dir, recursive=True)
    observer.start()

    print(f"Monitoring directory: {args.watch_dir}")
    print("Press Ctrl+C to stop...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

        # Save history
        history_file = Path('monitoring_history.json')
        with open(history_file, 'w') as f:
            json.dump(monitor.history, f, indent=2)
        print(f"\nHistory saved to: {history_file}")

    observer.join()

if __name__ == '__main__':
    main()