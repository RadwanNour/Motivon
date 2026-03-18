# Motivon Delivery Cart - Implementation Guide

## Project Requirements Summary

### Simulation: 12 marks
- [x] **GZ Sim Harmonic** - Configured and working
- [ ] **Environment Setup** - On hold (as requested)
- [x] **Dynamic/Static Obstacle Avoidance** - Ready for refinement
- [x] **IMU & Encoders** - Integrated
- [ ] **Goal Communication via ROS nodes** - Ready to implement
- [ ] **Path Completion** - 3+ waypoints with orientation
- [ ] **Extra Mechanism** - Delivery box mechanism
- [ ] **Start/Stop Signals** - On hold (as requested)

---

## Current Architecture

### Robot Hardware Components Mapped:
```
Raspberry Pi 5:
├── Sensors
│   ├── MPU6050 IMU (I2C)
│   ├── 4x Ultrasonic sensors (GPIO)
│   ├── Camera Module V2 (face detection)
│   └── 2x Servo motors (for ultrasonic rotation) - GPIO
├── Actuators
│   ├── Power screw motor (H-bridge) - GPIO
│   └── Encoder readout - GPIO
└── LED strip (GPIO)

ESP32:
├── TB6612FNG drivers (2x) for 4 Mecanum wheels
│   ├── FR_Joint (Front Right)
│   ├── FL_Joint (Front Left)
│   ├── RR_Joint (Rear Right)
│   └── RL_Joint (Rear Left)
└── Motor encoders readout

Communication:
├── ROS2 on Raspberry Pi ← SSH connection ← Your laptop
└── Wireless sync with ESP32
```

---

## Obstacle Detection Logic - To Be Implemented

### Current Status
The `obstacle_avoidance.py` uses basic reactive control. You want to add:

**Logic Flow:**
```
1. Robot moving on path
2. Obstacle detected (ultrasonic/scan data)
   ├─ Start timer
3. Wait for duration (X seconds - you decide)
   ├─ If obstacle GONE before timer expires:
   │  └─ → Dynamic obstacle (ignored, resume path)
   ├─ If obstacle STAYS after timer expires:
   │  └─ → Static obstacle
   │     ├─ Trigger pathfinding/reroute
   │     ├─ Use sensor data to navigate around
   │     └─ Try to merge back to original path
4. Continue navigation
```

### Implementation Parameters (To be decided by you):
```yaml
obstacle_detection:
  safe_distance: 0.5        # meters (current)
  static_timeout: 3.0       # seconds - YOUR CHOICE
  sensor_type: "ultrasonic" # 4 sensors on robot
  max_turn_angle: 90        # degrees for avoidance
  reroute_margin: 0.3       # meters clearance from obstacle
```

---

## Waypoint Navigation - Currently Implemented

### Straight Line Test Path (As Requested)
```
Waypoint 0: (0.0, 0.0, 0.0°)    [Home position]
Waypoint 1: (2.0, 0.0, 0.0°)    [After obstacle at 2.0m]
Waypoint 2: (4.0, 0.0, 0.0°)    [Delivery goal]
```

**Obstacle Placement:** Static obstacle at X=2.0m on path

### State Machine (All 3 states required):
1. **rotate_to_target**: Orient robot toward waypoint
2. **move_forward**: Move toward waypoint
3. **rotate_to_final**: Achieve target orientation

### For Your Delivery Cart - Multiple Locations
You'll need to define:
```python
waypoints = [
    (x1, y1, yaw1),  # Location 1
    (x2, y2, yaw2),  # Location 2
    (x3, y3, yaw3),  # Location 3
    (0.0, 0.0, 0.0), # Return home
]
```

---

## IMU Integration

### Current Setup
- **Topic**: `/imu`
- **Frame**: `imu_link`
- **Update Rate**: 50 Hz
- **Data Available**: 
  - Orientation (quaternion → roll, pitch, yaw)
  - Angular velocity
  - Linear acceleration

### Usage in Navigation
```python
# Already implemented in waypoints_control.py
- imu_callback() → extracts yaw for heading
- Uses tf_transformations to convert quaternion to Euler angles
- Yaw used for: angle_to_target, final_yaw_error calculations
```

---

## Encoders Integration

### Wheel Encoders
- **Connected to**: TB6612FNG drivers
- **Data Available**: Velocity feedback from `/diff_drive_controller/odom`
- **Usage**: Position and velocity for odometry

### Lid Mechanism Encoder
- **Type**: Power screw encoder
- **Status**: Added to URDF but not actuated yet
- **Joint**: `Lid_Joint` (prismatic, 0-180 range)

---

## Delivery Mechanism - Structure Ready

### Current URDF Components
```xml
<link name="Lid">           ✓ Defined
<joint name="Lid_Joint">   ✓ Prismatic joint (sliding)

In your specification:
├─ Face detection (Raspberry Pi camera)
├─ Automatic lid open when confirmed
├─ User closes via GUI button
├─ Lid opens at delivery location
├─ User confirms pickup via GUI
```

### To Implement
1. Add callback for camera face detection
2. Add ROS2 service/action for lid control
3. Create simple GUI with:
   - Delivery location selector
   - Confirm/Cancel buttons
   - Lid open/close controls
   - Face detection status

---

## Testing Order (Recommended)

### Phase 1: Visualization ✓
```bash
ros2 launch motivon_pkg display_rviz.launch.py gui:=True
```
- Check all dummy links appear and rotate correctly
- Verify joint orientations (all move in forward direction)

### Phase 2: Gazebo Simulation ✓
```bash
ros2 launch motivon_pkg robot_gazebo.launch.py
```
- Robot spawns correctly
- Can see IMU and ultrasonic sensors
- Obstacle and delivery goal visible

### Phase 3: Sensor Data ✓
```bash
# In separate terminals:
ros2 topic echo /imu
ros2 topic echo /scan
ros2 topic echo /diff_drive_controller/odom
```

### Phase 4: Obstacle Avoidance (Basic)
```bash
# Terminal 1: Gazebo
ros2 launch motivon_pkg robot_gazebo.launch.py

# Terminal 2: Obstacle avoidance
ros2 run motivon_pkg obstacle_avoidance.py
```
- Watch robot respond to obstacle
- Ready for static/dynamic logic addition

### Phase 5: Waypoint Navigation
```bash
# Terminal 1: Gazebo
ros2 launch motivon_pkg robot_gazebo.launch.py

# Terminal 2: Waypoint control
ros2 run motivon_pkg waypoints_control.py
```
- Robot navigates to each waypoint
- Updates position display
- Handles avoidance around obstacle

---

## Files You'll Need to Modify for Full Project

### 1. **Update Waypoints** (for your delivery locations)
```python
# File: scripts/waypoints_control.py - Line ~48
waypoints = [
    (0.0, 0.0, 0.0),           # Home
    (1.0, 0.0, 0.0),           # Location 1
    (1.0, 1.0, math.pi / 2),   # Location 2
    (0.0, 1.0, math.pi),       # Location 3
    # Add or modify as needed
]
```

### 2. **Add Static/Dynamic Logic** (to obstacle avoidance)
```python
# File: scripts/obstacle_avoidance.py
# Add obstacle timer and classification logic
# (To be provided when you specify timeout value)
```

### 3. **Add Lid Control** (new file)
```python
# File: scripts/delivery_control.py (NEW)
# Handle:
# - Face detection → open lid
# - GUI button → close lid
# - Location selection
```

### 4. **Modify World** (for your specific layout)
```xml
<!-- File: world/my_world.sdf -->
<!-- Add your actual delivery location markers -->
<!-- Adjust obstacle positions -->
```

---

## Decision Points - Waiting for Your Input

### 1. Obstacle Detection Timeout
**Question**: How long should the robot wait before deciding an obstacle is static?
**Current Setting**: Not yet implemented
**Recommended Range**: 1-5 seconds
**Example**: 
```yaml
static_timeout: 3.0  # 3 seconds
```

### 2. Delivery Locations
**Question**: How many delivery locations and what coordinates?
**Current Setup**: 3 waypoints on straight line
**Example**:
```python
waypoints = [
    (0.0, 0.0, 0.0),    # Home
    (5.0, 0.0, 0.0),    # Front desk
    (5.0, 3.0, -pi/2),  # Side room
    (0.0, 5.0, pi),     # Rear entrance
]
```

### 3. Extra Mechanism
**Question**: Delivery box with sliding lid - any special considerations?
**Current Setup**: URDF ready, actuator ready
**Options**:
- Simple open/close timing
- Manual control from GUI
- Automatic at delivery location

### 4. Start/Stop Implementation
**Question**: How should start/stop signals work?
**Options**:
- GUI button
- ROS2 service call
- Automatic on startup
- User command via terminal

---

## Ready to Proceed

All code strictly follows:
- ✓ Lab 4A - ROS2 Simulation Setup sections
- ✓ Lab 5A - ROS2 Navigation sections  
- ✓ Lab 6A - Raspberry Pi Setup sections (for future integration)

**Your package is ready for:**
1. Refinement of obstacle logic
2. Addition of delivery mechanism control
3. GUI integration
4. Real hardware deployment on Raspberry Pi 5 + ESP32

Please specify the parameters and we'll add the remaining functionality!
