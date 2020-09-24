# Speedtest by Ookla Global Fixed and Mobile Network Performance Map Tiles

## Summary
Global fixed broadband and mobile (cellular) network performance, allocated to zoom level 16 web mercator tiles (approximately 610.8 meters by 610.8 meters at the equator). Data is provided in both Shapefile format as well as Apache Parquet with geometries represented in Well Known Text (WKT) projected in EPSG:4326. Download speed, upload speed, and latency are collected via the Speedtest by Ookla applications for Android and iOS and averaged for each tile. Measurements are filtered to results containing GPS-quality location accuracy.

## About
Speedtest data is used today by commercial fixed and mobile network operators around the world to inform network buildout, improve global Internet quality, and increase Internet accessibility. Government regulators such as the United States Federal Communications Commission and the Malaysian Communications and Multimedia Commission use Speedtest data to hold telecommunications entities accountable and direct funds for rural and urban connectivity development. Ookla licenses data to NGOs and educational institutions to fulfill its mission: to help make the internet better, faster and more accessible for everyone. By distributing this data, Ookla hopes to further this mission by increasing the ease at which individuals and organizations may utilize it for the purposes of bridging the social and economic gaps between those with and without modern Internet access.

## Data

### Overview

#### Tiles
Hundreds of millions of [Speedtests](https://www.speedtest.net/) are taken on the [Ookla](https://www.ookla.com/) platform each month. In order to create a manageable dataset, we aggregate raw data into tiles. The size of a data tile is defined as a function of "zoom level" (or "z"). At z=0, the size of a tile is the size of the whole world. At z=1, the tile is split in half vertically and horizontally, creating 4 tiles that cover the globe. This tile-splitting continues as zoom level increases, causing tiles to become exponentially smaller as we zoom into a given region. By this definition, tile sizes are actually some fraction of the width/height of Earth according to [Web Mercator projection](https://en.wikipedia.org/wiki/Web_Mercator_projection) (EPSG:3857). As such, tile size varies slightly depending on latitude, but tile sizes can be estimated in meters.

For the purposes of these layers, a zoom level of 16 (z=16) is used for the tiling. This equates to a tile that is approximately 610.8 meters by 610.8 meters at the equator (18 arcsecond blocks). The geometry of each tile is represented in [WGS 84](https://en.wikipedia.org/wiki/World_Geodetic_System) (EPSG:4326) in the `tile` field.

#### Attributes
Each tile contains the following adjoining attributes:

| Field Name   | Description                                                                                        |
|--------------|----------------------------------------------------------------------------------------------------|
| `avg_d_kbps` | The average download speed of all tests performed in the tile, represented in kilobits per second. |
| `avg_u_kbps` | The average upload speed of all tests performed in the tile, represented in kilobits per second.   |
| `avg_lat_ms` | The average latency of all tests performed in the tile, represented in milliseconds                |
| `tests`      | The number of tests taken in the tile.                                                             |
| `devices`    | The number of unique devices contributing tests in the tile.                                       |

#### Layers
Two layers are distributed:

* `gps_mobile_tiles` - Tiles containing tests taken from mobile devices with GPS-quality location and a cellular connection type (e.g. 4G LTE, 5G NR).
* `gps_fixed_tiles` - Tiles containing tests taken from mobile devices with GPS-quality location and a non-cellular connection type (e.g. WiFi, ethernet).

#### Period

Layers are generated based on a quarter of data (three months) on a quarterly basis. A `1Q2020` period would include all data generated on or after `2020-01-01` and before `2020-04-01`.

### Shapefile

The [Shapefile](https://en.wikipedia.org/wiki/Shapefile) (SHP) is a widely-adopted format for sharing geospatial data, and is supported by nearly every GIS-capable software and library. There is a .zip file for each layer:

* `gps_mobile_tiles.zip`
* `gps_fixed_tiles.zip`

Each layer .zip unarchives to contain a directory of the same name and the necessary files. E.g. `gps_mobile_tiles.zip` unarchives with the following structure:

```
gps_mobile_tiles.zip
+-- gps_mobile_tiles
|   +-- gps_mobile_tiles.dbf
|   +-- gps_mobile_tiles.prj
|   +-- gps_mobile_tiles.shp
|   +-- gps_mobile_tiles.shx
```

These files serve the following purpose:

* `.dbf` dBase file containing attributes
* `.prj` defines the spatial projection
* `.shp` contains the geometries
* `.shx` spatial index

### Parquet

The data is also available in Apache Parquet format. The available fields are described in the *Attributes* section. An additional field, `tiles` contains a [Well Known Text](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) (WKT) representation of the tile geometry. WKT is readable by many cloud tools with spatial extensions such as [Athena](https://docs.aws.amazon.com/athena/latest/ug/geospatial-input-data-formats-supported-geometry-types.html) and [Redshift](https://docs.aws.amazon.com/redshift/latest/dg/ST_GeomFromText-function.html).

## License
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
