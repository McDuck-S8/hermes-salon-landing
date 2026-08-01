# gateway-service/ — Gateway Launcher

## Purpose
Contains the Windows batch launcher for the Hermes gateway service.

## Ownership
Single-file launcher. No code to maintain.

## Local Contracts
- `Hermes_Gateway.cmd` — Windows batch script to start gateway

## Work Guidance
- This is a convenience wrapper, not the gateway code itself
- Gateway source: `hermes-agent/gateway/`
- Gateway config: `~/.hermes/config.yaml`
