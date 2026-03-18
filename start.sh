#!/bin/bash
set -e
echo "Starting Web3 Wallet Tracker with Real-Time Analytics..."
uvicorn app:app --host 0.0.0.0 --port 9050 --workers 1
