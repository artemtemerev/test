from django.views.generic import (
  ListView, 
  TemplateView, 
  CreateView
)
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter 
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
from requests_oauthlib import OAuth2Session
from datetime import time

graph_url = 'https://graph.microsoft.com/v1.0'


def get_oauth2_session(request):
    """ Create OAuth2 session which autoupdates the access token if it has expired """

    # This needs to be amended to whatever your refresh_token_url is.
    refresh_token_url = AzureOAuth2Adapter.refresh_token_url
    
    social_token = SocialToken.objects.get(account__user=request.user)

    def token_updater(token):
        social_token.token = token['access_token']
        social_token.token_secret = token['refresh_token']
        social_token.expires_at = timezone.now() + timedelta(seconds=int(token['expires_in']))
        social_token.save()

    client_id = social_token.app.client_id
    client_secret = social_token.app.secret

    extra = {
        'client_id': client_id,
        'client_secret': client_secret
    }

    expires_in = (social_token.expires_at - timezone.now()).total_seconds()
    token = {
        'access_token': social_token.token,
        'refresh_token': social_token.token_secret,
        'token_type': 'Bearer',
        'expires_in': expires_in  # Important otherwise the token update doesn't get triggered.
    }

    return OAuth2Session(client_id, token=token, auto_refresh_kwargs=extra, 
                         auto_refresh_url=refresh_token_url, token_updater=token_updater)

def get_update_token(user):
  token = SocialToken.objects.get(account__user=user, account__provider='microsoft')
  expires_at = token.app.client_id

  redirect_uri = 'https://example.com/accounts/microsoft/login/callback/'
  print("expires at :", redirect_uri)
  print(token.token_secret)
  print(redirect_uri)

  if token != None:
    # Check expiration
    now = time.time()
    # Subtract 5 minutes from expiration to account for clock skew
    expire_time = expires_at - 300
    if now >= expire_time:
      pass
      # Refresh the token
      aad_auth = OAuth2Session(
        token.app.client_id,
        token = token,
        redirect_uri=redirect_uri
      )

    #  refresh_params = {
  #      'client_id': settings['app_id'],
  #      'client_secret': settings['app_secret'],
  #    }
  #    new_token = aad_auth.refresh_token(token_url, **refresh_params)

      # Save new token
  #    store_token(request, new_token)

      # Return new access token
  #    return new_token

  #  else:
      # Token still valid, just return it
  #    return token

  return str(token)

def get_calendar_events(token):
  
  token = {'access_token': token}
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,organizer,start,end',
    '$orderby': 'createdDateTime DESC'
  }

  # Send GET to /me/events
  events = graph_client.get('{0}/me/events'.format(graph_url), params=query_params)
  # Return the JSON result
  return events.json()

def get_all_users(token):
  token = {'access_token': token}
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'displayName, givenName, mail, surname, jobTitle',
  }

  # Send GET to /me/events
  users = graph_client.get('{0}/users'.format(graph_url))
  # Return the JSON result
  return users.json()

def post_event(token, **kwargs):

  token = {'access_token': token}
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'displayName, givenName, mail, surname, jobTitle',
  }

  # Send GET to /me/events
  users = graph_client.get('{0}/me/reminderView'.format(graph_url))
  # Return the JSON result
  return users.json()

class CalendarView(TemplateView):
  template_name = "users/calendar_view.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = self.request.user
    redirect_uri = 'https://example.com/accounts/microsoft/login/callback/'
    try:  
      token = get_update_token(user.pk)
      events = get_calendar_events(token)
      users = get_all_users(token)
    except:
      events = "Your account does not belong to Microsoft Office 365"
      users = "No info about users"
    context['events'] = events
    context['users'] = users
    context['redirect_uri'] = redirect_uri
    print(redirect_uri)
    return context

#class CreateCalendarEvent(CreateView):
#  model =  