This repository is an example of how to add automations to your ftrack workspace
using webhooks.

We will do this by creating a webhook in ftrack and a cloud run in Google Cloud.
The cloud run will receive the webhooks and then use the ftrack python api
client to make changes in ftrack.

# Requirements
* Basic python knowledge
* Google Cloud account
* A virtual python env with Poetry
* ngrok
* gcloud

# Setup

```
poetry install
```

# Run locally

```
export FTRACK_API_KEY=MY-API-KEY
export FTRACK_API_USER=MY-USERNAME
export FTRACK_SERVER=https://MY-WORKSPACE.ftrackapp.com
export FTRACK_SECRET=my-secret-key

uvicorn webhook_handler.main:app --reload
```

# Local development with ngrok

```
ngrok http --region eu 127.0.0.1:8000
```

# Deploy to Google Cloud

```
export FTRACK_API_KEY=MY-API-KEY
export FTRACK_API_USER=MY-USERNAME
export FTRACK_SERVER=https://MY-WORKSPACE.ftrackapp.com
export FTRACK_SECRET=my-secret-key

gcloud run deploy ftrack-webhook-handler --port 8080 --allow-unauthenticated --set-env-vars FTRACK_API_KEY=$FTRACK_API_KEY,FTRACK_API_USER=$FTRACK_API_USER,FTRACK_SERVER=$FTRACK_SERVER,FTRACK_SECRET=$FTRACK_SECRET --source . --project=my-google-cloud-project
```

When deploying the service you have to allow unauthenticated requests.

# Add webhook to ftrack

```
import json

import ftrack_api

session = ftrack_api.Session()

automation = session.create("Automation", {
    "name": "Version changes",
})

webhook = session.create("WebhookAction", {
        "automation_id": automation["id"],
        "webhook_url": "https://URL-TO-NGROK-OR-CLOUDRUN",
        "headers": json.dumps({
            "ftrack-secret": "my-secret-key"
        })
})

trigger = session.create("Trigger", {
    "automation_id": automation["id"],
    "filter": 'entity.entity_type = "AssetVersion" and entity.operation = "update" and entity.new.status_id != entity.old.status_id',
})

session.commit()
```
