#!/bin/python3

import argparse
import os

import gpxpy
import gpxpy.gpx

from snapper import Snapper
from writer import Writer

HIKING_SPORT_TYPE = 17


def parse_args():
    parser = argparse.ArgumentParser(
        description="Converts a gpx to a fit file.",
        epilog="When waypoints are in the gpx file those are converted as well. "
               "To ensure the 'Up Ahead' feature (also called 'POIs along a route'), waypoints are snapped to the track. "
               "This can be disabled. "
               "For each track in the gpx file a separate fit file is created. ",
    )
    parser.add_argument('input', type=str, help="The path to the input gpx.")
    parser.add_argument('--no-waypoints', dest="include_waypoints", action='store_false', default=True, help="Exclude all waypoints.")
    parser.add_argument('--no-snap', dest="snap_waypoints", action='store_false', default=True, help="Don't modify waypoints' position.")
    parser.add_argument('--max-snap-distance', dest="max_distance", type=int, default=100, help="When waypoints are snapped to the track, "
                                                                                                "filter out any waypoint further away than "
                                                                                                "given (default: 100), in meters.")
    parser.add_argument('--speed', type=str, default="3.5", help="Set the expected speed for the course (default 3.5 m/s")
    parser.add_argument('--sport-type', type=str, default=HIKING_SPORT_TYPE, help="Set the sport of the course. "
                                                                                  "Default: 17 which stands for hiking. "
                                                                                  "Can be set to any empty string.")

    return parser.parse_args()


def check_for_unique_names(gpx_object):
    names = list(map(lambda track: track.name[:15], gpx_object.tracks))
    if len(names) != len(set(names)):
        raise Exception("Each track has to have a unique name (only the first 15 characters are checked).")


def main():
    args = parse_args()

    with open(args.input) as input_file:
        gpx_object = gpxpy.parse(input_file)

    check_for_unique_names(gpx_object)
    for track in gpx_object.tracks:
        waypoints_for_track = []
        if args.include_waypoints:
            waypoints_for_track = list(gpx_object.waypoints)
            if args.snap_waypoints:
                waypoints_for_track = Snapper().snap_points_to_track(track, list(gpx_object.waypoints), args.max_distance)
        Writer(track, waypoints_for_track, args.max_distance, args.speed).convert_to_fit(track.name, args.sport_type)


if __name__ == '__main__':
    main()
