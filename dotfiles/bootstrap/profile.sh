#!/usr/bin/env bash
# bootstrap/profile.sh — resolve the dotfiles install profile.
#
# Profiles (system-wide, orthogonal to the install/upgrade lifecycle):
#   minimal  applications installed & working; NO heavy "attachments"
#            (ollama models and any other large-data topic step).
#   full     minimal + attachments.
#
#   resolve_profile [explicit]   echoes "minimal" or "full" on STDOUT.
#
# Precedence:  explicit arg  >  saved default  >  first-run prompt (interactive)
#              >  minimal (non-interactive first run, NOT persisted).
#
# All human-facing text goes to STDERR so STDOUT is only the profile token
# (safe for `profile="$(resolve_profile "$1")"`). The saved default lives at
# ${XDG_CONFIG_HOME:-~/.config}/dotfiles/profile and is written only by an
# interactive first run; an explicit arg is a one-off override that never
# rewrites it.

profile_pref_file() {
	printf '%s/dotfiles/profile' "${XDG_CONFIG_HOME:-$HOME/.config}"
}

resolve_profile() {
	local explicit="${1:-}"
	local pref_file profile ans
	pref_file="$(profile_pref_file)"

	# 1) explicit arg — one-off override, never persisted
	case "$explicit" in
	full | minimal)
		printf '%s\n' "$explicit"
		return 0
		;;
	'') : ;;
	*)
		printf "profile: expected 'full' or 'minimal', got '%s'\n" "$explicit" >&2
		return 2
		;;
	esac

	# 2) saved default
	if [ -f "$pref_file" ]; then
		profile="$(tr -d '[:space:]' <"$pref_file")"
		case "$profile" in
		full | minimal)
			printf '%s\n' "$profile"
			return 0
			;;
		esac
	fi

	# 3) first run, no saved default — prompt if we have a TTY, else minimal
	if [ -t 0 ] && [ -t 1 ]; then
		while :; do
			printf 'First run — choose your default install/upgrade profile:\n' >&2
			printf '  [f]ull    = applications + heavy attachments (ollama models, large data)\n' >&2
			printf '  [m]inimal = applications only\n' >&2
			printf 'profile [f/m]: ' >&2
			read -r ans || ans=''
			case "$ans" in
			f | full)
				profile='full'
				break
				;;
			m | minimal)
				profile='minimal'
				break
				;;
			*) printf 'please answer f or m\n' >&2 ;;
			esac
		done
		mkdir -p "$(dirname "$pref_file")"
		printf '%s\n' "$profile" >"$pref_file"
		printf 'saved default profile = %s  (%s)\n' "$profile" "$pref_file" >&2
		printf '%s\n' "$profile"
		return 0
	fi

	# 4) non-interactive first run — safe default, not persisted
	printf 'no saved profile and non-interactive → using minimal (not persisted)\n' >&2
	printf 'minimal\n'
	return 0
}
