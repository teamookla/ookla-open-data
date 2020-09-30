Filtering tiles by location (with parquet)
================

``` r
library(tidyverse)
library(sf)
library(slippymath)
library(arrow)
```

## Finding a boundary file

There are a few ways to get a basemap to filter the Speedtest data with:

1.  Upload your own shapefile
2.  Use an R package like `tigris` that connects to an API with
    shapefiles (the Census Bureau API in the case of `tigris`)
3.  Use OpenStreetMap to get boundary files
4.  Find an open data portal with shapefiles

<!-- end list -->

  - The **government** section of
    [awesome-public-datasets](https://github.com/awesomedata/awesome-public-datasets#id76)
    is a good place to start looking for that

<!-- end list -->

4.  Manually find bounding coordinates using a service like Google Maps

## Calculate the bounding box

We will filter the Speedtest tiles with the bounding box of the area of
interest.

I’ll use the Belltown neighborhood of Seattle as an example.

``` r
# read in a shapefile of all of the seattle neighborhoods to start
nb <- st_read("https://opendata.arcgis.com/datasets/b76cdd45f7b54f2a96c5e97f2dda3408_2.geojson") %>%
  st_transform(4326) # convert to latitude, longitude in case it's in a different projection. Won't hurt if it's already in the right coordinate system.
```

    ## Reading layer `City_Clerk_Neighborhoods' from data source `https://opendata.arcgis.com/datasets/b76cdd45f7b54f2a96c5e97f2dda3408_2.geojson' using driver `GeoJSON'
    ## Simple feature collection with 119 features and 12 fields
    ## geometry type:  POLYGON
    ## dimension:      XY
    ## bbox:           xmin: -122.436 ymin: 47.49551 xmax: -122.236 ymax: 47.73416
    ## epsg (SRID):    4326
    ## proj4string:    +proj=longlat +datum=WGS84 +no_defs

When filtering an `sf` dataframe, the bounding box is not updated to the
filtered copy. Instead, I use base R so that the bounding box covers
only the specific neighborhood.

``` r
belltown <- nb[nb$S_HOOD == "Belltown", ]
```

Then `st_bbox()` produces a vector with the minimum and maximum x and y
values for the specific neighborhood. Plotting both the boundary and
bounding box together help visually confirm this.

``` r
belltown_bbox <- st_bbox(belltown)
belltown_bbox
```

    ##       xmin       ymin       xmax       ymax
    ## -122.36050   47.60994 -122.32871   47.61862

Another way to check this is to look at the message that printed when we
first read in the shapefile. When you read in with `st_read()` it prints
a message that includes the full bounding box, in this case `## bbox:
xmin: -122.436 ymin: 47.49551 xmax: -122.236 ymax: 47.73416`. Our new
bounding box should be at most this large and in this case we can see
that it’s smaller.

``` r
ggplot() +
  geom_sf(data = belltown,
          color = "gray20",
          fill = "gray98",
          lwd = 0.1) +
  geom_sf(data = st_as_sfc(belltown_bbox), # convert the bounding box to sfc in order to plot
          color = "#7ECCBA",
          fill = NA) +
  theme_void()
```

![](https://raw.githubusercontent.com/teamookla/ookla-open-data/tutorials-2/tutorials/img/belltown_box-1.png)<!-- -->

Looks correct\!

## Filter the Speedtest tiles

The general idea of this function is *find tiles covered by bounding box
-\> convert to quadkey -\> [convert to
quadkey](https://gist.github.com/dselivanov/77526fed90ca97a53a6d423e313708fb)*

Quadkeys are unique identifiers for map tiles at different zoom levels–
these tiles are all zoom level 16. They’re helpful for comparing
datasets over time and loading quickly on a webmap, among other things.
In this case we can find the grid of quadkeys covered by our bounding
box and filter accordingly.

## Set up the function

These helper functions will help to write a function that takes a
bounding box and the tiles as inputs and outputs a tibble of just the
tiles of interest.

``` r
as_binary = function(x){
  tmp = rev(as.integer(intToBits(x)))
  id = seq_len(match(1, tmp, length(tmp)) - 1)
  tmp[-id]
}

deg2num = function(lat_deg, lon_deg, zoom) {
  lat_rad = lat_deg * pi /180
  n = 2.0 ^ zoom
  xtile = floor((lon_deg + 180.0) / 360.0 * n)
  ytile = floor((1.0 - log(tan(lat_rad) + (1 / cos(lat_rad))) / pi) / 2.0 * n)
  c(xtile, ytile)
}

# reference JavaScript implementations
# https://developer.here.com/documentation/traffic/dev_guide/common/map_tile/topics/quadkeys.html

tileXYToQuadKey = function(xTile, yTile, z) {
  quadKey = ""
  for (i in z:1) {
    digit = 0
    mask = bitwShiftL(1, i - 1)
    xtest = as_binary(bitwAnd(xTile, mask))
    if(any(xtest)) {
      digit = digit + 1
    }

    ytest = as_binary(bitwAnd(yTile, mask))
    if(any(ytest)) {
      digit = digit + 2
    }
    quadKey = paste0(quadKey, digit)
  }
  quadKey
}

get_perf_tiles <- function(bbox, tiles){
  bbox <- st_bbox(
  st_transform(
    st_as_sfc(bbox),
    4326
  ))
  tile_grid <- bbox_to_tile_grid(bbox, zoom = 16)
  # zoom level 16 held constant, otherwise loop through the tile coordinates calculated above
  quadkeys <- pmap(list(tile_grid$tiles$x, tile_grid$tiles$y, 16), tileXYToQuadKey)
  perf_tiles <- tiles %>%
    filter(quadkey %in% quadkeys)
}
```

There are a few ways to download the parquet file from s3. In this
example I’ll download the fixed broadband data from Q2 2020 to a temp
file and then read it in.

``` r
temp <- tempfile()
download.file("https://ookla-open-data.s3-us-west-2.amazonaws.com/parquet/performance/type%3Dfixed/year%3D2020/quarter%3D2/2020-04-01_performance_fixed_tiles.parquet", temp)

tiles <- read_parquet(temp)

belltown_perf_tiles <- get_perf_tiles(belltown_bbox, tiles) %>%
  st_as_sf(wkt = "tile", crs = 4326)
```

There are 20 tiles in the Speedtest data that overlap with the Belltown
bounding box.

## Map the tiles

Just to see one more time that the location filter worked as expected
I’ll make a quick map with `ggplot2`. I’m filtering out tiles with
fewer than 10 tests total.

``` r
ggplot() +
  geom_sf(data = belltown_perf_tiles %>% filter(tests > 9),
          color = "white",
          aes(fill = cut(avg_d_kbps / 1000,
                         breaks=c(quantile(avg_d_kbps / 1000,
                                           probs = seq(0, 1, by = 0.20))),
                         labels=c("33.8 to 44.2","44.3 to 49.2","49.3 to 55.5","55.6 to 89.5","89.6 to 146"),
                         include.lowest=TRUE))) +
  scale_fill_brewer(palette = "BuPu", name = "Mean Download Mbps") +
  geom_sf(data = belltown,
          color = "gray20",
          fill = NA) +
  theme_void() +
  theme(text = element_text(color = "gray20", family = "Lato"),
        legend.position = "bottom",
        legend.direction = "horizontal") +
  labs(title = "Belltown, Seattle, WA",
       caption = "Quantile breaks")
```

![](https://raw.githubusercontent.com/teamookla/ookla-open-data/tutorials-2/tutorials/img/belltown_tiles-1.png)<!-- -->
