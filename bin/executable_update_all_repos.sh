#!/usr/bin/env bash

# This script pulls all changes for clean branches of all repositories found in PARENT_DIR
# It ensures that all repositories in the specified directory have the latest changes from their clean branches.
# It does not pull changes from dirty branches, nor does it commit or push any changes.

# bash strict mode
set -euo pipefail
IFS=$'\n\t'

# Uncomment line below to enable full line-by-line debugging
# set -x

# Store original directory to return to it after operations
ORIGINAL_DIR="$(pwd)"
trap 'cd "${ORIGINAL_DIR}"' EXIT

# Define paths
PARENT_DIRS="$HOME/airbyte/code"
CRON_FILE="$HOME/cron-logs/update_all_repos.log"

############################################
# Helper scripts with absolute path handling
############################################

parent_dir_exists() {
    local parent_dir="$1"
    if [ -d "$parent_dir" ]; then
        return 0
    else
        return 1
    fi
}

branch_exists() {
    local branch="$1"
    local repo="$2"
    local branch_exists
    
    # Use absolute path for git operations
    cd "${repo}" || return 1
    branch_exists="$(git branch -l "$branch")"
    
    if [ "$branch_exists" = "" ]; then
        return 1
    else
        return 0
    fi
}

branch_is_clean() {
    local branch="$1"
    local repo="$2"
    local branch_status
    
    # Use absolute path for git operations
    cd "${repo}" || return 1
    branch_status="$(git add . && git diff --quiet && git diff --cached --quiet)"
    
    if [ "$branch_status" != "" ]; then
        return 1
    else
        return 0
    fi
}

pull_branches() {
    local repo="$1"
    local REPO_NAME
    REPO_NAME="$(basename "$repo")"

    # Always cd using absolute path
    cd "${repo}" || {
        printf "Failed to access repository directory %s\n" "$repo"
        return 1
    }

    # Loop through each branch in the repo
    for branch in $(git branch --format '%(refname:short)'); do
        printf "Checking out branch %s in %s ...\n" "$branch" "$REPO_NAME"
        
        if branch_exists "$branch" "$repo"; then
            echo "Branch $branch exists in ${REPO_NAME}..."
            if branch_is_clean "$branch" "$repo"; then
                echo "Pulling changes from branch $branch in ${REPO_NAME}..."
                git switch "$branch" 2>/dev/null
                git fetch
                git pull
                printf "\n"
            else
                echo "Skipping branch $branch in ${REPO_NAME} due to uncommitted changes..."
            fi
        else
            echo "Skipping branch $branch in ${REPO_NAME} - branch does not exist..."
        fi

        printf "* Branch %s in %s is now up-to-date.\n\n" "$branch" "$REPO_NAME"
    done
}

update() {
    for parent_dir in ${PARENT_DIRS}; do
        if parent_dir_exists "$parent_dir"; then
            printf "Git repository collection's parent directory %s exists...\n\n" "$parent_dir"

            # Use find to get absolute paths of all directories
            while IFS= read -r repo; do
                if [ -d "${repo}/.git" ]; then
                    REPO_NAME="$(basename "$repo")"
                    printf "Processing %s ...\n" "$REPO_NAME"
                    printf "######## Updating %s located at %s ... ########\n\n" "$REPO_NAME" "$repo"
                    pull_branches "$repo"
                fi
            done < <(find "$parent_dir" -maxdepth 1 -type d)
        else
            echo "Git repository collection's parent directory $parent_dir does not exist..."
            continue
        fi
    done
}

main() {
    START_DATETIME_STAMP="$(date +'%Y-%m-%d %H:%M:%S')"
    printf "\n######## Starting update_all_repos.sh at %s ########\n\n" "$START_DATETIME_STAMP"

    update

    END_DATETIME_STAMP="$(date +'%Y-%m-%d %H:%M:%S')"
    printf "\n\n######## Ending update_all_repos.sh at %s ########\n" "$END_DATETIME_STAMP"
}

main >> "$CRON_FILE" 2>&1