# GPX to FIT Converter

This script converts a given gpx file to `fit` files.
For each track in the gpx file a separate `fit` file is created.
The created `fit` files are a [course files](https://developer.garmin.com/fit/file-types/course/).

The script creates `fit` files supporting the
"[Up Ahead](https://support.garmin.com/en-GB/?faq=lQMibRoY2I5Y4pP8EXgxv7)" or "POIs along a route" feature.
If you don't want to use this feature use `--no-waypoints` to disable course points.
By default, waypoints are snapped to the track.
Doing this ensures that "Up Ahead" works as intended.
If you don't want to snap waypoints to the track use `--no-snap`.
If you want to exclude waypoints far away from the track, use `--max-snap-distance`.
By default, only waypoints closer than 100 meters are snapped.

The script supports icons for the course points.
Assign your GPX Waypoint a `type` or `sym` tags.
The script first checks the `type` tag and then the `sym` tag, so you can have different value in them.
Supported types are:

- `generic` or `0`
- `summit` or `1`
- `valley` or `2`
- `water` or `3`
- `food` or `4`
- `danger` or `5`
- `left` or `6`
- `right` or `7`
- `straight` or `8`
- `first_aid` or `9`
- `fourth_category` or `10`
- `third_category` or `11`
- `second_category` or `12`
- `first_category` or `13`
- `hors_category` or `14`
- `sprint` or `15`
- `left_fork` or `16`
- `right_fork` or `17`
- `middle_fork` or `18`
- `slight_left` or `19`
- `sharp_left` or `20`
- `slight_right` or `21`
- `sharp_right` or `22`
- `u_turn` or `23`
- `segment_start` or `24`
- `segment_end` or `25`
- `campsite` or `27`
- `aid_station` or `28`
- `rest_area` or `29`
- `general_distance` or `30`
- `service` or `31`
- `energy_gel` or `32`
- `sports_drink` or `33`
- `mile_marker` or `34`
- `checkpoint` or `35`
- `shelter` or `36`
- `meeting_spot` or `37`
- `overlook` or `38`
- `toilet` or `39`
- `shower` or `40`
- `gear` or `41`
- `sharp_curve` or `42`
- `steep_incline` or `43`
- `tunnel` or `44`
- `bridge` or `45`
- `obstacle` or `46`
- `crossing` or `47`
- `store` or `48`
- `transition` or `49`
- `navaid` or `50`
- `transport` or `51`
- `alert` or `52`
- `info` or `53`

You can define the sport type using the `--sport-type` flag.
By default, hiking (`17`) is used.

# Limitations, aka "missing feature"

`fit` files are binary files.
The python sdk does not support encoding files (only decoding).
This script

1. prepares all data,
2. saves the data as csv and
3. then uses a Java tool from the SDK called [FitCSVTool](https://developer.garmin.com/fit/fitcsvtool/) to convert the csv file to a fit file.
That means you have to download the SDK and have a Java JRE installed.

When your track has is a roundtrip with a shared started and beginning (or any other segment you plan to
walk more than once) and you have a waypoint onto this segment, then the waypoint will only be included
once.

# Dependencies

- python (obviously)
- java (not obvious, see above)
- gpxpy
- [Fit SDK](https://developer.garmin.com/fit/download/)
  - Download,
  - extract and
  - move the folder to the root folder of this repo.
  - Rename the folder to `SDK`. The `jar` should be at this place `SDK/java/FitCSVTool.jar`.
