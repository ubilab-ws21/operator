let json = `{
 "nodes": [{
  "data": {
   "id": "main",
   "name": "main",
   "status": "ACTIVE",
   "type": "SequenceWorkflow"
  }
 }, {
  "data": {
   "id": "Keypad_code_entrance_door",
   "name": "Keypad_code_entrance_door",
   "status": "ACTIVE",
   "type": "Workflow",
   "parent": "main"
  }
 }, {
  "data": {
   "id": "Entrance_door_opening",
   "name": "Entrance_door_opening",
   "status": "INACTIVE",
   "type": "DoorWorkflow",
   "parent": "main"
  }
 }, {
  "data": {
   "id": "Closing_entrance_door_globes",
   "name": "Closing_entrance_door_globes",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "main"
  }
 }, {
  "data": {
   "id": "Lab room",
   "name": "Lab room",
   "status": "INACTIVE",
   "type": "ParallelWorkflow",
   "parent": "main"
  }
 }, {
  "data": {
   "id": "Solve safe",
   "name": "Solve safe",
   "status": "INACTIVE",
   "type": "SequenceWorkflow",
   "parent": "Lab room"
  }
 }, {
  "data": {
   "id": "Activate_safe_lab_room",
   "name": "Activate_safe_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve safe"
  }
 }, {
  "data": {
   "id": "Open_safe_lab_room",
   "name": "Open_safe_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve safe"
  }
 }, {
  "data": {
   "id": "Solve fusebox",
   "name": "Solve fusebox",
   "status": "INACTIVE",
   "type": "SequenceWorkflow",
   "parent": "Lab room"
  }
 }, {
  "data": {
   "id": "Laser_lab_room",
   "name": "Laser_lab_room",
   "status": "INACTIVE",
   "type": "ActivateLaserWorkflow",
   "parent": "Solve fusebox"
  }
 }, {
  "data": {
   "id": "Solve fuse box",
   "name": "Solve fuse box",
   "status": "INACTIVE",
   "type": "ParallelWorkflow",
   "parent": "Solve fusebox"
  }
 }, {
  "data": {
   "id": "Fusebox_laser_detection_lab_room",
   "name": "Fusebox_laser_detection_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve fuse box"
  }
 }, {
  "data": {
   "id": "Fusebox_rewiring0_lab_room",
   "name": "Fusebox_rewiring0_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve fuse box"
  }
 }, {
  "data": {
   "id": "Fusebox_rewiring1_lab_room",
   "name": "Fusebox_rewiring1_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve fuse box"
  }
 }, {
  "data": {
   "id": "Fusebox_potentiometer_lab_room",
   "name": "Fusebox_potentiometer_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve fuse box"
  }
 }, {
  "data": {
   "id": "Robot_lab_room",
   "name": "Robot_lab_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Solve fusebox"
  }
 }, {
  "data": {
   "id": "Server room",
   "name": "Server room",
   "status": "INACTIVE",
   "type": "ParallelWorkflow",
   "parent": "main"
  }
 }, {
  "data": {
   "id": "Floppy_disk_server_room",
   "name": "Floppy_disk_server_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Server room"
  }
 }, {
  "data": {
   "id": "Maze_server_room",
   "name": "Maze_server_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Server room"
  }
 }, {
  "data": {
   "id": "Simon_server_room",
   "name": "Simon_server_room",
   "status": "INACTIVE",
   "type": "Workflow",
   "parent": "Server room"
  }
 }],
 "edges": [{
  "data": {
   "id": "Keypad_code_entrance_door->Entrance_door_opening",
   "source": "Keypad_code_entrance_door",
   "target": "Entrance_door_opening"
  }
 }, {
  "data": {
   "id": "Entrance_door_opening->Closing_entrance_door_globes",
   "source": "Entrance_door_opening",
   "target": "Closing_entrance_door_globes"
  }
 }, {
  "data": {
   "id": "Closing_entrance_door_globes->Lab room",
   "source": "Closing_entrance_door_globes",
   "target": "Lab room"
  }
 }, {
  "data": {
   "id": "Activate_safe_lab_room->Open_safe_lab_room",
   "source": "Activate_safe_lab_room",
   "target": "Open_safe_lab_room"
  }
 }, {
  "data": {
   "id": "Laser_lab_room->Solve fuse box",
   "source": "Laser_lab_room",
   "target": "Solve fuse box"
  }
 }, {
  "data": {
   "id": "Solve fuse box->Robot_lab_room",
   "source": "Solve fuse box",
   "target": "Robot_lab_room"
  }
 }, {
  "data": {
   "id": "Lab room->Server room",
   "source": "Lab room",
   "target": "Server room"
  }
 }]
}`;