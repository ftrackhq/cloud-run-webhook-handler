This repository is an example of how to add automations to your ftrack workspace
using webhooks.

We will do this by creating a webhook in ftrack and a cloud run in Google Cloud.
The cloud run will receive the webhooks and then use the ftrack python api
client to make changes in ftrack.

# Requirements
* Basic python knowledge
* Google Cloud account
* A virtual python env with Poetry installed

# Setup

```
poetry install
```

# Run.

```
export FTRACK_API_KEY=MY-API-KEY
export FTRACK_API_USER=MY-USERNAME
export FTRACK_SERVER=https://MY-WORKSPACE.ftrackapp.com

uvicorn webhook_handler.main:app --reload
```

# Local development with ngrok.

```
ngrok http --region eu 127.0.0.1:8000
```

# Deploy.

```
poetry export -f requirements.txt --output requirements.txt
gcloud run deploy ftrack-webhook-handler --port 8080 --allow-unauthenticated --set-env-vars FTRACK_API_KEY=$FTRACK_API_KEY,FTRACK_API_USER=$FTRACK_API_USER,FTRACK_SERVER=$FTRACK_SERVER --source . --project=my-google-cloud-project
```

When deploying the service you have to allow unauthenticated requests.

# Add webhook to ftrack.

```
import ftrack_api

session = ftrack_api.Session()

automation = session.create('Automation', {
    'name': 'Version changes',
})

webhook = session.create('WebhookAction', {
        'automation_id': automation['id'],
        "webhook_url": "https://cce3-155-4-19-67.ngrok.io"
})

trigger = session.create('Trigger', {
    'automation_id': automation['id'],
    'filter': "entity.entity_type = AssetVersion",
})

session.commit()
```
