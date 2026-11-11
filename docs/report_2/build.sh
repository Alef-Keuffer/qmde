#!/usr/bin/env bash
# Builds report_2.pdf: syncs the Continuous Page template, fetches the EMF results from CI, generates the
# tables, Appendix A, the EMF metamodel diagrams and emf/CONTEXT.md's results table (generate.py), then runs
# latexmk, and checks the prose's claims against their evidence (verify.py). It does not run the chains:
# emf/build.sh does. Needs TeX Live (LuaLaTeX, BibTeX), python3, pdftotext and gh.
#
# Usage: ./build.sh [final] [--run <id> | --results <dir>]
#   ./build.sh                  the results of the newest emf.yml run of this branch that uploaded emf-results
#   ./build.sh --run <id>       the results of that CI run (e.g. a pull request's)
#   ./build.sh --results <dir>  the results of a local run (emf/out after emf/build.sh): the tables say so
#                               and count as placeholders, and emf/CONTEXT.md is left as it is
#   ./build.sh final ...        fails while any placeholder remains or verify.py reports a claim
# With no emf-results artifact on this branch yet, the committed tables are kept; a gh error stops the build.
set -euo pipefail
cd "$(dirname "$0")"

final="" run="" results=""
while [ $# -gt 0 ]; do
	case "$1" in
	final) final=1 ;;
	--run) run="$2"; shift ;;
	--results) results="$(cd "$2" && pwd)"; shift ;;
	*) echo "usage: $0 [final] [--run <id> | --results <dir>]" >&2; exit 2 ;;
	esac
	shift
done

# The template's own repository, where it is present, is the source of the vendored copy.
template="${MY_TEX_TEMPLATES:-$HOME/Documents/repos/my-tex-templates}/continuous-page"
if [ -d "$template" ]; then
	cp "$template/continuous-page.sty" "$template/continuous-page.lua" .
fi

set --
if [ -n "$results" ]; then
	set -- --results "$results"
else
	branch=$(git rev-parse --abbrev-ref HEAD)
	if [ -z "$run" ]; then
		# Every page, newest first by date: the API lists artifacts 30 a page, not in creation order.
		run=$(gh api --paginate 'repos/{owner}/{repo}/actions/artifacts?name=emf-results&per_page=100' --jq \
			'.artifacts[] | select(.expired | not) | [.created_at, .workflow_run.id, .workflow_run.head_branch] | @tsv' |
			sort -r | awk -F '\t' -v branch="$branch" '$3 == branch && !run { run = $2 } END { print run }')
	fi
	if [ -n "$run" ]; then
		dir=$(mktemp -d)
		trap 'rm -rf "$dir"' EXIT
		gh run download "$run" --name emf-results --dir "$dir"
		set -- --results "$dir" --run-url "$(gh run view "$run" --json url --jq .url)"
	else
		echo "No emf-results artifact on $branch yet: keeping the committed result tables." >&2
	fi
fi
python3 generate.py "$@"
python3 verify.py && verified=1 || verified="" # after generate.py: claims quote its tables

export max_print_line=10000 # one log line per placeholder
latexmk -lualatex -interaction=nonstopmode -halt-on-error report_2.tex

if [ -n "$final" ] && grep '^Placeholder: ' report_2.log >&2; then
	echo "final: the placeholders above remain." >&2
	exit 1
fi
if [ -n "$final" ] && [ -z "$verified" ]; then
	echo "final: verify.py's claims above lack evidence (the verify-report skill)." >&2
	exit 1
fi
