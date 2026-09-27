# Project Plan

## 1. Aim

Build a camera-guided system that uses a robotic arm to detect an object, pick it up, and relocate it to a defined destination.

## 2. Minimum Requirements

- [ ] Place one object within the camera's field of view.
- [ ] Detect the object and determine a usable pick position.
- [ ] Calculate and document the robot's safe reachable workspace.
- [ ] Verify that the detected pick position and destination are safely reachable before commanding motion; reject any object that cannot be reached or grasped safely.
- [ ] Pick up the object with the robotic arm.
- [ ] Move the object away from its original position.
- [ ] Place and release the object at a defined destination.
- [ ] Reproduce the complete sequence reliably in a demonstration.

## 3. Optional Extensions

### Robustness

- [ ] Test the effect of common ambient-light changes.
- [ ] Add controlled lighting if it improves repeatability.
- [ ] Test different object positions within the working area.
- [ ] Test a limited range of planar object orientations.
- [ ] Detect a failed pick and retry or stop safely.
- [ ] Record success rates and the causes of failure.

### Additional Functions

- [ ] Process more than one object.
- [ ] Read a QR code or barcode.
- [ ] Route unknown items to a rejection area.
- [ ] Record item identity and processing status locally.

## 4. Tentative Technical Direction

Python and OpenCV appear suitable for the initial vision work. Robot control should preferably use the supported manufacturer or ROS interface. The final approach will be selected after inspecting the equipment and completing basic control and camera tests.

## 5. Schedule

The project lasts 11 weeks. Engineering is limited to the first eight weeks at approximately two project days per week. Weeks 9–11 are reserved for analysis and writing.

| Week | Intended outcome |
|---|---|
| 1 | Confirm the equipment and environment; complete one controlled movement. |
| 2 | Establish safe and repeatable arm and gripper control. |
| 3 | Detect one object and estimate its image position. |
| 4 | Relate camera observations to robot positions. |
| 5 | Complete the minimum pick, move and place sequence. |
| 6 | Improve repeatability and begin selected extensions. |
| 7 | Test robustness and record results. |
| 8 | Complete validation, evidence and documentation. |
| 9 | Analyse results and prepare figures. |
| 10 | Draft the report. |
| 11 | Revise and prepare the submission. |

No new feature should normally begin after Week 8.

## 6. To Do

- [ ] Confirm the supported control software and ROS environment.
- [ ] Confirm how the equipment should be stored between sessions.
- [ ] Inspect the controller, gripper, cables and accessories.
- [ ] Confirm the safe operating and emergency-stop procedures.
- [ ] Select a simple test object and destination area.
- [ ] Inspect the available camera and mounting hardware.
- [ ] Confirm access to the university's 3D-printing facilities, materials and lead time.
- [ ] Decide whether a fixed lamp is needed for controlled testing.
