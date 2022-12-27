# calendly-python

calendly-python is an API wrapper for Calendly, written in Python

## Installing
```
pip install calendly-python
```
## Usage
```
from calendly.client import Client
client = Client('access_token')

user_uri = client.user_uri
user_uuid = client.user_uuid
organization_uri = client.organization_uri
organization_uuid = client.organization_uuid
```

If you don't have access_token you can get one using Oauth2, following the next steps:
Check https://developer.calendly.com/how-to-authenticate-with-oauth, for more info.
1. Initiate client:
```
client = Client(client_id="client_id", client_secret="client_secret", redirect_uri="redirect_uri")
```
2. Get authorization URL to get code
```
url = client.authorization_url()
```
3. Get access token using code
```
response = client.get_access_token(code)
```
4. Set access token
```
client.set_token(access_token)
```
If your access token expired, you can get a new one using refresh_token:
```
response = client.refresh_access_token(refresh_token)
```
And then set access token again...
#### Current User
```
current_user = client.get_current_user()
```
#### Get Scheduled Event
```
event = client.get_scheduled_event(event_uuid)
```
### Webhooks
#### Create webhook
```
webhook = client.create_webhook(self, url, events, organization_uri, user_uri, scope)
# events: must be a list of valid events (check calendly API)
# scope: two options: "user" or "organization"
```
#### List webhooks
 ```
webhooks = client.list_webhooks(self, scope, organization_uri, user_uri=None)
# scope: two options: "user" or "organization"
# Note: must send user_uri if scope = "user"
```
#### Delete webhook
 ```
client.delete_webhook(webhook_uuid)
 ```