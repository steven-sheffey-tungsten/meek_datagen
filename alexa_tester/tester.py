import sys

import requests

for url in sys.stdin.readlines():
    url = url.rstrip().split(',')[1]
    for protocol in ["http", "https"]:
        success = None
        resp = None
        try:
            # Make the request
            resp = requests.get("{}://{}".format(protocol, url))
            success = True
        except:
            success = False
        # Determine whether the request had a http => https redirect
        redirected_to_https = success and protocol == "http" and resp.url.split("://")[0] == "https"
        # Log the response
        sys.stdout.write("{},{},{},{}\n".format(url, protocol, success, redirected_to_https))
