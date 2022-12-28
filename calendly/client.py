from urllib.parse import urlencode
import requests

from calendly.exceptions import UnauthorizedError, WrongFormatInputError, ContactsLimitExceededError


class Client(object):
    URL = "https://api.calendly.com/"
    AUTH_URL = "https://auth.calendly.com/"
    AUTH_ENDPOINT = "oauth/authorize?"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, access_token=None, client_id=None, client_secret=None, redirect_uri=None):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri
        self.user_uri = None
        if access_token:
            self.set_token(access_token)

    def authorization_url(self, state=None):
        params = {
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI,
            'response_type': 'code',
        }
        if state:
            params['state'] = state
        return self.URL + self.AUTH_ENDPOINT + urlencode(params)

    def get_access_token(self, code):
        params = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }
        body = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.REDIRECT_URI
        }
        return self.post('oauth/token', params=params, data=body, auth_url=True)

    def refresh_access_token(self, refresh_token):
        params = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET
        }
        body = {
            'grant_type': 'authorization_code',
            'refresh_token': refresh_token
        } 
        return self.post('oauth/token', params=params, data=body, auth_url=True)
        
    def set_token(self, access_token):
        self.headers.update(Authorization=f"Bearer {access_token}")
        if self.user_uri is None:
            current_user = self.get_current_user()["resource"]
            self.user_uri = current_user["uri"]
            self.user_uuid = current_user["uri"].split("/")[-1]
            self.organization_uri = current_user["current_organization"]
            self.organization_uuid = current_user["current_organization"].split("/")[-1]

    def get_current_user(self):
        return self.get('users/me')

    def get_scheduled_event(self, event_uuid):
        return self.get(f'scheduled_events/{event_uuid}')

    def create_webhook(self, url, events, organization_uri, user_uri, scope):
        body = {
            "url": url,
            "events": events,
            "organization": organization_uri,
            "user": user_uri,
            "scope": scope
        }
        return self.post('webhook_subscriptions', data=body)

    def list_webhooks(self, scope, organization_uri, user_uri=None):
        params = {"scope": scope, "organization": organization_uri}
        if scope == "user":
            params.update(user=user_uri)
        webhooks = self.get('webhook_subscriptions',params=params)["collection"]
        for webhook in webhooks:
            webhook["uuid"] = webhook["uri"].split("/")[-1]
        return webhooks

    def delete_webhook(self, webhook_uuid):
        return self.delete(f'webhook_subscriptions/{webhook_uuid}')

    def get(self, endpoint, params=None):
        response = self.request('GET', endpoint, params=params)
        return self.parse(response)

    def post(self, endpoint, params=None, data=None, headers=None, json=True, auth_url=False):
        response = self.request('POST', endpoint, params=params, data=data, headers=headers, json=json, auth_url=auth_url)
        return self.parse(response)

    def delete(self, endpoint, params=None):
        response = self.request('DELETE', endpoint, params=params)
        return self.parse(response)

    def request(self, method, endpoint, params=None, data=None, headers=None, json=True, auth_url=False):
        _headers = self.headers
        if headers:
            _headers.update(headers)
        kwargs = {}
        if json:
            kwargs['json'] = data
        else:
            kwargs['data'] = data
        if auth_url:
            return requests.request(method, self.AUTH_URL + endpoint, params=params, headers=_headers, **kwargs)
        else:
            return requests.request(method, self.URL + endpoint, params=params, headers=_headers, **kwargs)

    def parse(self, response):
        status_code = response.status_code
        if 'Content-Type' in response.headers and 'application/json' in response.headers['Content-Type']:
            try:
                r = response.json()
            except ValueError:
                r = response.text
        else:
            r = response.text
        if status_code == 200:
            return r
        if status_code == 204:
            return None
        if status_code == 400:
            raise WrongFormatInputError(r)
        if status_code == 401:
            raise UnauthorizedError(r)
        if status_code == 406:
            raise ContactsLimitExceededError(r)
        if status_code == 500:
            raise Exception
        return r
