# RTX6000 Metrics Proxy

Use this on the shared RTX6000 host so the public `:8000` endpoint returns:
- VM-side inference latency
- measured `energy_kwh`
- measured `co2_g`
- measured `gpu_power_w`

## Prerequisites

- vLLM container listens on host port `8001`
- proxy code exists under `/home/dogukantopcu/thesis-proxy-src`
- proxy venv exists under `/home/dogukantopcu/thesis-proxy-venv`

## Install

Copy the service file:

```bash
sudo cp infrastructure/systemd/thesis-vllm-metrics-proxy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now thesis-vllm-metrics-proxy
```

## Verify

```bash
systemctl status thesis-vllm-metrics-proxy --no-pager
journalctl -u thesis-vllm-metrics-proxy -n 50 --no-pager
curl -fsS http://127.0.0.1:8000/health | jq .
curl -fsS http://127.0.0.1:8000/v1/models | jq .
```
