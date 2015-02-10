from urlparse import parse_qsl, urlparse, urlunsplit
from urllib import urlencode

from clickanalysis.models import Campaign, ClickTracking
from django.http import HttpResponseRedirect


class ClickAnalysisMiddleware(object):
    """This middleware is the core logic for tracking all the clicks across the site
       We have already added campaign ids to the links which we want to track
       and this class will isolate that campaign id, if campaign id is valid, click will be
       recorded to the related campaign.
    """

    def process_request(self, request):

        if request.GET.get('cid', ''):  # Will process the logic only if campaign id is present
            try:
                campaign = Campaign.objects.get(campaign_id=request.GET['cid'])
            except Campaign.DoesNotExist:
                campaign = None

            # Clearing the cid parameter from the link or providing a clean url for user to redirect
            url_parsed = urlparse(request.get_full_path())
            get_params = parse_qsl(url_parsed.query)
            params_to_send = urlencode([(k, v) for k, v in get_params if k != 'cid'])
            url = urlunsplit(url_parsed[:3] + (params_to_send,) + url_parsed[5:])

            if campaign is not None:  # If campaign was found then here the click will be recorded
                click, created = ClickTracking.objects.get_or_create(campaign=campaign, link=url)
                click.count += 1
                click.save()

            return HttpResponseRedirect(url)
