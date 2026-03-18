# Motivon Delivery Cart Robot - ROS2 Setup Complete

## Project Overview
This is a delivery cart robot with:
- **Drivetrain**: 4 Mecanum wheels with encoders (TB6612FNG drivers)
- **Delivery Mechanism**: Box with sliding lid actuated by power screw (H-bridge motor with encoder)
- **Sensors**:
  - IMU: MPU6050 (GY-6500)
  - Ultrasonic sensors: 4 units (2 on servos for rotation)
  - Raspberry Pi 5 Camera Module V2 (face confirmation)
  - LED strip for state monitoring
- **Computing**: Raspberry Pi 5 (sensors/servos) + ESP32 (other components)

## ROS2 Package Conversion Complete ✓

### 1. **Package Configuration (ROS1 → ROS2)**
   - ✓ `package.xml`: Updated from format 2 to format 3
   - ✓ Buildtool: Changed from `catkin` to `ament_cmake`
   - ✓ Added all dependencies (ros2_control, ros2_controllers, ros_gz, rclpy, etc.)
   - ✓ `CMakeLists.txt`: Converted to ROS2 standards with proper install directives

### 2. **URDF Enhancements**
   - ✓ **Dummy Links Added**:
     - 1 center dummy link (fixed to RobotBody)
     - 2 revolving dummy links (continuous joints around Z-axis)
     - 2 fixed dummy links (one at front-right, one at front-left)
   - ✓ **ROS2 Control Block**: Added for all 4 wheel joints (FR, FL, RR, RL)
   - ✓ **Gazebo Plugin**: Added for ros2_control integration
   - ✓ **IMU Sensor**: MPU6050 integration with Gazebo plugin
   - ✓ **Ultrasonic Sensor**: LiDAR/GPU LiDAR simulation with ray plugin

### 3. **Visualization Setup (Lab 4A - Section III)**
   - ✓ Created `launch/display_rviz.launch.py` with joint state publisher GUI
   - ✓ Created `rviz/config.rviz` with robot model, grid, and TF visualization
   - ✓ Can launch with: `ros2 launch motivon_pkg display_rviz.launch.py gui:=True`

### 4. **Joint Control Configuration (Lab 4A - Section IV)**
   - ✓ Created `config/controllers.yaml` with:
     - Differential drive controller for Mecanum wheels
     - Joint state broadcaster
     - Velocity limits and acceleration constraints
     - Odometry publishing configuration

### 5. **Gazebo Simulation (Lab 4A - Section IV & Environment Setup)**
   - ✓ Created `launch/robot_gazebo.launch.py` with:
     - Gazebo environment loading
     - ROS-Gazebo bridge for topics
     - Robot spawning
     - Controller manager integration
   - ✓ Created `world/my_world.sdf` with:
     - Ground plane with physics
     - Static obstacle on the path (for testing)
     - Delivery goal marker (green cylinder)
     - Proper lighting and physics engine

### 6. **Sensor Integration (Lab 4A - Sections V & VI)**
   - ✓ IMU sensor with update rate 50 Hz
   - ✓ Ultrasonic/LiDAR sensor (640 samples, 10m range)
   - ✓ Bridge configuration for: `/imu`, `/scan`, `/odom`, `/cmd_vel`

### 7. **Navigation Scripts (Lab 5A)**
   - ✓ `scripts/obstacle_avoidance.py`: Basic reactive obstacle avoidance
     - Monitors front ranges from LaserScan
     - Turns when obstacle detected (distance < 0.5m)
     - Moves forward when path is clear
   - ✓ `scripts/waypoints_control.py`: Waypoint navigation with state machine
     - Currently configured with 3 waypoints along X-axis (0, 2, 4 meters)
     - States: rotate_to_target → move_forward → rotate_to_final
     - Uses IMU for orientation, odometry for velocity

## File Structure
```
motivon_pkg/
├── CMakeLists.txt
├── package.xml
├── urdf/
│   └── Robot_SimplifiedCAD.urdf (with dummy links, ros2_control, sensors)
├── meshes/
│   └── (STL files)
├── config/
│   ├── controllers.yaml
│   └── joint_names_Robot_SimplifiedCAD.yaml
├── launch/
│   ├── display_rviz.launch.py
│   └── robot_gazebo.launch.py
├── rviz/
│   └── config.rviz
├── world/
│   └── my_world.sdf
└── scripts/
    ├── obstacle_avoidance.py
    └── waypoints_control.py
```

## Build Status
✓ Package built successfully with `colcon build --symlink-install`

## Next Steps for Project Requirements

### Immediate (Ready to implement):
1. **Obstacle Detection with Static/Dynamic Logic** 
   - Modify `scripts/obstacle_avoidance.py` with timing logic
   - Obstacle stays > X seconds = static → reroute
   - Obstacle disappears < X seconds = dynamic → resume path
   
2. **Waypoint Path Design**
   - Update waypoints in `scripts/waypoints_control.py`
   - Currently set to straight line (0→2→4 meters on X-axis) for testing

3. **Delivery Mechanism Control**
   - Add Lid_Joint actuation to launch file
   - Integrate with face confirmation callback

4. **Multiple Target Positions**
   - Expand waypoints list with different orientations
   - Add homepoint return logic

### To Be Added (Awaiting your specifications):
1. **Start/Stop Signals** - Control node integration
2. **Environment Details** - Specific map layout
3. **Face Confirmation Logic** - Camera module integration
4. **GUI for Delivery Locations** - User interface
5. **LED Strip State Monitoring** - Status indication
6. **Dynamic Obstacle Avoidance** - Moving obstacle handling

## Commands Reference

### Build
```bash
cd ~/motivon_ws
colcon build --symlink-install --packages-select motivon_pkg
source install/setup.bash
```

### Launch RViz Visualization
```bash
ros2 launch motivon_pkg display_rviz.launch.py gui:=True
```

### Launch Gazebo Simulation
```bash
ros2 launch motivon_pkg robot_gazebo.launch.py
```

### Run Obstacle Avoidance (in separate terminal)
```bash
ros2 run motivon_pkg obstacle_avoidance.py
```

### Run Waypoint Navigation (in separate terminal)
```bash
ros2 run motivon_pkg waypoints_control.py
```

### Check Topics
```bash
# List all active topics
ros2 topic list

# Monitor specific topics
ros2 topic echo /imu
ros2 topic echo /scan
ros2 topic echo /diff_drive_controller/odom
```

## Notes
- All code follows Lab 4A and Lab 5A standards exactly
- Package ready for Gazebo Harmonic with GZ-ROS2 bridge
- Dummy links are configured with visual materials for debugging (red center, blue/green revolving, yellow/cyan fixed)
- World contains test obstacle and delivery goal marker
- Ready for next phase: obstacle logic refinement and delivery mechanism integration
