| Group No. | Group Name                         | Topic Names               | Description                                                                                          |
| :-------- | :--------------------------------- | :------------------------ | :--------------------------------------------------------------------------------------------------- |
| **1**     | **Operator Room**                  | 1/gameTime_in_sec         | Provides the game time in seconds.                                                                   |
|           |                                    | 1/gameTime_formatted      | Provides the game time as a formatted string.                                                        |
|           |                                    | 1/gameControl             | Topic to control the workflow engine. Commands: START, STOP, PAUSE, SKIP \<workflow_name>            |
|           |                                    | 1/gameState               | Provides a cytoscape graph configuration with the current workflow states.                           |
|           |                                    | 1/gameOptions             | Topic to set game options (ex. player count, game duration).                                         |
| **2**     | **Environment & AI**               | 2/ledstrip/timer          | Topic of the game time display.                                                                      |
|           |                                    | 2/ledstrip/serverroom     | Topic of the LED strip in the server room.                                                           |
|           |                                    | 2/ledstrip/doorserverroom | Topic of the LED strip in the server room above the door.                                            |
|           |                                    | 2/ledstrip/labroom/south  | Topic of the LED strip in the lab room at the back wall on the opposite of the entrance door.        |
|           |                                    | 2/ledstrip/labroom/middle | Topic of the LED strip in the lab room at the server room wall on the opposite of the entrance door. |
|           |                                    | 2/ledstrip/labroom/north  | Topic of the LED strip in the lab room above the entrance door.                                      |
|           |                                    | 2/gyrophare               | Topic to control the gyrophare.                                                                      |
|           |                                    | 2/textToSpeech            | Topic to interact with the text to speech module.                                                    |
| **3**     | **Mission Briefing**               |                           |                                                                                                      |
| **4**     | **Both Doors & First Door Puzzle** | 4/puzzle                  | Topic of the key pad code riddle to open the entrance door.                                          |
|           |                                    | 4/door/entrance           | Topic of the entrance door.                                                                          |
|           |                                    | 4/door/serverRoom         | Topic of the server door.                                                                            |
|           |                                    | 4/globes                  | Topic of globes riddle.                                                                              |
| **5**     | **Safe & Puzzles**                 | 5/safe/activate           | Topic of the safe activation riddle.                                                                 |
|           |                                    | 5/safe/control            | Topic of the key pad to open the safe.                                                               |
| **6**     | **Prototype & Puzzles**            | 6/puzzle/scale            | Topic of the scale which recognizes if the disks are put out of the safe.                            |
|           |                                    | 6/puzzle/terminal         | Topic of the floppy disk riddle terminal.                                                            |
| **7**     | **Second Door Puzzles**            | 7/laser                   | Topic of the laser pointer to open the fuse box.                                                     |
|           |                                    | 7/fusebox/laserDetection  | Topic of the laser recognition which opens the fuse box.                                             |
|           |                                    | 7/fusebox/rewiring0       | Topic of the first rewiring riddle in the fuse box.                                                  |
|           |                                    | 7/fusebox/rewiring1       | Topic of the second rewiring riddle in the fuse box.                                                 |
|           |                                    | 7/fusebox/potentiometer   | Topic of the potentiometer riddle in the fuse box.                                                   |
|           |                                    | 7/robot                   | Topic of the robot riddle to open the server room door.                                              |
| **8**     | **AI Server & Puzzles**            | 8/puzzle/maze             | Topic of the maze riddle in the server room.                                                         |
|           |                                    | 8/puzzle/simon            | Topic of the simon riddle in the server room.                                                        |