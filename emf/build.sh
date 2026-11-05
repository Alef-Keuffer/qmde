#!/usr/bin/env bash
# Runs ./mvnw with a suitable JDK, whatever JAVA_HOME the shell has.
# Tycho needs JDK 21+; the generated scripts need Python 3.12 (Qiskit Aer wheels).
#
# Usage: ./build.sh [maven args...]     (default: verify)
#   ./build.sh                              build and run every instance
#   ./build.sh verify -Dproblem=$PWD/instances/1-path.exam
#   ./build.sh generate-sources             regenerate EMF and Xtext code only
set -euo pipefail

MIN_JAVA=21
cd "$(dirname "$0")"

java_major() { # prints the major version of the java binary in $1/bin, or 0
	local v
	v=$("$1/bin/java" -version 2>&1 | head -n1 | sed -E 's/.*version "([0-9]+)(\.([0-9]+))?.*/\1 \3/') || { echo 0; return; }
	set -- $v
	if [ "${1:-0}" = 1 ]; then echo "${2:-0}"; else echo "${1:-0}"; fi
}

candidates() {
	[ -n "${JAVA_HOME:-}" ] && echo "$JAVA_HOME"
	if [ -x /usr/libexec/java_home ]; then
		/usr/libexec/java_home -v "$MIN_JAVA+" 2>/dev/null || true
	fi
	for dir in "$HOME"/Library/Java/JavaVirtualMachines/*/Contents/Home \
		/Library/Java/JavaVirtualMachines/*/Contents/Home \
		"$HOME"/.sdkman/candidates/java/* /usr/lib/jvm/*; do
		[ -d "$dir" ] && echo "$dir"
	done
}

found=""
while IFS= read -r home; do
	if [ -x "$home/bin/java" ] && [ "$(java_major "$home")" -ge "$MIN_JAVA" ]; then
		found="$home"
		break
	fi
done < <(candidates)

if [ -z "$found" ]; then
	echo "No JDK $MIN_JAVA+ found (JAVA_HOME=${JAVA_HOME:-unset})." >&2
	echo "Install one, e.g. 'sdk install java 21-tem', or set JAVA_HOME to it." >&2
	exit 1
fi
export JAVA_HOME="$found"
echo "Using JDK $(java_major "$JAVA_HOME") at $JAVA_HOME"

if ! command -v python3.12 >/dev/null 2>&1; then
	echo "warning: python3.12 not found; the generated scripts will not run (brew install python@3.12)." >&2
fi

if [ $# -eq 0 ]; then
	set -- verify
fi
exec ./mvnw -B "$@"
