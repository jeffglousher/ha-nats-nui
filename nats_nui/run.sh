#!/bin/sh
set -eu
umask 077
log() { printf '%s [%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" "$2"; }
log_level=$(jq -er '.log_level // "warn" | select(. == "info" or . == "warn" or . == "error")' /db/options.json 2>/dev/null) || {
    log ERROR "Invalid Log detail setting. Select info, warn, or error in Configuration and restart."
    exit 1
}
mkdir -p /db/protoschemas/default /run/nginx
chown -R nui:nui /db
nginx -t
log INFO "Starting NUI. Access is through Home Assistant ingress only."
su-exec nui /cmd/nui-web --db-path=/db --proto-schemas-path=/db/protoschemas/default --log-level="$log_level" --nats-cli-contexts= &
nui_pid=$!
nginx -g 'daemon off;' &
proxy_pid=$!
cleanup() {
    log INFO "Stopping NUI and its ingress gateway."
    kill "$nui_pid" "$proxy_pid" 2>/dev/null || true
    wait "$nui_pid" "$proxy_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM
ready=false
startup_attempts=0
while kill -0 "$nui_pid" 2>/dev/null && kill -0 "$proxy_pid" 2>/dev/null; do
    if [ "$ready" = false ] && wget -q -T 2 -O /dev/null http://127.0.0.1:31311/health 2>/dev/null; then
        log INFO "NUI is ready. Select Open Web UI in Home Assistant."
        ready=true
    fi
    if [ "$ready" = false ]; then
        startup_attempts=$((startup_attempts + 1))
        if [ "$startup_attempts" -ge 30 ]; then
            log ERROR "NUI did not become ready within the startup deadline. Check the preceding service errors."
            exit 1
        fi
    fi
    sleep 1 &
    wait $! || true
done
if ! kill -0 "$nui_pid" 2>/dev/null; then
    log ERROR "NUI service exited unexpectedly. Review the preceding errors and check data-volume space and permissions."
else
    log ERROR "Ingress gateway exited unexpectedly. Review the preceding gateway error."
fi
exit 1
