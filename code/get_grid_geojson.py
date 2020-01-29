import click
import geojson
import requests


@click.command()
@click.argument(
    'files',
    required=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    nargs=-1)
def main(files):
    """Get GeoJSON for grid cells
    """

    # Load files
    # Each file should be a text file where each line is like:
    # https://api.weather.gov/gridpoints/HNX/100,101/forecast
    lines = []
    for file in files:
        with open(file) as f:
            lines.extend(f.readlines())

    # Remove \n at end of each line
    lines = [l.strip() for l in lines]

    # For each url, send a request and keep the geometry and the elevation
    features = []
    for url in lines:
        r = requests.get(url)

        # Somewhat often the NWS returns 404
        if r.status_code == 404:
            continue

        d = r.json()
        geometry = d['geometry']
        if geometry['type'] != 'GeometryCollection':
            raise ValueError('not GeometryCollection')

        box = [x for x in geometry['geometries'] if x['type'] == 'Polygon'][0]
        props = {
            'forecast_url': url,
            'ele': d['properties']['elevation']['value']}
        f = geojson.Feature(geometry=box, properties=props)
        features.append(f)

    fc = geojson.FeatureCollection(features)
    click.echo(geojson.dumps(fc))


if __name__ == '__main__':
    main()
