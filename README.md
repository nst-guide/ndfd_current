# Current NOAA NDFD forecasts

The National Weather Service creates forecasts for a grid of cells 2.5km on each
side that span the entire United States. That means that if you select any point
in the continental United States, it'll be a part of one of these grid cells.
You can see it on the web using their [web
portal](https://forecast.weather.gov/MapClick.php?lon=-119.31320821939654&lat=37.881631297141496).

All the data on that web portal is also exposed through their APIs. I use those
APIs to serve regularly-updated weather forecasts through the website and mobile
app.

The URLs to query these _gridpoints_, the centroids of each of these cells, have
the local station identifier as well, i.e.:
```
https://api.weather.gov/gridpoints/PQR/138,104/forecast
```
Because of this, I first need to query the `points/` API endpoint with a series
of lat/lon coordinates to find the URLs to later ping for the actual forecasts.

`find_gridpoints.py` takes a LineString geometry and a distance and retrieves
the URLs for the grid cells corresponding to a point along that LineString every
`dist` meters.

`lambda.py` is a small function that is run on AWS lambda to very cheaply update
my S3 bucket with the latest version of the forecasts. Even without the Lambda
free tier, the code takes about 4 minutes to run, and if I ran it every 4 hours,
it would cost 15 cents per month.

`lambda.py` uploads both individual GeoJSON files and zipped archives of
GeoJSONs per trail section. Individual GeoJSON files would be easiest to
transmit via the web API, and the zipped files would allow for bulk downloads
for offline use in the mobile app.

## Usage

```
> python find_gridpoints.py --help
Usage: find_gridpoints.py [OPTIONS] FILES...

  Find NOAA NDFD gridpoints along LineString

Options:
  -d, --dist FLOAT      Distance along LineString to query for grid position
                        (in meters)  [required]
  --projection INTEGER  EPSG code for projection used when creating buffer.
                        Coordinates must be in meters.  [default: 3488]
  --help                Show this message and exit.
```

So to get the gridpoints for 10km intervals of the five sections of the PCT:
```
export DATA_DIR=...
python find_gridpoints.py \
    --dist 10000 \
    $DATA_DIR/CA_Sec_A_tracks.geojson \
    $DATA_DIR/CA_Sec_B_tracks.geojson \
    $DATA_DIR/CA_Sec_C_tracks.geojson \
    $DATA_DIR/CA_Sec_D_tracks.geojson \
    $DATA_DIR/CA_Sec_E_tracks.geojson \
    > ca_south.txt
python find_gridpoints.py \
    --dist 10000 \
    $DATA_DIR/CA_Sec_F_tracks.geojson \
    $DATA_DIR/CA_Sec_G_tracks.geojson \
    $DATA_DIR/CA_Sec_H_tracks.geojson \
    $DATA_DIR/CA_Sec_I_tracks.geojson \
    $DATA_DIR/CA_Sec_J_tracks.geojson \
    $DATA_DIR/CA_Sec_K_tracks.geojson \
    > ca_central.txt
python find_gridpoints.py \
    --dist 10000 \
    $DATA_DIR/CA_Sec_L_tracks.geojson \
    $DATA_DIR/CA_Sec_M_tracks.geojson \
    $DATA_DIR/CA_Sec_N_tracks.geojson \
    $DATA_DIR/CA_Sec_O_tracks.geojson \
    $DATA_DIR/CA_Sec_P_tracks.geojson \
    $DATA_DIR/CA_Sec_Q_tracks.geojson \
    $DATA_DIR/CA_Sec_R_tracks.geojson \
    > ca_north.txt
python find_gridpoints.py \
    --dist 10000 \
    $DATA_DIR/OR_Sec_B_tracks.geojson \
    $DATA_DIR/OR_Sec_C_tracks.geojson \
    $DATA_DIR/OR_Sec_D_tracks.geojson \
    $DATA_DIR/OR_Sec_E_tracks.geojson \
    $DATA_DIR/OR_Sec_F_tracks.geojson \
    $DATA_DIR/OR_Sec_G_tracks.geojson \
    > or.txt
python find_gridpoints.py \
    --dist 10000 \
    $DATA_DIR/WA_Sec_H_tracks.geojson \
    $DATA_DIR/WA_Sec_I_tracks.geojson \
    $DATA_DIR/WA_Sec_J_tracks.geojson \
    $DATA_DIR/WA_Sec_K_tracks.geojson \
    $DATA_DIR/WA_Sec_L_tracks.geojson \
    > wa.txt
```
