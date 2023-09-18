#!/bin/python3

from gpxpy.gpx import GPXWaypoint


class Snapper(object):

    def snap_points_to_track(self, track, waypoints_for_track, max_distance):
        new_waypoints = []
        for waypoint in waypoints_for_track:
            nearest_location = track.get_nearest_location(waypoint).location
            if nearest_location.distance_3d(waypoint) <= max_distance:
                new_waypoints.append(self.__copy_waypoint_with_new_coordinates(
                    nearest_location.latitude,
                    nearest_location.longitude,
                    nearest_location.elevation,
                    waypoint)
                )
            else:
                print(f"waypoint '{waypoint.name}' is ignore. It is further way than {max_distance} m from the track '{track.name}'.")
        return new_waypoints

    @staticmethod
    def __copy_waypoint_with_new_coordinates(latitude, longitude, elevation, old_waypoint):
        return GPXWaypoint(
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            time=old_waypoint.time,
            name=old_waypoint.name,
            description=old_waypoint.description,
            symbol=old_waypoint.symbol,
            type=old_waypoint.type,
            comment=old_waypoint.comment,
            horizontal_dilution=old_waypoint.horizontal_dilution,
            vertical_dilution=old_waypoint.vertical_dilution,
            position_dilution=old_waypoint.position_dilution,
        )
