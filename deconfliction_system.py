from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import math
import logging

# Setup logging for debugging and traceability
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')


# =============================================================================
# Data Structures
# =============================================================================

class Waypoint:
    """
    Represents a single waypoint in 3D space with a timestamp.
    """
    def __init__(self, x, y, z, timestamp):
        self.x = x
        self.y = y
        self.z = z
        self.timestamp = timestamp

    def __repr__(self):
        return f"Waypoint({self.x}, {self.y}, {self.z}, {self.timestamp})"


class Mission:
    """
    Represents a drone mission, which consists of an ordered list of waypoints.
    """
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.waypoints = []

    def add_waypoint(self, waypoint):
        self.waypoints.append(waypoint)

    def __repr__(self):
        return f"Mission({self.drone_id}, {self.waypoints})"


class Conflict:
    """
    Represents a conflict detected between two drone missions.
    """
    def __init__(self, drone_id1, drone_id2, location, time, reason):
        self.drone_id1 = drone_id1
        self.drone_id2 = drone_id2
        self.location = location
        self.time = time
        self.reason = reason

    def __repr__(self):
        return (f"Conflict({self.drone_id1}, {self.drone_id2}, "
                f"Location: {self.location}, Time: {self.time}, Reason: {self.reason})")


# =============================================================================
# Utility Functions
# =============================================================================

def calculate_distance(point1, point2):
    """
    Calculates the Euclidean distance between two 3D points.
    
    Args:
        point1 (tuple): Coordinates (x, y, z) of the first point.
        point2 (tuple): Coordinates (x, y, z) of the second point.
    
    Returns:
        float: The Euclidean distance.
    """
    return math.sqrt((point2[0] - point1[0])**2 +
                     (point2[1] - point1[1])**2 +
                     (point2[2] - point1[2])**2)


def interpolate_position(waypoint1, waypoint2, target_time):
    """
    Linearly interpolates the position between two waypoints at a given time.
    
    Args:
        waypoint1 (Waypoint): The starting waypoint.
        waypoint2 (Waypoint): The ending waypoint.
        target_time (datetime): The time at which to interpolate the position.
    
    Returns:
        tuple: The interpolated (x, y, z) coordinates.
    """
    time_diff = (waypoint2.timestamp - waypoint1.timestamp).total_seconds()
    time_elapsed = (target_time - waypoint1.timestamp).total_seconds()

    if time_diff <= 0 or time_elapsed <= 0:
        return (waypoint1.x, waypoint1.y, waypoint1.z)
    if time_elapsed >= time_diff:
        return (waypoint2.x, waypoint2.y, waypoint2.z)

    fraction = time_elapsed / time_diff
    x = waypoint1.x + (waypoint2.x - waypoint1.x) * fraction
    y = waypoint1.y + (waypoint2.y - waypoint1.y) * fraction
    z = waypoint1.z + (waypoint2.z - waypoint1.z) * fraction
    return (x, y, z)


# =============================================================================
# Conflict Detection Module
# =============================================================================

def detect_conflicts(missions, min_safety_distance):
    """
    Detects potential conflicts between pairs of drone missions by comparing
    interpolated positions over overlapping time intervals.
    
    Args:
        missions (list): List of Mission objects.
        min_safety_distance (float): Minimum allowed distance between drones.
        
    Returns:
        list: List of Conflict objects.
    """
    conflicts = []
    num_missions = len(missions)
    
    # Compare each pair of missions
    for i in range(num_missions):
        for j in range(i + 1, num_missions):
            mission1 = missions[i]
            mission2 = missions[j]
            logging.info(f"Checking conflicts between {mission1.drone_id} and {mission2.drone_id}")

            # Loop through segments of mission1
            for k in range(len(mission1.waypoints) - 1):
                wp1_m1 = mission1.waypoints[k]
                wp2_m1 = mission1.waypoints[k + 1]

                # Loop through segments of mission2
                for l in range(len(mission2.waypoints) - 1):
                    wp1_m2 = mission2.waypoints[l]
                    wp2_m2 = mission2.waypoints[l + 1]

                    # Determine overlapping time interval between segments
                    start_time = max(wp1_m1.timestamp, wp1_m2.timestamp)
                    end_time = min(wp2_m1.timestamp, wp2_m2.timestamp)

                    if start_time < end_time:
                        # Divide the overlapping interval into sample points
                        num_steps = 10
                        time_interval = (end_time - start_time)
                        if time_interval.total_seconds() == 0:
                            num_steps = 1
                            time_step = time_interval
                        else:
                            time_step = time_interval / num_steps

                        # Sample positions within the time interval
                        for step in range(num_steps + 1):
                            current_time = start_time + step * time_step
                            pos1 = interpolate_position(wp1_m1, wp2_m1, current_time)
                            pos2 = interpolate_position(wp1_m2, wp2_m2, current_time)
                            distance = calculate_distance(pos1, pos2)
                            
                            # Log the distance for debugging purposes
                            logging.debug(f"Time: {current_time}, Distance: {distance}")
                            
                            if distance < min_safety_distance:
                                conflicts.append(Conflict(
                                    mission1.drone_id,
                                    mission2.drone_id,
                                    pos1,
                                    current_time,
                                    "Spatial proximity"
                                ))
                                # Once a conflict is found for this segment, break to avoid duplicate logging
                                break

    return conflicts


# =============================================================================
# Visualization Module
# =============================================================================

def visualize_missions(missions, conflicts):
    """
    Visualizes the 2D flight paths of missions and marks detected conflicts.
    
    Args:
        missions (list): List of Mission objects.
        conflicts (list): List of Conflict objects.
    """
    plt.figure(figsize=(10, 8))
    for mission in missions:
        x_coords = [wp.x for wp in mission.waypoints]
        y_coords = [wp.y for wp in mission.waypoints]
        plt.plot(x_coords, y_coords, marker='o', label=f"Drone {mission.drone_id}")

    if conflicts:
        conflict_x = [conflict.location[0] for conflict in conflicts]
        conflict_y = [conflict.location[1] for conflict in conflicts]
        plt.scatter(conflict_x, conflict_y, color='red', marker='X', s=100, label="Conflict")

    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("UAV Flight Paths and Detected Conflicts")
    plt.legend()
    plt.grid(True)
    plt.show()


# =============================================================================
# Input Function for Primary Drone Mission
# =============================================================================

def get_primary_mission():
    """
    Prompts the user to input the primary drone mission details.
    
    Returns:
        Mission: The primary drone mission entered by the user.
    """
    drone_id = input("Enter the Drone ID for the primary mission: ")
    primary_mission = Mission(drone_id)

    num_waypoints = int(input("Enter the number of waypoints for the primary mission: "))
    print("Enter waypoint details in the format: x y z YYYY-MM-DD HH:MM:SS")
    waypoint_index = 1
    while waypoint_index <= num_waypoints:
        data = input(f"Waypoint {waypoint_index}: ").split()
        if len(data) != 5:
            print("Invalid input format. Please enter exactly 5 values (x y z YYYY-MM-DD HH:MM:SS).")
            continue
        try:
            x, y, z = float(data[0]), float(data[1]), float(data[2])
            timestamp = datetime.strptime(" ".join(data[3:]), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("Invalid values or timestamp format. Please use the format: x y z YYYY-MM-DD HH:MM:SS")
            continue

        primary_mission.add_waypoint(Waypoint(x, y, z, timestamp))
        waypoint_index += 1

    return primary_mission



# =============================================================================
# Hardcoded Simulated Flight Schedules
# =============================================================================

def get_simulated_missions():
    """
    Returns a list of simulated flight missions with hardcoded waypoints.
    
    Returns:
        list: List of Mission objects representing simulated flight schedules.
    """
    simulated_missions = []

    # Simulated Mission for Drone2
    mission2 = Mission("Drone2")
    mission2.add_waypoint(Waypoint(200, 100, 15, datetime(2025, 4, 2, 10, 0, 30)))
    mission2.add_waypoint(Waypoint(100, 100, 15, datetime(2025, 4, 2, 10, 1, 0)))  # Conflict expected with primary mission
    mission2.add_waypoint(Waypoint(0, 100, 15, datetime(2025, 4, 2, 10, 2, 0)))
    mission2.add_waypoint(Waypoint(100, 100, 15, datetime(2025, 4, 2, 10, 3, 0)))
    simulated_missions.append(mission2)

    # Simulated Mission for Drone3
    mission3 = Mission("Drone3")
    mission3.add_waypoint(Waypoint(50, 0, 12, datetime(2025, 4, 2, 10, 0, 0)))
    mission3.add_waypoint(Waypoint(50, 150, 12, datetime(2025, 4, 2, 10, 2, 0)))
    mission3.add_waypoint(Waypoint(150, 150, 12, datetime(2025, 4, 2, 10, 4, 0)))
    simulated_missions.append(mission3)

    # Simulated Mission for Drone4
    mission4 = Mission("Drone4")
    mission4.add_waypoint(Waypoint(0, 200, 20, datetime(2025, 4, 2, 10, 1, 0)))
    mission4.add_waypoint(Waypoint(100, 200, 20, datetime(2025, 4, 2, 10, 3, 0)))
    mission4.add_waypoint(Waypoint(200, 200, 20, datetime(2025, 4, 2, 10, 5, 0)))
    simulated_missions.append(mission4)

    return simulated_missions


# =============================================================================
# Main Routine
# =============================================================================

def main():
    """
    Main function to run the conflict detection simulation.
    """
    print("Enter details for the Primary Drone Mission.")
    primary_mission = get_primary_mission()

    # Get simulated missions (hardcoded)
    simulated_missions = get_simulated_missions()

    # Combine all missions for conflict detection (primary mission first)
    all_missions = [primary_mission] + simulated_missions

    # Run Conflict Detection
    min_safety_distance = 20  # Minimum distance threshold
    detected_conflicts = detect_conflicts(all_missions, min_safety_distance)

    if detected_conflicts:
        print("Detected Conflicts:")
        for conflict in detected_conflicts:
            print(f"  Conflict between {conflict.drone_id1} and {conflict.drone_id2} "
                  f"at {conflict.location} at time {conflict.time} due to {conflict.reason}")
    else:
        print("No conflicts detected.")

    # Visualize the Missions and Conflicts
    visualize_missions(all_missions, detected_conflicts)


# =============================================================================
# Basic Testing (for QA)
# =============================================================================

def run_basic_tests():
    """
    Run basic tests to validate utility functions.
    """
    # Test distance calculation
    p1 = (0, 0, 0)
    p2 = (3, 4, 0)
    assert math.isclose(calculate_distance(p1, p2), 5.0), "Distance calculation error"
    
    # Test interpolation function
    t1 = datetime(2025, 4, 2, 10, 0, 0)
    t2 = datetime(2025, 4, 2, 10, 10, 0)
    wp_a = Waypoint(0, 0, 0, t1)
    wp_b = Waypoint(10, 10, 10, t2)
    mid_time = t1 + (t2 - t1) / 2
    interpolated = interpolate_position(wp_a, wp_b, mid_time)
    assert all(math.isclose(interpolated[i], 5.0, abs_tol=0.1) for i in range(3)), "Interpolation error"
    
    print("Basic tests passed.")


if __name__ == "__main__":
    try:
        run_basic_tests()
        main()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
