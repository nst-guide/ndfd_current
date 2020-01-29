"""
Script to run on AWS lambda to update weather forecasts
"""

import gzip
import json
from io import BytesIO
from urllib.parse import urlparse
from zipfile import ZIP_DEFLATED, ZipFile

import boto3
import requests

s3 = boto3.resource('s3')


def lambda_handler(event, context):
    sections = ['ca_south', 'ca_central', 'ca_north', 'or', 'wa']

    for section in sections:
        print(f'Updating section: {section}')
        update_forecasts(section)


def update_forecasts(section):
    """Update S3 with current NDFD forecasts
    """

    with open(f'{section}.txt') as f:
        lines = f.readlines()

    lines = [x.strip() for x in lines]

    buffer = BytesIO()
    with ZipFile(buffer, 'w', ZIP_DEFLATED) as zf:
        for url in lines:
            print(f'Downloading url: {url}')

            # Get forecast and store as minified JSON string
            r = requests.get(url)
            # Somewhat often the NWS returns 404
            if r.status_code == 404:
                continue
            json_string = json.dumps(r.json(), separators=(',', ':'))

            # Get the path after the weather.gov url, i.e.:
            # gridpoints/LOX/145,76/forecast
            identifier = urlparse(url).path.lstrip('/') + '.geojson'

            # Add to ZipFile
            # Make sure to add the _non-compressed_ string to the zipfile
            # because the zipfile is compressed itself
            zf.writestr(identifier, json_string)

            # Write individual GeoJSON file to S3
            # Now we compress it since it's already been added to zipfile
            # 2-hour cache plus 24-hour stale-while-revalidate
            compressed = gzip.compress(json_string.encode('utf-8'))
            obj = s3.Object('tiles.nst.guide', f'ndfd_current/{identifier}')
            obj.put(
                Body=compressed,
                ContentType='application/geo+json',
                ACL='public-read',
                ContentEncoding='gzip',
                CacheControl='public, max-age=7200, stale-while-revalidate=86400'
            )

    # Write ZipFile to S3
    # Note that this has to be after the ZipFile has closed, aka outside the
    # context manager
    buffer.seek(0)
    obj = s3.Object('tiles.nst.guide', f'ndfd_current/{section}.zip')
    obj.put(
        Body=buffer,
        ContentType='application/zip',
        ACL='public-read',
        CacheControl='public, max-age=7200, stale-while-revalidate=86400')
