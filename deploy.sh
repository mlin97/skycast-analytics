#!/bin/bash
# Deployment script for SkyCast Analytics to Google Cloud Run

# Exit on error
set -e

APP_NAME="skycast-analytics"
REGION="us-central1" # You can change this to your preferred region

echo "🌤️  Deploying $APP_NAME to Google Cloud Run..."

# 1. Project ID check
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No Google Cloud project selected."
    echo "👉 Run 'gcloud config set project <YOUR_PROJECT_ID>' first."
    exit 1
fi
echo "✅ Using Project ID: $PROJECT_ID"

# 2. Deploy using source
# This builds the container specifically for Cloud Run using the Dockerfile
echo "🚀 Deploying to Cloud Run (this may take a few minutes)..."

gcloud run deploy $APP_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --port 8501

echo "✨ Deployment Complete!"
