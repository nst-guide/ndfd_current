import click
import geopandas as gpd
import requests
from shapely.geometry import LineString


@click.command()
@click.option(
    '--file',
    required=False,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    default=None,
    help=
    'Geospatial file with geometry to download data for. Will download all image tiles that intersect this geometry. Must be a file format that GeoPandas can read.'
)
@click.option(
    '-d',
    '--dist',
    required=False,
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
def main(file, dist, projection):
    """Find NOAA NDFD gridpoints along LineString
    """
    # Load file
    gdf = gpd.read_file(file)

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

        len(all_urls)

    print('\n'.join(all_urls))


def find_gridpoints(points):
    baseurl = 'https://api.weather.gov/points/'
    headers = {'accept': 'application/geo+json'}
    forecast_urls = set()
    for point in points:
        request_url = baseurl + f'{point[1]},{point[0]}'
        r = requests.get(request_url, headers=headers)
        forecast_urls.add(r.json()['properties']['forecast'])

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
