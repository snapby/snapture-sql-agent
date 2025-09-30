#!/bin/bash

# generate_changelog.sh - Generate CHANGELOG.md from git commits
# Usage: ./generate_changelog.sh [from_tag] [to_tag]
#
# If no tags provided, generates changelog from last tag to HEAD
# If no tags exist, generates changelog from first commit to HEAD

set -euo pipefail

# Configuration
CHANGELOG_FILE="CHANGELOG.md"
DATE_FORMAT="%Y-%m-%d"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get current version from pyproject.toml
get_current_version() {
    uv version --short 2>/dev/null || echo "0.1.0"
}

# Get latest git tag
get_latest_tag() {
    git describe --tags --abbrev=0 2>/dev/null || echo ""
}

# Get all tags sorted by version
get_all_tags() {
    git tag -l | sort -V
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
}

# Generate changelog section for a version
generate_version_section() {
    local version="$1"
    local from_ref="$2"
    local to_ref="$3"
    local date="$4"
    
    echo "## [${version}] - ${date}"
    echo ""
    
    # Get commits between references
    local commits
    if [[ "$from_ref" == "ROOT" ]]; then
        commits=$(git log --reverse --pretty=format:"%h|%s|%an|%ad" --date=short "$to_ref")
    else
        commits=$(git log --reverse --pretty=format:"%h|%s|%an|%ad" --date=short "${from_ref}..${to_ref}")
    fi
    
    # Parse commits by type
    local features=()
    local fixes=()
    local docs=()
    local chores=()
    local other=()
    
    while IFS='|' read -r hash subject author date; do
        [[ -z "$hash" ]] && continue
        
        # Extract commit type from conventional commits
        if [[ "$subject" =~ ^feat(\(.+\))?: ]]; then
            features+=("- ${subject#feat*: } ([${hash}](../../commit/${hash}))")
        elif [[ "$subject" =~ ^fix(\(.+\))?: ]]; then
            fixes+=("- ${subject#fix*: } ([${hash}](../../commit/${hash}))")
        elif [[ "$subject" =~ ^docs(\(.+\))?: ]]; then
            docs+=("- ${subject#docs*: } ([${hash}](../../commit/${hash}))")
        elif [[ "$subject" =~ ^(chore|build|ci)(\(.+\))?: ]]; then
            chores+=("- ${subject} ([${hash}](../../commit/${hash}))")
        else
            other+=("- ${subject} ([${hash}](../../commit/${hash}))")
        fi
    done <<< "$commits"
    
    # Output sections
    if [[ ${#features[@]} -gt 0 ]]; then
        echo "### 🚀 Features"
        echo ""
        printf '%s\n' "${features[@]}"
        echo ""
    fi
    
    if [[ ${#fixes[@]} -gt 0 ]]; then
        echo "### 🐛 Bug Fixes"
        echo ""
        printf '%s\n' "${fixes[@]}"
        echo ""
    fi
    
    if [[ ${#docs[@]} -gt 0 ]]; then
        echo "### 📚 Documentation"
        echo ""
        printf '%s\n' "${docs[@]}"
        echo ""
    fi
    
    if [[ ${#chores[@]} -gt 0 ]]; then
        echo "### 🧹 Maintenance"
        echo ""
        printf '%s\n' "${chores[@]}"
        echo ""
    fi
    
    if [[ ${#other[@]} -gt 0 ]]; then
        echo "### 🔧 Other Changes"
        echo ""
        printf '%s\n' "${other[@]}"
        echo ""
    fi
    
    # If no categorized commits found, show a message
    if [[ ${#features[@]} -eq 0 && ${#fixes[@]} -eq 0 && ${#docs[@]} -eq 0 && ${#chores[@]} -eq 0 && ${#other[@]} -eq 0 ]]; then
        echo "_No significant changes in this version._"
        echo ""
    fi
}

# Generate full changelog
generate_changelog() {
    local from_tag="$1"
    local to_tag="$2"
    
    log_info "Generating changelog from ${from_tag:-"beginning"} to ${to_tag:-"HEAD"}..."
    
    # Create backup if changelog exists
    if [[ -f "$CHANGELOG_FILE" ]]; then
        cp "$CHANGELOG_FILE" "${CHANGELOG_FILE}.backup"
        log_info "Created backup: ${CHANGELOG_FILE}.backup"
    fi
    
    # Start writing changelog
    cat > "$CHANGELOG_FILE" << EOF
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

EOF
    
    # If specific range requested
    if [[ -n "$from_tag" && -n "$to_tag" ]]; then
        local version=$(get_current_version)
        local date=$(date +"$DATE_FORMAT")
        generate_version_section "$version" "$from_tag" "$to_tag" "$date" >> "$CHANGELOG_FILE"
        return
    fi
    
    # Generate for current unreleased changes
    local current_version=$(get_current_version)
    local latest_tag=$(get_latest_tag)
    local current_date=$(date +"$DATE_FORMAT")
    
    if [[ -n "$latest_tag" ]]; then
        # Check if there are commits since last tag
        local commits_since_tag=$(git rev-list "${latest_tag}..HEAD" --count)
        if [[ "$commits_since_tag" -gt 0 ]]; then
            generate_version_section "$current_version" "$latest_tag" "HEAD" "$current_date" >> "$CHANGELOG_FILE"
        fi
    else
        # No tags exist, generate from first commit
        generate_version_section "$current_version" "ROOT" "HEAD" "$current_date" >> "$CHANGELOG_FILE"
    fi
    
    # Generate for all existing tags
    local tags=($(get_all_tags | tac))  # Reverse order (newest first)
    local prev_tag=""
    
    for tag in "${tags[@]}"; do
        local tag_date=$(git log -1 --format=%ad --date=short "$tag")
        local tag_version="${tag#v}"  # Remove 'v' prefix if present
        
        if [[ -z "$prev_tag" ]]; then
            # First tag - compare with previous commits
            local first_commit=$(git rev-list --max-parents=0 HEAD)
            if [[ $(git rev-list "${first_commit}..${tag}" --count) -gt 0 ]]; then
                generate_version_section "$tag_version" "ROOT" "$tag" "$tag_date" >> "$CHANGELOG_FILE"
            fi
        else
            # Compare with previous tag
            generate_version_section "$tag_version" "$prev_tag" "$tag" "$tag_date" >> "$CHANGELOG_FILE"
        fi
        
        prev_tag="$tag"
    done
}

# Main function
main() {
    check_git_repo
    
    local from_tag="${1:-}"
    local to_tag="${2:-}"
    
    generate_changelog "$from_tag" "$to_tag"
    
    log_success "Changelog generated: $CHANGELOG_FILE"
    
    # Show stats
    local lines=$(wc -l < "$CHANGELOG_FILE")
    local sections=$(grep -c "^## \[" "$CHANGELOG_FILE" || true)
    log_info "Generated $lines lines with $sections version sections"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi