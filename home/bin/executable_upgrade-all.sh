#!/usr/bin/env bash

# Enable bash strict mode:
# -e: exit on error
# -u: exit on undefined variable
# -o pipefail: exit on pipe failure
set -euo pipefail
IFS=$'\n\t'

# Uncomment line below to enable full line-by-line debugging
# set -x

## Upgrade system, compatibiity libraries, and system packages
# automatically install updates
sudo softwareupdate -i -a

# Upgrade Xcode using the xcode-select command:
# xcode-select --install

# VARs
WORKING_DIR="${HOME}/bin"

# Define array of scripts to execute
execute=(
    "${WORKING_DIR}/brewup.sh"
    "${WORKING_DIR}/helmup.sh"
    "${WORKING_DIR}/update_all_repos.sh"
    "${WORKING_DIR}/update-mise"
)

# Define array of scripts to exclude
exceptions=()

printf "\n=== Starting Script Execution ===\n"
printf "Current directory: %s\n" "${WORKING_DIR}"
# Execute whoami separately to avoid masking return value
whoami_output=$(whoami || true)
printf "User: %s\n" "${whoami_output}"
printf "Path: %s\n" "${PATH}"

# Loop through all files in current directory
for script_path in "${execute[@]}"; do
    # Skip if not both a file and not a shell script
    # Check if the file is a regular file and has a .sh extension
    if [[ ! -f "${script_path}" || "${script_path}" != *.sh ]]; then
        printf "Skipping non-shell script: %s\n" "${script_path}"
        continue
    fi

   printf "\n=== Processing Script: %s ===\n" "${script_path}"
   
   printf "Performing pre-execution checks...\n"
   
   # Skip if not a file
   if [[ ! -f "${script_path}" ]]; then
       printf "ERROR: %s is not a regular file - skipping\n" "${script_path}"
       continue
   fi
   
   # Check file permissions and type
   printf "\nFile metadata:\n"
   printf "Owner and permissions: "
   ls -l "${script_path}"
   printf "File type: "
   file "${script_path}"
   printf "First line: "
   head -n 1 "${script_path}"
   
   # Skip if not executable
   if [[ ! -x "${script_path}" ]]; then
       printf "\nERROR: %s is not executable - skipping\n" "${script_path}"
       printf "To fix: run chmod +x %s\n" "${script_path}"
       continue
   # Check if script is in exceptions array
   skip=0
   # Add null check for exceptions array
   if [[ ${#exceptions[@]} -gt 0 ]]; then
       for exception in "${exceptions[@]}"; do
               skip=1
               break
       done
   fi

   printf "\n=== Executing Script: %s ===\n" "${script_path}"
   # Execute date separately to avoid masking return value
   date_output=$(date || true)
   printf "Time: %s\n" "${date_output}"
   printf "Original directory: %s\n" "${PWD}"
   printf "Script directory: %s\n" "$(dirname "${script_path}")"
   
   printf "\n=== Executing Script: %s ===\n" "${script_path}"
   printf "Time: %s\n" "$(date)"
   printf "Original directory: %s\n" "${PWD}"
   printf "Script directory: %s\n" "$(dirname "${script_path}")"
   
   # Execute script with proper output and exit code handling
   (
       # Print script output
       printf "\nScript Output:\n%s\n" "${output}"
       
       # Exit with the script's exit code
       exit "${exit_code}"
       exit_code=$?
       
   script_status=$?
   
   if [[ "${script_status}" -ne 0 ]]; then
       # Exit with the script's exit code
       exit $exit_code
   )
   
   script_status=$?
   
   if [ $script_status -ne 0 ]; then
       printf "\n=== Script Execution Failed ===\n" >&2
       printf "Script: %s\n" "${script_path}" >&2
       printf "Exit code: %d\n" "${script_status}" >&2
       printf "\nScript contents:\n" >&2
       printf "================\n" >&2
       cat "${script_path}" >&2
       printf "\n================\n" >&2
       printf "Environment variables:\n"
       env | sort >&2
       printf "\nTo debug:\n" >&2
       printf "1. Check exit code above\n" >&2
       printf "2. Review script contents for errors\n" >&2
       printf "3. Verify all dependencies are installed\n" >&2
       printf "4. Check environment variables\n" >&2
printf "\n=== Script Execution Complete ===\n"
# Execute date separately to avoid masking return value
date_output=$(date || true)
printf "Time: %s\n" "${date_output}"
   else
       printf "\n=== Successfully Executed: %s ===\n" "${script_path}"
   fi
done

printf "\n=== Script Execution Complete ===\n"
printf "Time: %s\n" "$(date)"