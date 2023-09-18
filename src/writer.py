#!/bin/python3

import csv
import datetime
import os
import subprocess
import tempfile

from gpxpy.geo import Location

from coursePointTypes import COURSE_POINTS


class Writer(object):
    GARMIN_DATE_ZERO = datetime.datetime(1989, 12, 31, tzinfo=datetime.timezone.utc)
    TRACK_NAME_LENGTH = 23
    COURSE_POINT_NAME_LENGTH = 14

    def __init__(self, track, waypoints_for_track, max_distance):
        self.track = track
        self.rows = []

        self.__calculate_length_for_track_points()
        self.waypoints = self.__calculate_length_from_start_to_way_points(waypoints_for_track, max_distance)

    def __calculate_length_for_track_points(self):
        previous_point = None
        for segment in self.track.segments:
            for point in segment.points:
                if previous_point is None:
                    point.length_from_start = 0.0
                else:
                    point.length_from_start = round(previous_point.length_from_start + previous_point.distance_2d(point), ndigits=2)
                previous_point = point

    def __calculate_length_from_start_to_way_points(self, waypoints_for_track, max_distance):
        new_waypoints = []
        for waypoint in waypoints_for_track:
            nearest_location = self.track.get_nearest_location(waypoint).location
            # When we snap waypoints then the distance is 0, but if we don't snap the distance is unequal 0.
            distance_to_track = nearest_location.distance_3d(waypoint)
            waypoint.length_from_start = round(distance_to_track + nearest_location.length_from_start, ndigits=2)
            new_waypoints.append(waypoint)
        new_waypoints.sort(key=lambda x: x.length_from_start)
        return new_waypoints

    def convert_to_fit(self, filename, sport_type):
        self.__write_header()
        self.__write_definitions()
        self.__write_file_id()
        self.__write_course(sport_type)
        self.__write_lap()
        self.__write_event()
        self.__write_records()
        self.__write_course_points()
        self.__write_event_end()

        temp_file = self.__write_csv()
        self.__convert_csv_to_fit(temp_file, filename)

    def __write_header(self):
        self.rows.append([
            "Type", "Local Number", "Message",
            "Field 1", "Value 1", "Units 1",
            "Field 2", "Value 2", "Units 2",
            "Field 3", "Value 3", "Units 3",
            "Field 4", "Value 4", "Units 4",
            "Field 5", "Value 5", "Units 5",
            "Field 6", "Value 6", "Units 6",
            "Field 7", "Value 7", "Units 7",
            "Field 8", "Value 8", "Units 8",
            "Field 9", "Value 9", "Units 9",
            "Field 10", "Value 10", "Units 10",
            "Field 11", "Value 11", "Units 11",
        ])

    def __write_definitions(self):
        self.rows.append([
            "Definition", "0", "file_id",
            "type", "1", "",
            "manufacturer", "1", "",
            "product", "1", "",
            "time_created", "1", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])
        self.rows.append([
            "Definition", "1", "course",
            "name", "16", "",
            "sport", "1", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])
        self.rows.append([
            "Definition", "2", "lap",
            "timestamp", "1", "",
            "start_time", "1", "",
            "start_position_lat", "1", "",
            "start_position_long", "1", "",
            "end_position_lat", "1", "",
            "end_position_long", "1", "",
            "total_elapsed_time", "1", "",
            "total_timer_time", "1", "",
            "total_distance", "1", "",
            "avg_speed", "1", "",
            "max_speed", "1", "",
        ])
        self.rows.append([
            "Definition", "3", "event",
            "timestamp", "1", "",
            "event", "1", "",
            "event_type", "1", "",
            "event_group", "1", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])
        self.rows.append([
            "Definition", "4", "course_point",
            "timestamp", "1", "",
            "position_lat", "1", "",
            "position_long", "1", "",
            "distance", "1", "",
            "name", "16", "",
            "type", "1", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])
        self.rows.append([
            "Definition", "5", "record",
            "timestamp", "1", "",
            "position_lat", "1", "",
            "position_long", "1", "",
            "distance", "1", "",
            "altitude", "1", "",
            "speed", "1", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    def __write_file_id(self):
        self.rows.append([
            "Data", "0", "file_id",
            "type", "6", "",  # 6 = course file
            "manufacturer", "1", "",
            "garmin_product", "1001", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    def __write_course(self, sport_type):
        track_name = self.track.name[:Writer.TRACK_NAME_LENGTH]
        self.rows.append([
            "Data", "1", "course",
            "name", track_name, "",
            "sport", sport_type, "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    def __write_lap(self):
        first_point = self.to_semicircles(self.track.segments[0].points[0])
        last_point = self.to_semicircles(self.track.segments[-1].points[-1])
        total_distance = round(self.track.length_2d(), ndigits=2)
        self.rows.append([
            "Data", "2", "lap",
            "start_position_lat", f"{first_point.latitude}", "semicircles",
            "start_position_long", f"{first_point.longitude}", "semicircles",
            "end_position_lat", f"{last_point.latitude}", "semicircles",
            "end_position_long", f"{last_point.longitude}", "semicircles",
            "total_elapsed_time", "", "s",
            "total_timer_time", "", "s",
            "total_distance", f"{total_distance}", "m",
            "avg_speed", "", "m / s",
            "max_speed", "", "m / s",
            "enhanced_avg_speed", "", "m / s",
            "enhanced_max_speed", "", "m / s",
        ])

    def __write_event(self):
        self.rows.append([
            "Data", "3", "event",
            "event", "0", "",
            "event_type", "0", "",
            "event_group", "0", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    def __write_event_end(self):
        self.rows.append([
            "Data", "3", "event",
            "event", "0", "",
            "event_type", "9", "",
            "event_group", "0", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    def __write_records(self):
        for segment in self.track.segments:
            for track_point in segment.points:
                self.__write_record(track_point)

    def __write_record(self, track_point):
        position = self.to_semicircles(track_point)
        elevation = position.elevation if position.elevation else ''
        self.rows.append([
            "Data", "5", "record",
            "position_lat", f"{position.latitude}", "semicircles",
            "position_long", f"{position.longitude}", "semicircles",
            "distance", f"{track_point.length_from_start}", "m",
            "altitude", f"{elevation}", "m",
            "speed", "", "m/s",
            "enhanced_altitude", f"{elevation}", "m",
            "enhanced_speed", "", "m/s",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    def __write_course_points(self):
        for waypoint in self.waypoints:
            self.__write_course_point(waypoint)

    def __write_course_point(self, waypoint):
        name = waypoint.name[:Writer.COURSE_POINT_NAME_LENGTH]
        waypoint_type = self.__get_course_point_type(waypoint)
        if waypoint.time is None:
            waypoint.time = datetime.datetime.now(tz=datetime.timezone.utc)
        timestamp = waypoint.time - Writer.GARMIN_DATE_ZERO
        time_in_seconds = round(timestamp.total_seconds())
        position = self.to_semicircles(waypoint)
        self.rows.append([
            "Data", "4", "course_point",
            "timestamp", f"{time_in_seconds}", "",
            "position_lat", f"{position.latitude}", "semicircles",
            "position_long", f"{position.longitude}", "semicircles",
            "distance", f"{waypoint.length_from_start}", "m",
            "name", f"{name}", "",
            "type", f"{waypoint_type}", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
            "", "", "",
        ])

    @staticmethod
    def __get_course_point_type(waypoint):
        waypoint_type = waypoint.type.lower() if waypoint.type else waypoint.symbol.lower()
        waypoint_type = waypoint_type.replace(' ', '_')
        if waypoint_type in COURSE_POINTS:
            return COURSE_POINTS[waypoint_type]
        if waypoint_type.isnumeric():
            return waypoint_type
        return COURSE_POINTS['generic']

    def __write_csv(self):
        temp_file = tempfile.mkstemp(suffix=".csv")[1]
        with open(temp_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in self.rows:
                writer.writerow(row)
        return temp_file

    @staticmethod
    def __convert_csv_to_fit(temp_file, filename):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        subprocess.call([
            "java",
            "-jar",
            f"{dir_path}/../SDK/java/FitCSVTool.jar",
            "-c",
            temp_file,
            filename
        ])

    @staticmethod
    def to_semicircles(location):
        return Location(
            latitude=round(location.latitude / 180 * 0x80000000),
            longitude=round(location.longitude / 180 * 0x80000000),
            elevation=location.elevation,
        )
