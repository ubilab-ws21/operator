| Group No. | Group Name                         | Topic Name                   | Control Topic | Description                                                                                          |
| :-------- | :--------------------------------- | :------------------------    | :-----------: | :--------------------------------------------------------------------------------------------------- |
| **op**    | **Operator Room**                  | op/gameTime_in_sec           |               | game time in seconds.                                                                                |
|           |                                    | op/gameTime_remain_in_sec    |               | remaining game time in seconds.                                                                      |
|           |                                    | op/gameTime_formatted        |               | game time as a formatted string.                                                                     |
|           |                                    | op/gameTime_remain_formatted |               | remaining game time as a formatted string.                                                           |
|           |                                    | op/gameControl               |               | control the workflow engine. Commands: START, STOP, PAUSE, SKIP \<workflow_name>                     |
|           |                                    | op/gameState                 |               | cytoscape graph configuration with the current workflow states.                                      |
|           |                                    | op/gameOptions               |               | set game options (ex. player count, game duration).                                                  |
| **env**   | **Environment**                    | env/video                    |               | Play video files on the beamer                                                                       |
|           |                                    | env/powerfail                | x             | Blocking trigger waiting for signal from AR app to start the power fail scenario                     |
| **1**     | **Group/Puzzle 1**                 | 1/cube/state                 | x             | Game state of the Cube puzzle                                                                        |
|           |                                    | 1/panel/state                | x             | Game state of the Panel puzzle                                                                       |
| **2**     | **Group/Puzzle 2**                 | 2/esp                        | x             | Control topic of the knock knock / switchboard puzzle                                                |
|           |                                    | 2/ledstrip/timer             |               | Game time display.                                                                        |
|           |                                    | 2/ledstrip/serverroom        |               | LED strip in the server room.                                                             |
|           |                                    | 2/ledstrip/labroom/south     |               | LED strip in the lab room at the back wall on the opposite of the entrance door.          |
|           |                                    | 2/ledstrip/labroom/middle    |               | LED strip in the lab room at the server room wall on the opposite of the entrance door.   |
|           |                                    | 2/ledstrip/labroom/north     |               | LED strip in the lab room above the entrance door.                                        |
|           |                                    | 2/ledstrip/lobby             |               | LED strip in the lobby                           .                                        |
|           |                                    | 2/gyrophare                  |               | control the gyrophare.                                                                    |
|           |                                    | 2/textToSpeech               |               | *(legacy)* interact with the text to speech module.                                                  |
| **3**     | **Group/Puzzle 3**                 | 3/gamecontrol/antenna        | x             | start the first puzzle & receive updates on it                                                       |
|           |                                    | 3/gamecontrol/map            | x             | start the second puzzle & receive updates on it                                                      |
|           |                                    | 3/gamecontrol/touchgame      | x             | start the third puzzle & receive updates on it                                                       |
|           |                                    | 3/audiocontrol/roomsolved    | x             | play final message when the room is solved                                                           |
| **4**     | **Group/Puzzle 4**                 | 4/gamecontrol                | x             | puzzle control topic                                                                                 |
|           |                                    | 4/door/entrance              | x             | *(legacy)* entrance door.                                                                            |
|           |                                    | 4/door/serverRoom            | x             | *(legacy)* server door.                                                                              |
|           |                                    | 4/puzzle                     | x             | *(legacy)* first door keypad.                                                                        |
| **5**     | **Group/Puzzle 5**                 | 5/battery/1/level            |               | The supposed battery level                                                                           |
|           |                                    | 5/battery/1/location         |               | The current location of the battery                                                                  |
|           |                                    | 5/battery/1/uid              |               | The NFC UID of the battery                                                                           |
|           |                                    | 5/control_room/power         | x             | power status of the control room                                                                     |
|           |                                    | 5/safe/control               |               | *(legacy)* key pad to open the safe.                                                                 |
