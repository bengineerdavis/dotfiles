# -----------------------------------------------------------------------------
# Script Name:        vscode-wait.sh
# Description:        Waits for Visual Studio Code to fully launch before executing subsequent commands, ensuring that the editor is ready to accept input or handle arguments. This script passes all arguments to VS Code after ensuring it has started.
#
# License:            MIT
# Author:             Ben Davis <bengineerd's@gmail.com>
# Credits:            None
# Created:            2026-03-23
# Last Modified:      2026-03-23
#
# Usage:              vscode-wait.sh [arguments...]
#                     Example: vscode-wait.sh --wait --open /path/to/file.txt
#
# Notes:
#   - Requires Visual Studio Code to be installed and available in the PATH.
#   - Uses the `--wait` flag which is supported by VS Code's CLI to pause execution until the editor is fully initialized.
#   - The script assumes that `/opt/homebrew/bin/code` is the correct path to the VS Code binary on macOS with Homebrew.
#   - Does not require sudo or root privileges.
#   - If VS Code is not installed or the path is incorrect, the script will fail with a command not found error.
#
# ----------------------------------------------------------------------------

#!/usr/bin/env bash
/opt/homebrew/bin/code --wait "$@"
