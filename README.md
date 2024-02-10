# Speedtest by Ookla Global Fixed and Mobile Network Performance Map Tiles

![world map of Ookla open data](img/open-data-github-header.png)

## Summary
This [dataset](https://registry.opendata.aws/speedtest-global-performance/) provides global fixed broadband and mobile (cellular) network performance metrics in zoom level 16 web mercator tiles (approximately 610.8 meters by 610.8 meters at the equator). Data is provided in both Shapefile format as well as Apache Parquet with geometries represented in Well Known Text (WKT) projected in EPSG:4326. Download speed, upload speed, and latency are collected via the Speedtest by Ookla applications for Android and iOS and averaged for each tile. Measurements are filtered to results containing GPS-quality location accuracy.

## About
Speedtest data is used today by commercial fixed and mobile network operators around the world to inform network buildout, improve global Internet quality, and increase Internet accessibility. Government regulators such as the United States Federal Communications Commission and the Malaysian Communications and Multimedia Commission use Speedtest data to hold telecommunications entities accountable and direct funds for rural and urban connectivity development. Ookla licenses data to NGOs and educational institutions to fulfill its mission: to measure, understand, and help improve connected experiences for all. Ookla hopes to further this mission by distributing the data to make it easier for individuals and organizations to use it for the purposes of bridging the social and economic gaps between those with and without modern Internet access.

## Data

### Overview

#### Tiles
Hundreds of millions of measurements are taken on [Ookla](https://www.ookla.com/)'s [Speedtest](https://www.speedtest.net/) platform each month. In order to create a manageable dataset, we aggregate raw data into tiles. The size of a data tile is defined as a function of "zoom level" (or "z"). At z=0, the size of a tile is the size of the whole world. At z=1, the tile is split in half vertically and horizontally, creating 4 tiles that cover the globe. This tile-splitting continues as zoom level increases, causing tiles to become exponentially smaller as we zoom into a given region. By this definition, tile sizes are actually some fraction of the width/height of Earth according to [Web Mercator projection](https://en.wikipedia.org/wiki/Web_Mercator_projection) (EPSG:3857). As such, tile size varies slightly depending on latitude, but tile sizes can be estimated in meters.

For the purposes of these layers, a zoom level of 16 (z=16) is used for the tiling. This equates to a tile that is approximately 610.8 meters by 610.8 meters at the equator (18 arcsecond blocks). The geometry of each tile is represented in [WGS 84](https://en.wikipedia.org/wiki/World_Geodetic_System) (EPSG:4326) in the `tile` field.

#### Update Cadence

The tile aggregates start in Q1 2019 and go through the most recently completed quarter (Q4 2023). They will be updated shortly after the conclusion of the quarter.

#### Tile Attributes
Each tile contains the following adjoining attributes:

| Field Name        | Type        | Description                                                                                                                             | Notes                                                                                                                                                                              |
|-------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `avg_d_kbps`      | Integer     | The average download speed of all tests performed in the tile, represented in kilobits per second.                                      |                                                                                                                                                                                    |
| `avg_u_kbps`      | Integer     | The average upload speed of all tests performed in the tile, represented in kilobits per second.                                        |                                                                                                                                                                                    |
| `avg_lat_ms`      | Integer     | The average latency of all tests performed in the tile, represented in milliseconds                                                     |                                                                                                                                                                                    |
| `avg_lat_down_ms` | Integer     | The average latency under load of all tests performed in the tile as measured during the download phase of the test. Represented in ms. | Parquet-only. Added 2023-02-23 beginning in Q4 2022 dataset. This column is sparsely populated-- some rows will have a null value as not all versions of Speedtest can perform this measurement. |
| `avg_lat_up_ms`   | Integer     | The average latency under load of all tests performed in the tile as measured during the upload phase of the test. Represented in ms.   | Parquet-only. Added 2023-02-23 beginning in Q4 2022 dataset. This column is sparsely populated-- some rows will have a null value as not all versions of Speedtest can perform this measurement. |
| `tests`           | Integer     | The number of tests taken in the tile. |
| `devices`         | Integer     | The number of unique devices contributing tests in the tile. |
| `quadkey`         | Text        | The quadkey representing the tile.  |
| `tile_x`			| Numeric	  | X coordinate of the tile's centroid.| Added 2023-07-01 beginning in the Q3 2023 dataset.
| `tile_y`          | Numeric     | Y coordinate of the tile's centroid.| Added 2023-07-01 beginning in the Q3 2023 dataset.


#### Quadkeys

[Quadkeys](https://docs.microsoft.com/en-us/bingmaps/articles/bing-maps-tile-system) can act as a unique identifier for the tile. This can be useful for joining data spatially from multiple periods (quarters), creating coarser spatial aggregations without using geospatial functions, spatial indexing, partitioning, and an alternative for storing and deriving the tile geometry.

#### Layers
Two layers are distributed as separate sets of files:

* `performance_mobile_tiles` - Tiles containing tests taken from mobile devices with GPS-quality location and a cellular connection type (e.g. 4G LTE, 5G NR).
* `performance_fixed_tiles` - Tiles containing tests taken from mobile devices with GPS-quality location and a non-cellular connection type (e.g. WiFi, ethernet).

#### Time Period and Update Frequency

Layers are generated based on a quarter year of data (three months) and files will be updated and added on a quarterly basis. A `/year=2020/quarter=1/` period, the first quarter of the year 2020, would include all data generated on or after `2020-01-01` and before `2020-04-01`.

Data is subject to be reaggregated regularly in order to honor Data Subject Access Requests (DSAR) as is applicable in certain jurisdictions under laws including but not limited to General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), and Lei Geral de Proteção de Dados (LGPD). Therefore, data accessed at different times may result in variation in the total number of tests, tiles, and resulting performance metrics.

## Data Formats

### Shapefile

The [Shapefile](https://en.wikipedia.org/wiki/Shapefile) (SHP) is a widely-adopted format for sharing geospatial data, and is supported by nearly every GIS-capable software and library. There is a .zip file for each layer:

* `2020-04-01_performance_mobile_tiles.zip`
* `2020-04-01_performance_fixed_tiles.zip`

Each layer .zip unarchives to contain a directory of the same name and the necessary files. E.g. `gps_mobile_tiles.zip` unarchives with the following structure:

```
2020-04-01_performance_mobile_tiles.zip
+-- 2020-04-01_performance_mobile_tiles
|   +-- 2020-04-01_performance_mobile_tiles.dbf
|   +-- 2020-04-01_performance_mobile_tiles.prj
|   +-- 2020-04-01_performance_mobile_tiles.shp
|   +-- 2020-04-01_performance_mobile_tiles.shx
```

These files serve the following purpose:

* `.dbf` dBase file containing attributes
* `.prj` defines the spatial projection
* `.shp` contains the geometries
* `.shx` spatial index

### Parquet

The data is also available in Apache Parquet format. The available fields are described in the *Attributes* section. An additional field, `tiles` contains a [Well Known Text](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) (WKT) representation of the tile geometry. WKT is readable by many cloud tools with spatial extensions, such as [Athena](https://docs.aws.amazon.com/athena/latest/ug/geospatial-input-data-formats-supported-geometry-types.html) and [Redshift](https://docs.aws.amazon.com/redshift/latest/dg/ST_GeomFromText-function.html).

## Data Access

### Access via S3

The performance datasets are available via [AWS S3](https://aws.amazon.com/s3/) at the `s3://ookla-open-data` bucket, where individual [Parquet](https://parquet.apache.org/) time series and compressed Shapefiles are organized by

1. file format (`shapefiles` or `parquet`)
2. service type (`fixed` or `mobile`)
3. year (`2020`)
4. quarter (for example, `1` corresponds to the Q1 period starting `2020-01-01`)

Individual downloads for fixed or mobile network performance aggregates (map tiles) for a given quarter can be located based on the following object key naming pattern:

s3://ookla-open-data/**FORMAT**/performance/type=**TYPE**/year=**YYYY**/quarter=**Q**/**FILENAME**

For example, to access all of the files for fixed and mobile service types for the second quarter of the year 2023, one would use the following S3 URIs:

Shapefiles:

* `s3://ookla-open-data/shapefiles/performance/type=mobile/year=2023/quarter=4/2023-10-01_performance_mobile_tiles.zip`
* `s3://ookla-open-data/shapefiles/performance/type=fixed/year=2023/quarter=4/2023-10-01_performance_fixed_tiles.zip`

parquet files:

* `s3://ookla-open-data/parquet/performance/type=mobile/year=2023/quarter=4/2023-10-01_performance_mobile_tiles.parquet`
* `s3://ookla-open-data/parquet/performance/type=fixed/year=2023/quarter=4/2023-10-01_performance_fixed_tiles.parquet`


### Download via URL

Files can also be downloaded directly by clicking on the following URLs:

Esri Shapefiles:

* https://ookla-open-data.s3.amazonaws.com/shapefiles/performance/type=mobile/year=2023/quarter=4/2023-10-01_performance_mobile_tiles.zip
* https://ookla-open-data.s3.amazonaws.com/shapefiles/performance/type=fixed/year=2023/quarter=4/2023-10-01_performance_fixed_tiles.zip

Apache Parquet:

* https://ookla-open-data.s3.amazonaws.com/parquet/performance/type=mobile/year=2023/quarter=4/2023-10-01_performance_mobile_tiles.parquet
* https://ookla-open-data.s3.amazonaws.com/parquet/performance/type=fixed/year=2023/quarter=4/2023-10-01_performance_fixed_tiles.parquet

### Download via CLI

S3 objects can also be downloaded via the AWS CLI. See these instructions for [installing AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).  

Using the object keys described above, the following bash script downloads a shapefile (`2023-10-01_performance_fixed_tiles.zip`) for fixed performance tiles aggregated over Q4 2023 using [aws s3 cp](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3/cp.html).

```bash
#!/usr/bin/env bash
export FORMAT='shapefiles' # (shapefiles|parquet)
export TYPE='fixed'        # (fixed|mobile)
export YYYY='2023'         # 2019,2020,2021,2022,2023
export Q='4'               # 1,2,3,4 (to date)
aws s3 cp s3://ookla-open-data/${FORMAT}/performance/type=${TYPE}/year=${YYYY}/quarter=${Q}/ . \
--recursive \
--no-sign-request
```


To download the 2023 Q4 mobile and fixed time series datasets, we can also specify the full S3 URI to download the objects:

``` bash
#!/usr/bin/env bash
# Mobile 2023 Q4
aws s3 cp s3://ookla-open-data/parquet/performance/type=mobile/year=2023/quarter=4/2023-10-01_performance_mobile_tiles.parquet --no-sign-request
# Fixed 2023 Q4
aws s3 cp s3://ookla-open-data/parquet/performance/type=fixed/year=2023/quarter=4/2023-10-01_performance_fixed_tiles.parquet --no-sign-request
```


### R Package

If using R, the [ooklaOpenDataR](https://github.com/teamookla/ooklaOpenDataR) package provides functions for accessing and working with the datasets.

## Tutorials

[Using Python to analyze download speeds in Kentucky counties](tutorials/python/aggregate_by_county/aggregate_by_county_py.ipynb)

[Using Python to filter tiles by centroids with parquet](tutorials/python/filter_by_centroids/centroids.ipynb)

[Using R to create your own maps with Ookla Open Datasets](https://www.ookla.com/articles/best-ookla-open-data-projects-2021)

[Using R to analyze download speeds in Kentucky counties](tutorials/R/aggregate_by_county/aggregate_by_county.md)

[Using R to filter tiles by location with parquet](tutorials/R/filter_parquet_bounding_box/filter_parquet_bounding_box.md)

[Using R to filter tiles by centroids with parquet](https://www.ookla.com/articles/ookla-for-good-centroid-coordinates)

## License
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Suggested Attribution

Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps was accessed on [DAY MONTH YEAR] from [AWS](https://aws.amazon.com/marketplace/pp/prodview-breawk6ljkovm#resources). Based on [LICENSEE’S] analysis of Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps for [DATA TIME PERIOD]. Ookla trademarks used under license and reprinted with permission.

## Change Log

* **2023-02-23** Loaded latency values added as `avg_lat_down_ms` and `avg_lat_up_ms`. [Loaded latency](https://www.ookla.com/articles/introducing-loaded-latency#:~:text=The%20loaded%20latency%20test%20measures,it%20is%20not%20in%20use.) measures how network load impacts network responsiveness, or latency. These values are only available in Parquet format.

* **2023-07-01** Centroid coordinate values for tiles added as `tile_x` and `tile_y`. 