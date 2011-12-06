#!/usr/bin/python2.5
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'lschumacher@google.com (Lee Schumacher)'

import urlparse
import utils

"""Handle redirect from old-style urls with host or query based repo_names to
the new path based urls.
TODO(lschumacher): delete this after we no longer require legacy redirect.
"""

# copied from utils to avoid circularity:
def strip(string):
    # Trailing nulls appear in some strange character encodings like Shift-JIS.
    return string.strip().rstrip('\0')

def get_subdomain(handler):
    """Determines the repo_name of the request based on old-style host/param."""
    if handler.ignore_repo_name:
        return None

    # The 'subdomain' query parameter always overrides the hostname.
    if strip(handler.request.get('subdomain', '')):
        return strip(handler.request.get('subdomain'))

    levels = handler.request.headers.get('Host', '').split('.')
    if len(levels) >= 4:
        # foo.person-finder.appspot.com -> subdomain 'foo'
        # bar.kpy.latest.person-finder.appspot.com -> subdomain 'bar'
        return levels[0]

def do_redirect(handler):
    """Return True when the request should be redirected."""
    return handler.config.missing_repo_redirect_enabled and \
        get_subdomain(handler)

def redirect(handler):
    """Extract the old host or param-based subdomain and redirect to new URL."""
    subdomain = get_subdomain(handler)
    if not subdomain and handler.repo_name_required:
        return handler.error(400, 'No repo_name specified')
    scheme, netloc, path, params, query, _ = \
        urlparse.urlparse(handler.request.url)
    query = utils.set_param(query, 'subdomain', None)  # remove a query param
    host = utils.get_host(netloc)
    if path.startswith('/'):
        path = path[1:]
    path = '%s/%s' % (subdomain, path)
    url = urlparse.urlunparse((scheme, host, path, params, query, ''))
    return handler.redirect(url)
