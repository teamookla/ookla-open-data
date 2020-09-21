Tutorial sketch: Make a table of counties sorted by download speed
================

``` r
library(tigris) # county boundaries
library(tidyverse) # data cleaning
library(sf) # spatial functions
library(gt) # table
library(urbnmapr) # county basemap
library(arrow) # parquet
```

## Download data

``` r
tiles <- read_parquet(...)
# OR
tiles <- st_read(...)
```

## Get county boundaries

``` r
us_counties <- tigris::counties()
```

## Join tiles to counties

``` r
us_counties_clean <- us_counties %>%
  select(...) %>% # only keep useful variables 
  st_transform(...) # projection = (something in meters)

tiles_clean <- tiles %>%
  st_transform(...) # projection = 

tiles_in_counties <- st_join(tiles_clean, us_counties_clean)
```

## US map

``` r
basemap <- get_urbn_map(map = "territories_counties", sf = TRUE) # includes the US territories in the county shapefile but moves them to a more visually convenient location, along with AK and HI
```

## Calculate statistics

  - Weighted
      - Mean download
      - Mean upload
      - Mean latency

<!-- end list -->

``` r
county_stats <- tiles_in_counties %>%
  group_by([county]) %>%
  summarise(mean_dl_wt = weighted.mean(dl, tests),
            ...)
```

## Make a sorted table by mean download

``` r
gt(...)
```
