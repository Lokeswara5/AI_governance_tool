#!/bin/bash
set -e

# Configuration
SEVERITY_THRESHOLD="MEDIUM"
SCAN_PATHS="./"
EXCLUDE_PATTERNS=(
    "*.test.js"
    "*.spec.py"
    "node_modules/"
    "venv/"
    ".git/"
)

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Starting secrets scan..."

# Function to check for required tools
check_dependencies() {
    local missing_deps=0

    if ! command -v gitleaks &> /dev/null; then
        echo "Installing gitleaks..."
        curl -L https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_linux_x64.tar.gz | tar xz
        sudo mv gitleaks /usr/local/bin/
    fi

    if ! command -v trufflehog &> /dev/null; then
        echo "Installing trufflehog..."
        pip install trufflehog
    fi
}

# Function to scan with gitleaks
scan_with_gitleaks() {
    local output_file="gitleaks-report.json"
    echo "Running gitleaks scan..."

    gitleaks detect \
        --source "." \
        --report-path "$output_file" \
        --no-git \
        --verbose || true

    return $(jq length "$output_file")
}

# Function to scan with trufflehog
scan_with_trufflehog() {
    local output_file="trufflehog-report.json"
    echo "Running trufflehog scan..."

    trufflehog filesystem . \
        --json \
        --output "$output_file" \
        --only-verified || true

    return $(jq length "$output_file")
}

# Function to check for hardcoded secrets in code
scan_code_secrets() {
    local files_to_scan=$(find . -type f \
        -not -path "*/\.*" \
        -not -path "*/node_modules/*" \
        -not -path "*/venv/*" \
        -exec file {} \; |
        grep "text" |
        cut -d: -f1)

    local found_secrets=0

    echo "Scanning source code for potential secrets..."

    while IFS= read -r file; do
        # Search for common secret patterns
        if grep -i -E "password|secret|key|token|credential" "$file" > /dev/null; then
            echo -e "${YELLOW}Warning: Potential secret found in $file${NC}"
            found_secrets=$((found_secrets + 1))
        fi
    done <<< "$files_to_scan"

    return $found_secrets
}

# Function to check AWS credentials
check_aws_credentials() {
    local found_issues=0

    echo "Checking AWS credential configuration..."

    # Check for hardcoded AWS credentials
    if find . -type f -name "*.py" -o -name "*.js" | xargs grep -l "AKIA"; then
        echo -e "${RED}Error: Found hardcoded AWS access keys${NC}"
        found_issues=$((found_issues + 1))
    fi

    # Verify AWS credentials are using environment variables
    if ! grep -r "AWS_ACCESS_KEY_ID" .github/workflows/ > /dev/null; then
        echo -e "${YELLOW}Warning: AWS credentials should use GitHub secrets${NC}"
        found_issues=$((found_issues + 1))
    fi

    return $found_issues
}

# Function to generate report
generate_report() {
    local gitleaks_count=$1
    local trufflehog_count=$2
    local code_secrets_count=$3
    local aws_issues_count=$4

    cat << EOF > security-scan-report.md
# Security Scan Report
Generated on $(date)

## Summary
- Gitleaks findings: $gitleaks_count
- Trufflehog findings: $trufflehog_count
- Code secrets: $code_secrets_count
- AWS issues: $aws_issues_count

## Recommendations
$([ $gitleaks_count -gt 0 ] && echo "- Review gitleaks-report.json for detailed findings")
$([ $trufflehog_count -gt 0 ] && echo "- Review trufflehog-report.json for detailed findings")
$([ $code_secrets_count -gt 0 ] && echo "- Review code for hardcoded secrets")
$([ $aws_issues_count -gt 0 ] && echo "- Fix AWS credential configuration")

## Next Steps
1. Review all findings
2. Remove or rotate any exposed secrets
3. Update code to use environment variables
4. Implement secret scanning in CI/CD pipeline
EOF
}

main() {
    check_dependencies

    local exit_code=0
    local gitleaks_count=0
    local trufflehog_count=0
    local code_secrets_count=0
    local aws_issues_count=0

    scan_with_gitleaks
    gitleaks_count=$?

    scan_with_trufflehog
    trufflehog_count=$?

    scan_code_secrets
    code_secrets_count=$?

    check_aws_credentials
    aws_issues_count=$?

    generate_report $gitleaks_count $trufflehog_count $code_secrets_count $aws_issues_count

    total_issues=$((gitleaks_count + trufflehog_count + code_secrets_count + aws_issues_count))

    if [ $total_issues -gt 0 ]; then
        echo -e "${RED}Found $total_issues potential security issues${NC}"
        echo "See security-scan-report.md for details"
        exit_code=1
    else
        echo -e "${GREEN}No security issues found${NC}"
    fi

    exit $exit_code
}

main "$@"