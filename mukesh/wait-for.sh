#!/usr/bin/env bash
#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <host> <port1> [port2 ...] -- <cmd> [args...]"
  echo "Example: $0 host.docker.internal 5432 27017 -- uvicorn filterservice-v2:app --host 0.0.0.0 --port 8001"
  exit 1
fi

HOST="$1"
shift

# Collect ports until the '--' separator
PORTS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --)
      shift
      break
      ;;
    *)
      PORTS+=("$1")
      shift
      ;;
  esac
done

if [ "${#PORTS[@]}" -eq 0 ]; then
  echo "No ports specified to wait for."
  exit 1
fi

if [ "$#" -eq 0 ]; then
  echo "No command specified to run after waiting."
  exit 1
fi

CMD=("$@")

check_port() {
  local host="$1"; local port="$2"
  python - <<PY
import socket,sys
host = "$host"
port = int("$port")
s = socket.socket()
s.settimeout(2)
try:
    s.connect((host,port))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
}

for p in "${PORTS[@]}"; do
  echo -n "Waiting for $HOST:$p"
  until check_port "$HOST" "$p"; do
    echo -n '.'
    sleep 1
  done
  echo " ok"
done

# Exec the command
exec "${CMD[@]}"
