import requests

from calendly.exceptions import UnauthorizedError, WrongFormatInputError, ContactsLimitExceededError


class Client(object):
    url = "https://api.calendly.com/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, access_token):
        self.headers.update(Authorization=f"Bearer {access_token}")
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

    def post(self, endpoint, params=None, data=None, headers=None, json=True):
        response = self.request('POST', endpoint, params=params, data=data, headers=headers, json=json)
        return self.parse(response)

    def delete(self, endpoint, params=None):
        response = self.request('DELETE', endpoint, params=params)
        return self.parse(response)

    def request(self, method, endpoint, params=None, data=None, headers=None, json=True):
        _headers = self.headers
        if headers:
            _headers.update(headers)
        kwargs = {}
        if json:
            kwargs['json'] = data
        else:
            kwargs['data'] = data
        return requests.request(method, self.url + endpoint, params=params, headers=_headers, **kwargs)

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
