# Operator Room

## Table of content
- [Operator Room](#operator-room)
  - [Table of content](#table-of-content)
  - [What is this about?](#what-is-this-about)
  - [Components](#components)
    - [Monitoring](#monitoring)
    - [Communication](#communication)
    - [Game logic](#game-logic)
  - [General architecture](#general-architecture)
  - [UI Control Board](#ui-control-board)
  - [MC Communication](#mc-communication)
    - [Network](#network)
    - [Protocol](#protocol)
    - [Communication format](#communication-format)
    - [Communication handling](#communication-handling)

## What is this about?
The operator room is the control center of the escape room. It's a separate room where the operator (game master) is taking place to observe the happenings in the escape room.
The operator room supports functionality to control, monitor and trace the events of the room. It also provides mechanisms to display hints to the visitors.

Another purpose of the operator room is to centralize the communication of all involved systems. It serves as a kind of server room which provides an interface for all systems to communicate with each other. It also controls the game workflow.   
## Components
The requirements of the system can be devided into three abstract components.

### Monitoring
The monitoring serves as feedback for the operator (game master) to observe the visitors. This is for ex. camaras or microphones.

***Implementation:*** The **UI control board** is implemented as a web application. It provides following features:

  1. Camera integration
  2. Game state displaying
  3. UI for state controlling (ex. reset, start, step back…)

### Communication
The communication interface allows the participated systems to exchange messages and transit a the game states (ex. if a puzzle is solved).

***Implementation:*** The communication framework and game interface consist of two modules.

  1. Centralized and standardized interface for inter mc communication (simple way to send message to other mcs)
  2. Interface for workflow feedback and state changes (ex. puzzle solved)
   
### Game logic
The game logic is an automaton which controls the game states and their transistions.

## General architecture
The following picture shows the general architecture according to the introduced three components. The diagram consists of four packages. There is a PC with in Browser in the "Operator room" and multiple cameras ("ESP cams") and micro computers (MCs) accessing the "Operator System". The "Operator System" contains the three components.

Moreover the diagramm specifies the communication protocols between the components.

![Design general system architecture](out/design/GeneralArchitecture.svg)

## UI Control Board
*"Nothing written yet"*

## MC Communication
### Network
All communication between the micro computers and the server will done over IP/TCP.
So every group gets an own IP range where they can use to connect their participants to the local network.

We are using the private ip range 10.0.0.0/16 (Subnet mask: 255.255.0.0).
To simplify the allocation of the ip addresses each group gets an ip range in **10.0.\<group-id\>.0/24**.

| Group No. | Group Name                     | IP range (from - to) |
| :-------- | :----------------------------- | :------------------- |
| 1         | Operator Room                  | 10.0.1.0-10.0.1.254  |
| 2         | Environment & AI               | 10.0.2.0-10.0.2.254  |
| 3         | Mission Briefing               | 10.0.3.0-10.0.3.254  |
| 4         | Both Doors & First Door Puzzle | 10.0.4.0-10.0.4.254  |
| 5         | Safe & Puzzles                 | 10.0.5.0-10.0.5.254  |
| 6         | Prototype & Puzzles            | 10.0.6.0-10.0.6.254  |
| 7         | Second Door Puzzles            | 10.0.7.0-10.0.7.254  |
| 8         | AI Server & Puzzles            | 10.0.8.0-10.0.8.254  |

There are two special network members:

1. The **router** is reachable under the ip address **10.0.0.1**.
It is also the default gateway of the network.
2. The **main server** is reachable unter the ip address **10.0.0.2**.

### Protocol
The supported protocol of the **main server** is **TCP**.
An connection can be established on port **1337**.
In python for example you can do this by execution the following code (more information [here](https://wiki.python.org/moin/TcpCommunication)):

```python
import socket

TCP_IP = '10.0.0.2'
TCP_PORT = 1337
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.close()
```

### Communication format
The format of the messages exchanged between the participants is **JSON**.
JSON is a very simple and compact data format to exchange data (more information [here](https://en.wikipedia.org/wiki/JSON)). 

All messages are sended over the **main server** even if the destination is an other client.
This is to log and monitor all communication centrally on the **main server** 
For all messages we defined following JSON schema: 

```javascript
{
  "src-ip": "<ip-addr>",
  "dest-ip": "<ip-addr>",
  "method": "<method>",
  "data": "<data>"
}
```

| Property | Description                                                                                                                | Example             |
| :------- | :------------------------------------------------------------------------------------------------------------------------- | :------------------ |
| src-ip   | The source IP address. This must not be set by the client. It is overriden by the server.                                  | 10.0.1.1            |
| dest-ip  | The destination IP address.                                                                                                | 10.0.2.2            |
| method   | The method indicates the purpose of the sender. For details see paragraph [Communication handling](#communication-format). | POLL, SEND, TRIGGER |
| data     | The data is the raw request of the sender. It's content is arbitary.                                                       | TURN ON main_light  |

### Communication handling
To communicate over **TCP** the client has to establish a connection to the sever.
In general the communication from client to server is unidirectional. This means only the client sends requests to the server.

We will solve this problem by **polling**. If there is a message for the client it has to fetch them by initiating a new request to the server.
The client polls periodically for received messages.

| Method Name | Description                                                                                                   |
| :---------- | :------------------------------------------------------------------------------------------------------------ |
| POLL        | Client polls for new received messages.                                                                       |
| SEND        | Client likes to send a message to another client                                                              |
| TRIGGER     | Client triggers a state change. This method allows to change the state of the game logic (ex. riddle solved). |