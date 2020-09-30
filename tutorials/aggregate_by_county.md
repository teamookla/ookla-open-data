Using R to analyze download speeds in U.S. counties
================

In this tutorial I will talk about how to:

  - Download the Ookla open dataset
  - Geocode the tiles to U.S. counties
  - Make a table of the top and bottom 20 counties by download speed
  - And map the counties

There are two main ways to join these tiles to another geographic
dataset: quadkeys and spatial joins. This tutorial will use the spatial
join approach.

``` r
library(tigris) # county boundaries
library(tidyverse) # data cleaning
library(sf) # spatial functions
library(knitr)
library(kableExtra)
library(RColorBrewer)
library(urbnmapr) # county basemap
library(here)
```

## Download data

First, download the data to a local directory

*Need to edit this with the public data*

``` r
# temp files
temp <- tempfile()
temp2 <- tempfile()
# download the zip folder from s3 and save to temp
download.file("https://ookla-open-data.s3-us-west-2.amazonaws.com/shapefiles/performance/type%3Dfixed/year%3D2020/quarter%3D2/2020-04-01_performance_fixed_tiles.zip",temp)
# unzip the contents in 'temp' and save unzipped content in 'temp2'
unzip(zipfile = temp, exdir = temp2)
# finds the filepath of the shapefile (.shp) file in the temp2 unzip folder
# the $ at the end of ".shp$" ensures you are not also finding files such as .shp.xml
shp <-list.files(temp2, pattern = ".shp$",full.names=TRUE)

#read the shapefile. Alternatively make an assignment, such as f<-sf::read_sf(your_SHP_file)
tiles <- read_sf(shp)
```

## Get county boundaries

Then, I’ll load the U.S. county boundaries from the U.S. Census Bureau
via `tigris`. These boundaries include D.C. and the territories.

``` r
us_counties <- tigris::counties() %>%
  select(state_code = STATEFP, geoid = GEOID, name = NAME) %>% # only keep useful variables
  st_transform(st_crs(tiles)) # transform to the same CRS as the tiles
```

## Join tiles to counties

Now I’ll join the tiles to the counties. I use `left = FALSE` because I
only want to include counties that have at least 1 tile.

``` r
tiles_in_counties <- st_join(us_counties, tiles, left = FALSE)
```

## Calculate statistics

Once the datasets are joined, we are interested in summary statistics at
the county level. Since we know the average download speed per tile, we
could just do a simple average. To make it more accurate, I’ll use a
weighted mean, weighted by test count. This gives us the overall mean in
the county if the data hadn’t been aggregated to tiles first. I’ve also
included weighted means for upload speed and latency here as well.

``` r
county_stats <- tiles_in_counties %>%
  st_set_geometry(NULL) %>%
  group_by(state_code, geoid, name) %>%
  summarise(mean_dl_mbps_wt = weighted.mean(avg_d_kbps, tests) / 1000,
            mean_ul_mbps_wt = weighted.mean(avg_u_kbps, tests) / 1000,
            mean_lat_ms_wt = weighted.mean(avg_lat_ms, tests),
            tests = sum(tests)) %>%
  ungroup() %>%
  left_join(fips_codes %>%
              mutate(geoid = paste0(state_code, county_code)) %>%
              # get nicer county and state names
              select(state, geoid, long_name = county, county), by = c("geoid"))
```

## Make a table of the top 20 and bottom 20 counties

Next we can make a summary table of just the best and worst counties.
We’ll require that counties have at least 50 tests so that the
averages are more reliable. I use `kable()` here for simplicity, but you
could use any of the R packages that help with tables.

``` r
table_data <- county_stats %>%
  filter(tests >= 50) %>%
  mutate(rank = min_rank(-mean_dl_mbps_wt)) %>% # rank in descending order
  dplyr::filter(rank <= 20 | rank >= n() - 19) %>%
  mutate(`County` = paste0(long_name, ", ", state),
         mean_dl_mbps_wt = round(mean_dl_mbps_wt, 2)) %>%
  arrange(rank) %>%
  select(`County`, `Average download speed (Mbps)` = mean_dl_mbps_wt, `Tests` = tests, `Rank` = rank)

kable(table_data, format.args = list(big.mark = ","))
```

<table>

<thead>

<tr>

<th style="text-align:left;">

County

</th>

<th style="text-align:right;">

Average download speed (Mbps)

</th>

<th style="text-align:right;">

Tests

</th>

<th style="text-align:right;">

Rank

</th>

</tr>

</thead>

<tbody>

<tr>

<td style="text-align:left;">

Colonial Heights city, VA

</td>

<td style="text-align:right;">

199.17

</td>

<td style="text-align:right;">

981

</td>

<td style="text-align:right;">

1

</td>

</tr>

<tr>

<td style="text-align:left;">

Hopewell city, VA

</td>

<td style="text-align:right;">

198.29

</td>

<td style="text-align:right;">

812

</td>

<td style="text-align:right;">

2

</td>

</tr>

<tr>

<td style="text-align:left;">

Gloucester County, NJ

</td>

<td style="text-align:right;">

194.02

</td>

<td style="text-align:right;">

17,139

</td>

<td style="text-align:right;">

3

</td>

</tr>

<tr>

<td style="text-align:left;">

Salem County, NJ

</td>

<td style="text-align:right;">

189.17

</td>

<td style="text-align:right;">

3,263

</td>

<td style="text-align:right;">

4

</td>

</tr>

<tr>

<td style="text-align:left;">

Corson County, SD

</td>

<td style="text-align:right;">

188.52

</td>

<td style="text-align:right;">

137

</td>

<td style="text-align:right;">

5

</td>

</tr>

<tr>

<td style="text-align:left;">

Calvert County, MD

</td>

<td style="text-align:right;">

186.80

</td>

<td style="text-align:right;">

5,326

</td>

<td style="text-align:right;">

6

</td>

</tr>

<tr>

<td style="text-align:left;">

Petersburg Census Area, AK

</td>

<td style="text-align:right;">

185.51

</td>

<td style="text-align:right;">

153

</td>

<td style="text-align:right;">

7

</td>

</tr>

<tr>

<td style="text-align:left;">

Mercer County, ND

</td>

<td style="text-align:right;">

185.07

</td>

<td style="text-align:right;">

820

</td>

<td style="text-align:right;">

8

</td>

</tr>

<tr>

<td style="text-align:left;">

Kent County, DE

</td>

<td style="text-align:right;">

184.05

</td>

<td style="text-align:right;">

9,801

</td>

<td style="text-align:right;">

9

</td>

</tr>

<tr>

<td style="text-align:left;">

Baker County, FL

</td>

<td style="text-align:right;">

183.94

</td>

<td style="text-align:right;">

749

</td>

<td style="text-align:right;">

10

</td>

</tr>

<tr>

<td style="text-align:left;">

Burlington County, NJ

</td>

<td style="text-align:right;">

180.79

</td>

<td style="text-align:right;">

31,337

</td>

<td style="text-align:right;">

11

</td>

</tr>

<tr>

<td style="text-align:left;">

Camden County, NJ

</td>

<td style="text-align:right;">

179.81

</td>

<td style="text-align:right;">

27,115

</td>

<td style="text-align:right;">

12

</td>

</tr>

<tr>

<td style="text-align:left;">

Manassas city, VA

</td>

<td style="text-align:right;">

178.86

</td>

<td style="text-align:right;">

3,391

</td>

<td style="text-align:right;">

13

</td>

</tr>

<tr>

<td style="text-align:left;">

Bossier Parish, LA

</td>

<td style="text-align:right;">

178.18

</td>

<td style="text-align:right;">

16,211

</td>

<td style="text-align:right;">

14

</td>

</tr>

<tr>

<td style="text-align:left;">

Carroll County, MD

</td>

<td style="text-align:right;">

178.03

</td>

<td style="text-align:right;">

12,634

</td>

<td style="text-align:right;">

15

</td>

</tr>

<tr>

<td style="text-align:left;">

Powhatan County, VA

</td>

<td style="text-align:right;">

177.63

</td>

<td style="text-align:right;">

2,386

</td>

<td style="text-align:right;">

16

</td>

</tr>

<tr>

<td style="text-align:left;">

Cumberland County, NJ

</td>

<td style="text-align:right;">

177.13

</td>

<td style="text-align:right;">

4,316

</td>

<td style="text-align:right;">

17

</td>

</tr>

<tr>

<td style="text-align:left;">

Belmont County, OH

</td>

<td style="text-align:right;">

177.11

</td>

<td style="text-align:right;">

3,579

</td>

<td style="text-align:right;">

18

</td>

</tr>

<tr>

<td style="text-align:left;">

Atlantic County, NJ

</td>

<td style="text-align:right;">

176.80

</td>

<td style="text-align:right;">

15,035

</td>

<td style="text-align:right;">

19

</td>

</tr>

<tr>

<td style="text-align:left;">

Hamilton County, TN

</td>

<td style="text-align:right;">

176.60

</td>

<td style="text-align:right;">

35,954

</td>

<td style="text-align:right;">

20

</td>

</tr>

<tr>

<td style="text-align:left;">

Choctaw County, AL

</td>

<td style="text-align:right;">

9.10

</td>

<td style="text-align:right;">

727

</td>

<td style="text-align:right;">

3,095

</td>

</tr>

<tr>

<td style="text-align:left;">

Tensas Parish, LA

</td>

<td style="text-align:right;">

8.75

</td>

<td style="text-align:right;">

295

</td>

<td style="text-align:right;">

3,096

</td>

</tr>

<tr>

<td style="text-align:left;">

Culebra Municipio, PR

</td>

<td style="text-align:right;">

8.61

</td>

<td style="text-align:right;">

106

</td>

<td style="text-align:right;">

3,097

</td>

</tr>

<tr>

<td style="text-align:left;">

Tyrrell County, NC

</td>

<td style="text-align:right;">

8.58

</td>

<td style="text-align:right;">

133

</td>

<td style="text-align:right;">

3,098

</td>

</tr>

<tr>

<td style="text-align:left;">

Roberts County, TX

</td>

<td style="text-align:right;">

8.51

</td>

<td style="text-align:right;">

61

</td>

<td style="text-align:right;">

3,099

</td>

</tr>

<tr>

<td style="text-align:left;">

Bethel Census Area, AK

</td>

<td style="text-align:right;">

8.42

</td>

<td style="text-align:right;">

311

</td>

<td style="text-align:right;">

3,100

</td>

</tr>

<tr>

<td style="text-align:left;">

Pope County, IL

</td>

<td style="text-align:right;">

8.28

</td>

<td style="text-align:right;">

324

</td>

<td style="text-align:right;">

3,101

</td>

</tr>

<tr>

<td style="text-align:left;">

Pawnee County, OK

</td>

<td style="text-align:right;">

8.24

</td>

<td style="text-align:right;">

349

</td>

<td style="text-align:right;">

3,102

</td>

</tr>

<tr>

<td style="text-align:left;">

Roger Mills County, OK

</td>

<td style="text-align:right;">

8.04

</td>

<td style="text-align:right;">

170

</td>

<td style="text-align:right;">

3,103

</td>

</tr>

<tr>

<td style="text-align:left;">

Perry County, MS

</td>

<td style="text-align:right;">

8.00

</td>

<td style="text-align:right;">

334

</td>

<td style="text-align:right;">

3,104

</td>

</tr>

<tr>

<td style="text-align:left;">

Loving County, TX

</td>

<td style="text-align:right;">

7.60

</td>

<td style="text-align:right;">

243

</td>

<td style="text-align:right;">

3,105

</td>

</tr>

<tr>

<td style="text-align:left;">

Treutlen County, GA

</td>

<td style="text-align:right;">

7.60

</td>

<td style="text-align:right;">

258

</td>

<td style="text-align:right;">

3,106

</td>

</tr>

<tr>

<td style="text-align:left;">

Vieques Municipio, PR

</td>

<td style="text-align:right;">

7.53

</td>

<td style="text-align:right;">

395

</td>

<td style="text-align:right;">

3,107

</td>

</tr>

<tr>

<td style="text-align:left;">

Nome Census Area, AK

</td>

<td style="text-align:right;">

7.08

</td>

<td style="text-align:right;">

69

</td>

<td style="text-align:right;">

3,108

</td>

</tr>

<tr>

<td style="text-align:left;">

Rawlins County, KS

</td>

<td style="text-align:right;">

6.77

</td>

<td style="text-align:right;">

124

</td>

<td style="text-align:right;">

3,109

</td>

</tr>

<tr>

<td style="text-align:left;">

Calhoun County, IL

</td>

<td style="text-align:right;">

6.34

</td>

<td style="text-align:right;">

349

</td>

<td style="text-align:right;">

3,110

</td>

</tr>

<tr>

<td style="text-align:left;">

Ozark County, MO

</td>

<td style="text-align:right;">

6.09

</td>

<td style="text-align:right;">

189

</td>

<td style="text-align:right;">

3,111

</td>

</tr>

<tr>

<td style="text-align:left;">

Kinney County, TX

</td>

<td style="text-align:right;">

5.21

</td>

<td style="text-align:right;">

105

</td>

<td style="text-align:right;">

3,112

</td>

</tr>

<tr>

<td style="text-align:left;">

Camas County, ID

</td>

<td style="text-align:right;">

5.20

</td>

<td style="text-align:right;">

121

</td>

<td style="text-align:right;">

3,113

</td>

</tr>

<tr>

<td style="text-align:left;">

Dillingham Census Area, AK

</td>

<td style="text-align:right;">

4.14

</td>

<td style="text-align:right;">

52

</td>

<td style="text-align:right;">

3,114

</td>

</tr>

</tbody>

</table>

## And we can also make a map of these counties

The table is good for a quick glance at overall patterns (what are the
overall maxima and minima? where is the fastest speed?) but unless
you’re already familiar with these areas it can be hard to picture
where they are on a map. To go along with the table we can produce a
quick choropleth map that will help give a more visual representation.

I like using the basemaps from the [Urban
Institute](https://urbaninstitute.github.io/urbnmapr/articles/introducing-urbnmapr.html)
because they have the non-lower-48 shifted over so they’re easier to see
on a map layout. Not great for geocoding, but excellent for
visualization.

``` r
basemap <- get_urbn_map(map = "territories_counties", sf = TRUE)

state_borders <- get_urbn_map(map = "territories_states", sf = TRUE)
```

We can join our county statistics table to the basemap (remember, we
already got rid of the geometry from that county statistics table). I’m
also creating a categorical variable from the continuous download speed
because people aren’t great at reading continuous color schemes. People
can read discrete legends much more easily, with 7 categories maximum
(this can depend on the situation, though).

``` r
county_stats_sf <- basemap %>%
  select(geoid = county_fips) %>%
  left_join(county_stats, by = c("geoid")) %>%
  mutate(mean_dl_mbps_wt = case_when(tests < 50 ~ NA_real_,
                            TRUE ~ mean_dl_mbps_wt)) %>% # at least 50 tests
  mutate(dl_cat = cut(mean_dl_mbps_wt, c(0, 25, 50, 100, 150, 200), ordered_result = TRUE))

ggplot() +
  geom_sf(data = county_stats_sf, aes(fill = dl_cat), color = "white", lwd = 0.1) +
  geom_sf(data = state_borders, fill = NA, color = "gray20", lwd = 0.2) +
  theme_void() +
  scale_fill_manual(values = brewer.pal(n = 6, name = "BuPu"),
                    na.value = "gray80",
                    labels = c("0 to 25", "25.1 to 50", "50.1 to 100", "100.1 to 150", "150.1 to 200", "Insufficient data"),
                    name = "Mean download speed (Mbps)",
                    guide = guide_legend(direction = "horizontal", title.position = "top", nrow = 1, label.position = "bottom", keyheight = 0.5, keywidth = 5)) +
  theme(text = element_text(family = "Lato", color = "gray25"),
        legend.position = "top")
```

![county map showing higher speeds in more urban areas on average](https://raw.githubusercontent.com/teamookla/ookla-open-data/tutorials-2/tutorials/img/county_map-1.png)<!-- -->

``` r
sessionInfo()
```

    ## R version 3.6.1 (2019-07-05)
    ## Platform: x86_64-apple-darwin15.6.0 (64-bit)
    ## Running under: macOS Mojave 10.14.6
    ##
    ## Matrix products: default
    ## BLAS:   /Library/Frameworks/R.framework/Versions/3.6/Resources/lib/libRblas.0.dylib
    ## LAPACK: /Library/Frameworks/R.framework/Versions/3.6/Resources/lib/libRlapack.dylib
    ##
    ## locale:
    ## [1] en_US.UTF-8/en_US.UTF-8/en_US.UTF-8/C/en_US.UTF-8/en_US.UTF-8
    ##
    ## attached base packages:
    ## [1] stats     graphics  grDevices utils     datasets  methods   base
    ##
    ## other attached packages:
    ##  [1] here_0.1            urbnmapr_0.0.0.9002 RColorBrewer_1.1-2
    ##  [4] kableExtra_1.1.0    knitr_1.29          sf_0.8-0
    ##  [7] forcats_0.5.0       stringr_1.4.0       dplyr_1.0.0
    ## [10] purrr_0.3.4         readr_1.3.1         tidyr_1.1.0
    ## [13] tibble_3.0.1        ggplot2_3.3.2       tidyverse_1.3.0
    ## [16] tigris_1.0
    ##
    ## loaded via a namespace (and not attached):
    ##  [1] httr_1.4.2         jsonlite_1.7.0     viridisLite_0.3.0  modelr_0.1.8
    ##  [5] assertthat_0.2.1   sp_1.3-2           highr_0.8          blob_1.2.1
    ##  [9] cellranger_1.1.0   yaml_2.2.1         pillar_1.4.4       backports_1.1.8
    ## [13] lattice_0.20-38    glue_1.4.1         uuid_0.1-2         digest_0.6.25
    ## [17] rvest_0.3.5        colorspace_1.4-1   htmltools_0.5.0    pkgconfig_2.0.3
    ## [21] broom_0.5.6        haven_2.3.1        scales_1.1.1       webshot_0.5.1
    ## [25] farver_2.0.3       generics_0.0.2     ellipsis_0.3.1     withr_2.2.0
    ## [29] cli_2.0.2          magrittr_1.5       crayon_1.3.4       readxl_1.3.1
    ## [33] maptools_0.9-8     evaluate_0.14      fs_1.4.2           fansi_0.4.1
    ## [37] nlme_3.1-140       xml2_1.3.2         foreign_0.8-71     class_7.3-15
    ## [41] tools_3.6.1        hms_0.5.3          lifecycle_0.2.0    munsell_0.5.0
    ## [45] reprex_0.3.0       compiler_3.6.1     e1071_1.7-3        rlang_0.4.7
    ## [49] classInt_0.4-2     units_0.6-5        grid_3.6.1         rstudioapi_0.11
    ## [53] rappdirs_0.3.1     rmarkdown_2.3      gtable_0.3.0       DBI_1.1.0
    ## [57] R6_2.4.1           lubridate_1.7.9    rgdal_1.4-6        rprojroot_1.3-2
    ## [61] KernSmooth_2.23-15 stringi_1.4.6      Rcpp_1.0.3         vctrs_0.3.1
    ## [65] dbplyr_1.4.4       tidyselect_1.1.0   xfun_0.15
