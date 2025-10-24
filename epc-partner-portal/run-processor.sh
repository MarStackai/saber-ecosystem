#!/bin/bash
# EPC Processor Runner Script - Reads config from config.json

CONFIG_FILE="/home/marstack/saber_business_ops/config.json"

# Extract values from config
SITE_URL=$(jq -r '.SharePoint.SiteUrl' "$CONFIG_FILE")
CLIENT_ID=$(jq -r '.SharePoint.ClientId' "$CONFIG_FILE")
TENANT=$(jq -r '.SharePoint.Tenant' "$CONFIG_FILE")

# Run the processor
/snap/bin/pwsh -File /home/marstack/saber_business_ops/scripts/process-epc.ps1 \
  -SiteUrl "$SITE_URL" \
  -ClientId "$CLIENT_ID" \
  -Tenant "$TENANT"