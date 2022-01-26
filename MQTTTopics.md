| Group No. | Group Name                         | Topic Name                | Description                                                                                          |
| :-------- | :--------------------------------- | :------------------------ | :--------------------------------------------------------------------------------------------------- |
| **op**    | **Operator Room**                  | op/gameTime_in_sec        | game time in seconds.                                                                                |
|           |                                    | op/gameTime_formatted     | game time as a formatted string.                                                                     |
|           |                                    | op/gameControl            | control the workflow engine. Commands: START, STOP, PAUSE, SKIP \<workflow_name>                     |
|           |                                    | op/gameState              | cytoscape graph configuration with the current workflow states.                                      |
|           |                                    | op/gameOptions            | set game options (ex. player count, game duration).                                                  |
| **env**   | **Environment**                    | env/                      |                                                                                                      |
| **1**     | **Group/Puzzle 1**                 | 1/                        |                                                                                                      |
| **2**     | **Group/Puzzle 2**                 | 2/                        |                                                                                                      |
|           |                                    | 2/ledstrip/timer          | *(legacy)* game time display.                                                                        |
|           |                                    | 2/ledstrip/serverroom     | *(legacy)* LED strip in the server room.                                                             |
|           |                                    | 2/ledstrip/doorserverroom | *(legacy)* LED strip in the server room above the door.                                              |
|           |                                    | 2/ledstrip/labroom/south  | *(legacy)* LED strip in the lab room at the back wall on the opposite of the entrance door.          |
|           |                                    | 2/ledstrip/labroom/middle | *(legacy)* LED strip in the lab room at the server room wall on the opposite of the entrance door.   |
|           |                                    | 2/ledstrip/labroom/north  | *(legacy)* LED strip in the lab room above the entrance door.                                        |
|           |                                    | 2/gyrophare               | *(legacy)* control the gyrophare.                                                                    |
|           |                                    | 2/textToSpeech            | *(legacy)* interact with the text to speech module.                                                  |
| **3**     | **Group/Puzzle 3**                 | 3/gamecontrol             | Control the radio: which puzzle state is currently in play                                           |
|           |                                    | 3/antenna/orientation     | gives information if the angle of the antenna correct                                                |
|           |                                    | 3/map/knob1               | gives information whether knob1 is in correct position                                               |
|           |                                    | 3/map/knob2               | gives information whether knob2 is in correct position                                               |
|           |                                    | 3/map/knob3               | gives information whether knob3 is in correct position                                               |
|           |                                    | 3/touchgame/trialCount    | gives information about the trails the group already had                                             |
|           |                                    | 3/touchgame/displayTime   | the game can either be set in easy or hard mode                                                      |
| **4**     | **Group/Puzzle 4**                 | 4/                        |                                                                                                      |
|           |                                    | 4/door/entrance           | *(legacy)* entrance door.                                                                            |
|           |                                    | 4/door/serverRoom         | *(legacy)* server door.                                                                              |
| **5**     | **Group/Puzzle 5**                 | 5/battery/1/level         | The supposed battery level                                                                           |
|           |                                    | 5/battery/1/location      | The current location of the battery                                                                  |
|           |                                    | 5/battery/1/uid           | The NFC UID of the battery                                                                           |
|           |                                    | 5/control_room/power      | power status of the control room                                                                     |
|           |                                    | 5/safe/control            | *(legacy)* key pad to open the safe.                                                                 |