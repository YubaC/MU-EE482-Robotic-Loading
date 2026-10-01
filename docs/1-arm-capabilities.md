# Robot Arm Capability Notes

Current setup: DYNAMIXEL SDK 4.1.0 + OpenCR usb_to_dxl + XM430-W350-T.
[x] Verified in this project; [ ] To implement or verify.

| Degree of freedom       | DYNAMIXEL (Servo) ID | Current Operating Mode                 | Joint range / gripper opening                                                        |
| ----------------------- | -------------------: | -------------------------------------- | ------------------------------------------------------------------------------------ |
| Base rotation           |                   11 | 3: Position Control Mode               | Approximately 3° round trip verified; mechanical limits to be calibrated             |
| Shoulder                |                   12 | To be checked                          | To be calibrated                                                                     |
| Elbow                   |                   13 | To be checked                          | To be calibrated                                                                     |
| Wrist pitch             |                   14 | To be checked                          | To be calibrated                                                                     |
| Gripper opening/closing |                   15 | 5: Current-based Position Control Mode | Approximately 7° actuator rotation verified; opening in millimetres to be calibrated |

The SDK does not define the arm's mechanical limits or gripper opening range. Model limits from other controller libraries are not applied here.

## Units and Conversion

n denotes the register integer after decoding its signedness. R = Read Only; RW = Read/Write. Access permissions follow the XM430 Control Table.

| Physical quantity                        | Value per count                       | Conversion formula                    | Register address                                          | Data type                           | Notes                                                                                                                       |
| ---------------------------------------- | ------------------------------------- | ------------------------------------- | --------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Actuator position / angular displacement | 360/4096 ≈ 0.08789°                   | Δθ = Δn × 360/4096                    | Present Position: 132 (R); Goal Position: 116 (RW)        | 32-bit signed integer               | Joint angles require zero reference, direction and offset; Position Control Mode defaults to a single-turn range of 0–4095  |
| Motor current                            | Approximately 2.69 mA                 | I = n × 2.69 mA                       | Present Current: 126 (R); Goal Current: 102 (RW)          | 16-bit signed integer               | Goal Current is the current target in mode 0 and limits current in mode 5; not a direct measurement of gripping force       |
| Rotational velocity                      | Approximately 0.229 RPM               | v = n × 0.229 RPM                     | Present Velocity: 128 (R); Goal Velocity: 104 (RW)        | 32-bit signed integer               | Goal Velocity is used in Velocity Control Mode; a negative value indicates the opposite direction                           |
| Profile Velocity / motion duration       | Approximately 0.229 RPM / 1 ms        | v = n × 0.229 RPM; or t = n ms        | Profile Velocity: 112 (RW)                                | 32-bit unsigned integer             | Drive Mode selects Velocity-based Profile or Time-based Profile; 0 is a special setting, not a command to remain stationary |
| Profile Acceleration / acceleration time | Approximately 214.577 rev/min² / 1 ms | a = n × 214.577 rev/min²; or t = n ms | Profile Acceleration: 108 (RW)                            | 32-bit unsigned integer             | Interpretation depends on Drive Mode; 0 is a special setting                                                                |
| PWM duty cycle                           | Approximately 0.113%                  | duty ≈ n × 0.113%                     | Present PWM: 124 (R); Goal PWM: 100 (RW)                  | 16-bit signed integer               | Limits or controls PWM output; not a current or torque value                                                                |
| Input voltage                            | 0.1 V                                 | U = n × 0.1 V                         | Present Input Voltage: 144 (R)                            | 16-bit unsigned integer             | Supply voltage at the DYNAMIXEL                                                                                             |
| Temperature                              | 1°C                                   | T = n °C                              | Present Temperature: 146 (R)                              | 8-bit unsigned integer              | Internal DYNAMIXEL temperature                                                                                              |
| Gripper opening between fingers          | To be calibrated                      | w = f(n)                              | Present Position: 132 (R); Goal Position: 116 (RW), ID 15 | Raw position: 32-bit signed integer | Requires the linkage mapping; the SDK has no built-in conversion to millimetres                                             |

SDK return values are not necessarily sign-decoded: for a b-bit raw value ≥ 2^(b−1), the signed value is raw value − 2^b. Units and data interpretation come from the XM430 Control Table; packet encoding and communication are handled by the SDK.

## Capabilities and Improvement Checklist

- [x] Device communication: serial connection, ping/model identification and register reads/writes; COM3, 1 Mbps, Protocol 2.0, IDs 11–15.
- [x] Single-axis position control: Goal Position, Torque Enable, low-speed profiles and output limits, with Present Position feedback; base and gripper verified.
- [x] Basic status feedback: Present Position, Present Input Voltage, Present Temperature, Hardware Error Status and Torque Enable.
- [ ] Joint-angle / gripper-opening interface: calibrate direction, zero reference, mechanical limits and opening conversion; test shoulder, elbow and wrist; provide commands in degrees / millimetres.
- [ ] Coordinated multi-joint motion: use GroupSyncRead/GroupSyncWrite and generate time-dependent joint trajectories; synchronous writes do not perform trajectory planning.
- [ ] Grasp feedback and compliant control: read Present Current, Present Velocity and Moving Status; limit gripper output in Current-based Position Control Mode; combine feedback with vision to detect contact, successful grasp and slipping. Quantitative force estimation / constant-force control requires calibration or additional sensors.
- [ ] Control strategy tuning: investigate Position PID Gain, Feedforward Gains, Current Control Mode (0) or Velocity Control Mode (1) as needed; Extended Position Control Mode (4) does not make the assembled arm mechanically capable of multiple turns.
- [ ] Fault and communication protection: check firmware support, configure Bus Watchdog, enforce limits and handle errors; software protection does not replace a hardware emergency stop.
- [ ] End-effector control and vision-guided grasping: object detection, coordinate calibration, inverse kinematics, reachability / collision checks, joint trajectory generation and grasp verification.

Reference: [XM430 Control Table](official/robotis/xm430-w350.md). SDK interfaces follow the installed version 4.1.0.
