#!/usr/bin/env python3
"""Interactive CLI dashboard for AI Governance compliance monitoring."""

import sys
import time
from datetime import datetime
import sqlite3
import curses
import pandas as pd
from pathlib import Path
from ai_governance_tool import ComplianceAnalyzer

class ComplianceDashboard:
    def __init__(self, screen):
        self.screen = screen
        self.analyzer = ComplianceAnalyzer()
        self.current_view = 'main'  # main, history, details
        self.selected_policy = None
        self.scroll_offset = 0
        self.max_scroll = 0

    def run(self):
        """Main dashboard loop."""
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.use_default_colors()

        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)

        while True:
            self.screen.clear()

            # Handle different views
            if self.current_view == 'main':
                self.show_main_menu()
            elif self.current_view == 'history':
                self.show_history()
            elif self.current_view == 'details':
                self.show_policy_details()

            self.screen.refresh()

            # Handle input
            try:
                key = self.screen.getch()
                self.handle_input(key)
            except KeyboardInterrupt:
                break

    def show_main_menu(self):
        """Show main dashboard view."""
        height, width = self.screen.getmaxyx()

        # Title
        title = "AI Governance Compliance Dashboard"
        self.screen.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

        # Recent compliance status
        trends = self.analyzer.get_historical_trends()
        if trends and trends['overall_scores']:
            latest_score = trends['overall_scores'][0]
            status = "PASS" if latest_score >= 0.6 else "FAIL"
            status_color = curses.color_pair(1) if status == "PASS" else curses.color_pair(2)

            self.screen.addstr(2, 2, f"Latest Compliance Status: ")
            self.screen.addstr(status, status_color | curses.A_BOLD)
            self.screen.addstr(3, 2, f"Score: {latest_score:.2f}")

            # Category scores
            self.screen.addstr(5, 2, "Category Scores:", curses.A_BOLD)
            row = 6
            for category, scores in trends['category_scores'].items():
                score = scores[0]
                score_color = curses.color_pair(1) if score >= 0.6 else curses.color_pair(2)
                self.screen.addstr(row, 4, f"{category}: ")
                self.screen.addstr(f"{score:.2f}", score_color)
                row += 1

        # Menu options
        menu_start = height - 5
        self.screen.addstr(menu_start, 2, "Options:", curses.A_BOLD)
        self.screen.addstr(menu_start + 1, 4, "C - Check new policy")
        self.screen.addstr(menu_start + 1, 30, "H - View history")
        self.screen.addstr(menu_start + 2, 4, "Q - Quit")

    def show_history(self):
        """Show compliance history view."""
        height, width = self.screen.getmaxyx()

        # Title
        title = "Compliance History"
        self.screen.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

        # Get history data
        trends = self.analyzer.get_historical_trends()
        if not trends or not trends['overall_scores']:
            self.screen.addstr(2, 2, "No history available")
            return

        # Display history
        row = 2
        max_display = height - 6
        records = list(zip(
            trends['timestamps'],
            trends['overall_scores']
        ))

        # Update max scroll
        self.max_scroll = max(0, len(records) - max_display)

        # Display records with scrolling
        for timestamp, score in records[self.scroll_offset:self.scroll_offset + max_display]:
            status = "PASS" if score >= 0.6 else "FAIL"
            status_color = curses.color_pair(1) if status == "PASS" else curses.color_pair(2)

            date = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
            self.screen.addstr(row, 2, f"{date} | ")
            self.screen.addstr(f"Score: {score:.2f} | ")
            self.screen.addstr(status, status_color)
            row += 1

        # Footer
        self.screen.addstr(height - 3, 2, "↑/↓ - Scroll", curses.color_pair(4))
        self.screen.addstr(height - 2, 2, "B - Back to main menu", curses.color_pair(4))

    def show_policy_details(self):
        """Show detailed policy view."""
        if not self.selected_policy:
            return

        height, width = self.screen.getmaxyx()

        # Title
        title = f"Policy Details - {self.selected_policy['timestamp']}"
        self.screen.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

        # Display details
        row = 2
        self.screen.addstr(row, 2, f"Overall Score: {self.selected_policy['score']:.2f}")
        row += 2

        self.screen.addstr(row, 2, "Category Scores:", curses.A_BOLD)
        row += 1
        for category, score in self.selected_policy['category_scores'].items():
            score_color = curses.color_pair(1) if score >= 0.6 else curses.color_pair(2)
            self.screen.addstr(row, 4, f"{category}: ")
            self.screen.addstr(f"{score:.2f}", score_color)
            row += 1

        # Footer
        self.screen.addstr(height - 2, 2, "B - Back to history", curses.color_pair(4))

    def handle_input(self, key):
        """Handle keyboard input."""
        if key == ord('q') and self.current_view == 'main':
            sys.exit(0)
        elif key == ord('b'):
            if self.current_view == 'history':
                self.current_view = 'main'
            elif self.current_view == 'details':
                self.current_view = 'history'
        elif key == ord('h') and self.current_view == 'main':
            self.current_view = 'history'
            self.scroll_offset = 0
        elif key == curses.KEY_UP and self.current_view == 'history':
            self.scroll_offset = max(0, self.scroll_offset - 1)
        elif key == curses.KEY_DOWN and self.current_view == 'history':
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)
        elif key == ord('c') and self.current_view == 'main':
            curses.endwin()
            self.check_new_policy()
            self.screen = curses.initscr()

    def check_new_policy(self):
        """Check a new policy file."""
        try:
            path = input("\nEnter policy file path: ").strip()
            if not path:
                return

            with open(path, 'r') as f:
                content = f.read()

            result = self.analyzer.check_compliance(content)
            print("\nAnalysis complete!")
            print(f"Score: {result.score:.2f}")
            print(f"Status: {'PASS' if result.is_compliant else 'FAIL'}")

            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\nError: {str(e)}")
            input("\nPress Enter to continue...")

def main():
    curses.wrapper(lambda screen: ComplianceDashboard(screen).run())

if __name__ == "__main__":
    main()