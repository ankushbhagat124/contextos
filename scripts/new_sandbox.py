"""Create a fresh browser sandbox through its supported API, preserving old data."""
import argparse
import urllib.request
import http.cookiejar

parser = argparse.ArgumentParser(description='Create a fresh demo sandbox; does not delete existing workspaces.')
parser.add_argument('--url', default='http://127.0.0.1:8000')
args = parser.parse_args()
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
with opener.open(args.url.rstrip('/') + '/api/workspace', timeout=15) as response:
    if response.status != 200:
        raise SystemExit('Workspace creation failed.')
print('Fresh isolated sandbox created successfully. For a fresh browser demo, use a private browser window.')
print('Existing data was preserved. No session bearer values are printed.')
