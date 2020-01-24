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

let debug = `{
 'elements': {
  'nodes': [{
   'data': {
    'id': 'main',
    'name': 'main',
    'status': 'ACTIVE',
    'type': 'SequenceWorkflow'
   },
   'position': {
    'x': 574.4247734067978,
    'y': 444.9099702248978
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Keypad_code_entrance_door',
    'name': 'Keypad_code_entrance_door',
    'status': 'ACTIVE',
    'type': 'Workflow',
    'parent': 'main'
   },
   'position': {
    'x': 615.7757403730923,
    'y': 203.17598544611735
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Entrance_door_opening',
    'name': 'Entrance_door_opening',
    'status': 'INACTIVE',
    'type': 'DoorWorkflow',
    'parent': 'main'
   },
   'position': {
    'x': 378.7035918824164,
    'y': 164.9710379989948
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Closing_entrance_door_globes',
    'name': 'Closing_entrance_door_globes',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'main'
   },
   'position': {
    'x': 308.1588143406673,
    'y': 233.8390784648508
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Lab room',
    'name': 'Lab room',
    'status': 'INACTIVE',
    'type': 'ParallelWorkflow',
    'parent': 'main'
   },
   'position': {
    'x': 600.6115797668974,
    'y': 550.0631122783196
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Solve safe',
    'name': 'Solve safe',
    'status': 'INACTIVE',
    'type': 'SequenceWorkflow',
    'parent': 'Lab room'
   },
   'position': {
    'x': 499.0138953689145,
    'y': 367.9917184591036
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Activate_safe_lab_room',
    'name': 'Activate_safe_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve safe'
   },
   'position': {
    'x': 528.1770488935642,
    'y': 402.9048719837533
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Open_safe_lab_room',
    'name': 'Open_safe_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve safe'
   },
   'position': {
    'x': 458.35074184426486,
    'y': 333.0785649344539
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Solve fusebox',
    'name': 'Solve fusebox',
    'status': 'INACTIVE',
    'type': 'SequenceWorkflow',
    'parent': 'Lab room'
   },
   'position': {
    'x': 654.9574385838539,
    'y': 668.4711851379893
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Laser_lab_room',
    'name': 'Laser_lab_room',
    'status': 'INACTIVE',
    'type': 'ActivateLaserWorkflow',
    'parent': 'Solve fusebox'
   },
   'position': {
    'x': 763.37241768953,
    'y': 555.3947106537933
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Solve fuse box',
    'name': 'Solve fuse box',
    'status': 'INACTIVE',
    'type': 'ParallelWorkflow',
    'parent': 'Solve fusebox'
   },
   'position': {
    'x': 661.8100062551994,
    'y': 707.0476596221854
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Fusebox_laser_detection_lab_room',
    'name': 'Fusebox_laser_detection_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve fuse box'
   },
   'position': {
    'x': 661.8100062551994,
    'y': 644.0476596221854
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Fusebox_rewiring0_lab_room',
    'name': 'Fusebox_rewiring0_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve fuse box'
   },
   'position': {
    'x': 637.8100062551994,
    'y': 728.0476596221854
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Fusebox_rewiring1_lab_room',
    'name': 'Fusebox_rewiring1_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve fuse box'
   },
   'position': {
    'x': 637.8100062551994,
    'y': 770.0476596221854
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Fusebox_potentiometer_lab_room',
    'name': 'Fusebox_potentiometer_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve fuse box'
   },
   'position': {
    'x': 657.8100062551994,
    'y': 686.0476596221854
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Robot_lab_room',
    'name': 'Robot_lab_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Solve fusebox'
   },
   'position': {
    'x': 548.0424594781778,
    'y': 560.0349898876307
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Server room',
    'name': 'Server room',
    'status': 'INACTIVE',
    'type': 'ParallelWorkflow',
    'parent': 'main'
   },
   'position': {
    'x': 850.1907324729284,
    'y': 153.2722808276102
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Floppy_disk_server_room',
    'name': 'Floppy_disk_server_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Server room'
   },
   'position': {
    'x': 850.1907324729284,
    'y': 111.27228082761019
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Maze_server_room',
    'name': 'Maze_server_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Server room'
   },
   'position': {
    'x': 824.6907324729284,
    'y': 195.2722808276102
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }, {
   'data': {
    'id': 'Simon_server_room',
    'name': 'Simon_server_room',
    'status': 'INACTIVE',
    'type': 'Workflow',
    'parent': 'Server room'
   },
   'position': {
    'x': 828.6907324729284,
    'y': 153.2722808276102
   },
   'group': 'nodes',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': false,
   'classes': ''
  }],
  'edges': [{
   'data': {
    'id': 'Keypad_code_entrance_door->Entrance_door_opening',
    'source': 'Keypad_code_entrance_door',
    'target': 'Entrance_door_opening'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }, {
   'data': {
    'id': 'Entrance_door_opening->Closing_entrance_door_globes',
    'source': 'Entrance_door_opening',
    'target': 'Closing_entrance_door_globes'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }, {
   'data': {
    'id': 'Closing_entrance_door_globes->Lab room',
    'source': 'Closing_entrance_door_globes',
    'target': 'Lab room'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }, {
   'data': {
    'id': 'Activate_safe_lab_room->Open_safe_lab_room',
    'source': 'Activate_safe_lab_room',
    'target': 'Open_safe_lab_room'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }, {
   'data': {
    'id': 'Laser_lab_room->Solve fuse box',
    'source': 'Laser_lab_room',
    'target': 'Solve fuse box'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }, {
   'data': {
    'id': 'Solve fuse box->Robot_lab_room',
    'source': 'Solve fuse box',
    'target': 'Robot_lab_room'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }, {
   'data': {
    'id': 'Lab room->Server room',
    'source': 'Lab room',
    'target': 'Server room'
   },
   'position': {
    'x': 0,
    'y': 0
   },
   'group': 'edges',
   'removed': false,
   'selected': false,
   'selectable': true,
   'locked': false,
   'grabbable': true,
   'pannable': true,
   'classes': ''
  }]
 },
 'style': [{
  'selector': 'node',
  'style': {
   'label': 'data(name)',
   'color': 'rgb(0,0,0)',
   'font-family': 'Verdana, Geneva, sans-serif',
   'text-valign': 'center',
   'text-halign': 'center',
   'background-color': 'rgb(147,161,161)'
  }
 }, {
  'selector': 'node[status = \\\\'
  ACTIVE\\\\ ']',
  'style': {
   'background-color': 'rgb(133,153,0)'
  }
 }, {
  'selector': 'node[status = \\\\'
  INACTIVE\\\\ ']',
  'style': {
   'background-color': 'rgb(203,75,22)'
  }
 }, {
  'selector': ':parent',
  'style': {
   'text-valign': 'top',
   'text-halign': 'center',
   'background-color': 'rgb(0,43,54)'
  }
 }, {
  'selector': 'edge',
  'style': {
   'curve-style': 'bezier',
   'target-arrow-shape': 'triangle'
  }
 }, {
  'selector': 'core',
  'style': {
   'active-bg-size': '0px'
  }
 }],
 'data': {},
 'zoomingEnabled': false,
 'userZoomingEnabled': false,
 'zoom': 0.8,
 'minZoom': 1e-50,
 'maxZoom': 1e+50,
 'panningEnabled': false,
 'userPanningEnabled': false,
 'pan': {
  'x': 0,
  'y': 0
 },
 'boxSelectionEnabled': false,
 'renderer': {
  'name': 'canvas'
 }
}`;