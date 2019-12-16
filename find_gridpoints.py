import click
import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import LineString


@click.command()
@click.option(
    '-d',
    '--dist',
    required=True,
    type=float,
    default=None,
    show_default=True,
    help='Distance along LineString to query for grid position (in meters)')
@click.option(
    '--projection',
    required=False,
    show_default=True,
    type=int,
    default=3488,
    help=
    'EPSG code for projection used when creating buffer. Coordinates must be in meters.'
)
@click.argument(
    'files',
    required=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    nargs=-1)
def main(files, dist, projection):
    """Find NOAA NDFD gridpoints along LineString
    """
    # Load files
    gdfs = []
    for file in files:
        gdf = gpd.read_file(file)
        gdfs.append(gdf)

    # Append into one
    gdf = gpd.GeoDataFrame(
        pd.concat(gdfs, sort=False), crs={'init': 'epsg:4326'})

    # Reproject:
    gdf = gdf.to_crs(epsg=projection)

    # For each geometry interpolate at a given distance
    geometries = []
    for row in gdf.itertuples():
        interpolated = redistribute_vertices(row.geometry, dist)
        geometries.append(interpolated)

    interpolated_gdf = gpd.GeoDataFrame(
        geometry=geometries, crs={'init': f'epsg:{projection}'})
    interpolated_gdf = interpolated_gdf.to_crs(epsg=4326)

    # For each line, query at every point
    all_urls = set()
    for row in interpolated_gdf.itertuples():
        all_urls.update(find_gridpoints(row.geometry.coords))

    print('\n'.join(all_urls))


def find_gridpoints(points):
    baseurl = 'https://api.weather.gov/points/'
    headers = {'accept': 'application/geo+json'}
    forecast_urls = set()
    for point in points:
        request_url = baseurl + f'{point[1]},{point[0]}'
        r = requests.get(request_url, headers=headers)
        res = r.json()
        if res.get('properties') and res['properties'].get('forecast'):
            forecast_urls.add(res['properties']['forecast'])

    return forecast_urls


def redistribute_vertices(geom, distance):
    if geom.geom_type == 'LineString':
        num_vert = int(round(geom.length / distance))
        if num_vert == 0:
            num_vert = 1
        return LineString([
            geom.interpolate(float(n) / num_vert, normalized=True)
            for n in range(num_vert + 1)])
    elif geom.geom_type == 'MultiLineString':
        parts = [redistribute_vertices(part, distance) for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise ValueError('unhandled geometry %s', (geom.geom_type, ))


if __name__ == '__main__':
    main()
