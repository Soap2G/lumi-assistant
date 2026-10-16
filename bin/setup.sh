#!/usr/bin/env bash
#
# open-data-assistant setup script.
#
# Sources idempotently, works from any CWD once sourced.
# Usage (local dev):
#   source ./bin/setup.sh
#
# Usage (CVMFS, once published):
#   source /cvmfs/<repo>/<path>/latest/bin/setup.sh
#
# Effect:
#   - exports OPENCODE_CONFIG_DIR pointing at this tree's config/
#   - exports OPENCODE_DISABLE_PROJECT_CONFIG=1 so opencode ignores any
#     .opencode/ dir walked up from CWD. Comment out the line below if
#     you want project-local config to still layer on top.
#   - exports OPEN_DATA_ASSISTANT_VERSION from the VERSION file.

# Resolve the directory this script lives in, handling symlinks.
_oda_src="${BASH_SOURCE[0]:-$0}"
while [ -L "$_oda_src" ]; do
  _oda_dir="$(cd -P "$(dirname "$_oda_src")" >/dev/null 2>&1 && pwd)"
  _oda_src="$(readlink "$_oda_src")"
  [[ "$_oda_src" != /* ]] && _oda_src="$_oda_dir/$_oda_src"
done
_oda_bin="$(cd -P "$(dirname "$_oda_src")" >/dev/null 2>&1 && pwd)"
_oda_root="$(cd -P "$_oda_bin/.." >/dev/null 2>&1 && pwd)"
_oda_config="$_oda_root/config"

if [ ! -d "$_oda_config" ]; then
  echo "ERROR: open-data-assistant config not found at $_oda_config" >&2
  unset _oda_src _oda_dir _oda_bin _oda_root _oda_config
  return 1 2>/dev/null || exit 1
fi

export OPENCODE_CONFIG_DIR="$_oda_config"

# Expose helper tools shipped in bin/ (lumi-rucio-auth, ...).
case ":$PATH:" in
  *":$_oda_bin:"*) ;;
  *) export PATH="$_oda_bin:$PATH" ;;
esac

# Comment the next line out to keep project .opencode/ layering on top.
export OPENCODE_DISABLE_PROJECT_CONFIG=1

if [ -f "$_oda_root/VERSION" ]; then
  OPEN_DATA_ASSISTANT_VERSION="$(cat "$_oda_root/VERSION")"
else
  OPEN_DATA_ASSISTANT_VERSION="unknown"
fi
export OPEN_DATA_ASSISTANT_VERSION

echo "open-data-assistant v${OPEN_DATA_ASSISTANT_VERSION} ready"
echo "  OPENCODE_CONFIG_DIR=$OPENCODE_CONFIG_DIR"
echo "  OPENCODE_DISABLE_PROJECT_CONFIG=$OPENCODE_DISABLE_PROJECT_CONFIG"

# Ensure opencode's data/log dir is writable.
# opencode writes logs, sessions and cache under $XDG_DATA_HOME/opencode
# (default ~/.local/share/opencode) — separate from OPENCODE_CONFIG_DIR above.
# On some notebook/batch hosts (e.g. REANA) that path is missing or owned by
# another UID, which makes opencode abort at startup with:
#   PermissionDenied: FileSystem.open (.../opencode/log/opencode.log)
# If the target isn't writable, relocate XDG_DATA_HOME to a per-user tmp dir.
# This is a no-op when the default location already works.
_oda_data_dir="${XDG_DATA_HOME:-$HOME/.local/share}/opencode/log"
if ( mkdir -p "$_oda_data_dir" && touch "$_oda_data_dir/.oda-write-test" ) 2>/dev/null; then
  rm -f "$_oda_data_dir/.oda-write-test" 2>/dev/null
else
  _oda_fallback="${TMPDIR:-/tmp}/opencode-data-$(id -u)"
  if mkdir -p "$_oda_fallback/opencode/log" 2>/dev/null; then
    export XDG_DATA_HOME="$_oda_fallback"
    echo "  XDG_DATA_HOME=$XDG_DATA_HOME (relocated; default data dir not writable)"
  else
    echo "  WARNING: opencode data dir not writable and fallback failed;" >&2
    echo "           opencode may crash on start (set XDG_DATA_HOME manually)" >&2
  fi
fi

unset _oda_src _oda_dir _oda_bin _oda_root _oda_config _oda_data_dir _oda_fallback
