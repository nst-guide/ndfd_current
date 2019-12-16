# Current NDFD forecasts


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
