# Transient Analyzer

A minimalist live voltage/current dashboard. The browser connects to a BLE peripheral with Web Bluetooth and relays each sample to a Python FastAPI backend.

## Run locally

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open <http://localhost:8000> in Chrome or Edge. Web Bluetooth requires a secure context; `localhost` qualifies. Use **Run demo** to preview the chart without hardware.

## Share a temporary online demo

With the FastAPI server running, open a second terminal in the project root and run:

```powershell
.\tools\cloudflared.exe tunnel --url http://127.0.0.1:8000
```

Open the `https://*.trycloudflare.com` URL printed by the command. This quick tunnel is temporary: its URL changes when restarted and stops working when the tunnel process exits. Anyone with the URL can access the demo, so use it for testing only.

## BLE protocol

Use a BLE GATT service and notify characteristic. The default UUIDs match common UART-style BLE modules:

- Service: `0000ffe0-0000-1000-8000-00805f9b34fb`
- Notify characteristic: `0000ffe1-0000-1000-8000-00805f9b34fb`

The peripheral sends UTF-8 JSON Lines: one JSON object per line, terminated by `\n`. Notifications may split a line across packets; the page buffers until newline. Example:

```json
{"voltage":3.284,"current":0.142,"sequence":501,"device_id":"rlc-01","timestamp":"2026-11-16T04:15:30.125Z"}
```

`voltage` is volts and `current` is amperes. `sequence`, `device_id`, and `timestamp` are optional; timestamp is ISO 8601 UTC. Use a compact BLE payload or binary framing if sending at high sample rates; this starter protocol is intended for moderate-rate telemetry.

## HTTP API

- `POST /api/v1/samples` accepts a JSON sample and broadcasts it to connected `/api/v1/ws` clients.
- `GET /api/v1/samples?limit=300` returns recent in-memory samples (up to 600).
- `GET /api/v1/health` is a health check.
- `WS /api/v1/ws` emits a history message when connected, then each new sample.

## Project layout

```text
app/
  api/routes.py           # Versioned HTTP and WebSocket endpoints
  schemas/sample.py       # Pydantic sample contracts
  services/sample_store.py # In-memory history and live clients
  static/                 # Static assets
  templates/index.html    # Dashboard UI
  main.py                 # FastAPI app setup and page route
requirements.txt
README.md
```

Samples are held in memory and reset when the server restarts. Before deployment, restrict CORS, serve over HTTPS, and persist data if session history must survive restarts.
