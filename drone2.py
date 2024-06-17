import sys
import itertools

is_drone = True

#from tello_sim import Simulator as Tello
from djitellopy import Tello

GRID_SIZE = 5

def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def input_waypoints():
    waypoints = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            print(f"Enter waypoint at position ({i}, {j}) (y/n): ", end="")
            if input().strip().lower() == 'y':
                waypoints.append((i, j))
    return waypoints

def solve_tsp(waypoints):
    min_path = None
    min_distance = float('inf')
    
    # Include returning to (0, 0) in the permutations
    waypoints_with_home = waypoints + [(0, 0)]
    
    for perm in itertools.permutations(waypoints_with_home):
        current_distance = sum(distance(perm[i], perm[i+1]) for i in range(len(perm) - 1))
        current_distance += distance(perm[-1], perm[0])
        
        if current_distance < min_distance:
            min_distance = current_distance
            min_path = perm
            
    return min_path, min_distance

def generate_commands(path):
    commands = []
    for i in range(len(path) - 1):
        p1 = path[i]
        p2 = path[i + 1]
        while p1[0] != p2[0]:
            commands.append("move forward" if p1[0] < p2[0] else "move backward")
            p1 = (p1[0] + 1, p1[1]) if p1[0] < p2[0] else (p1[0] - 1, p1[1])
        while p1[1] != p2[1]:
            commands.append("move right" if p1[1] < p2[1] else "move left")
            p1 = (p1[0], p1[1] + 1) if p1[1] < p2[1] else (p1[0], p1[1] - 1)
    
    # Add commands to return to (0, 0)
    while path[-1] != (0, 0):
        p1 = path[-1]
        if p1[0] != 0:
            commands.append("move forward" if p1[0] > 0 else "move backward")
            p1 = (p1[0] - 1, p1[1]) if p1[0] > 0 else (p1[0] + 1, p1[1])
        elif p1[1] != 0:
            commands.append("move right" if p1[1] > 0 else "move left")
            p1 = (p1[0], p1[1] - 1) if p1[1] > 0 else (p1[0], p1[1] + 1)
        path.append(p1)
    
    return commands

def send_commands_to_drone(commands):
    tello = Tello()

    if "connect" in dir(tello):
        tello.connect()
    tello.takeoff()

    for command in commands:
        if command == "move forward":
            if is_drone:
                tello.move_forward(30)
            else:
                tello.forward(30)
        elif command == "move backward":
            if is_drone:
                tello.move_back(30)
            else:
                tello.back(30)
        elif command == "move left":
            if is_drone:
                tello.move_left1(30)
            else:
                tello.left(30)
        elif command == "move right":
            if is_drone:
                tello.move_right(30)
            else:
                tello.right(30)

    tello.land()

def print_grid_with_waypoints(waypoints):
    grid = [['.' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for waypoint in waypoints:
        grid[GRID_SIZE - 1 - waypoint[1]][waypoint[0]] = 'W'  # Adjust coordinates for rotation

    print("Grid with waypoints:")
    print()
    for row in range(GRID_SIZE):
        print(f"{GRID_SIZE - 1 - row} ", end="")  # Print row index
        for col in range(GRID_SIZE):
            print(f"{grid[row][col]} ", end="")
        print()
    print("  ", end="")
    for col in range(GRID_SIZE):
        print(f"{col} ", end="")
    print()

def main():

    waypoints = input_waypoints()
    if not waypoints:
        print("No waypoints entered.")
        return
    
    print_grid_with_waypoints(waypoints)
    
    path, distance = solve_tsp(waypoints)
    print(f"\nOptimal path: {path}")
    print(f"Minimum distance: {distance}")
    
    commands = generate_commands(path)
    for command in commands:
        print(command)
    
    send_commands_to_drone(commands)

if __name__ == "__main__":
    main()
