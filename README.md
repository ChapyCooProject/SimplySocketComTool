Simple Socket Communication Software (Japanese Edition)
=======================================================

Development Environment
-----------------------

   * Python 3.8
   * Tkinter
   * Pyinstaller
   * Windows 11 64-bit

Introduction
------------

   * This software is a basic tool for testing TCP/IP socket communication.
   * No installation is required; it runs as a standalone executable.
   * It supports 64-bit versions of Windows. It will not run on 32-bit versions of Windows.

Startup and Exit
---------------------------------------

   * Launch the executable file "SimpleSocketCommunication.exe".
   * To exit, click "Exit" from the menu in the top-left corner of the screen.

Selecting and Starting Communication Mode
---------------------------------------------------

   * Server Mode
     1. Select "TCP Server" under "Communication Mode".
     2. Configure the following settings:
         - Port Number: The port number to listen on
         - Character Encoding: The encoding used for communication
     3. Click the "Start" button to begin listening.

   * Client Mode
     1. Select "TCP Client" under "Communication Mode".
     2. Configure the following settings:
         - IP Address: The IP address of the destination server
         - Port Number: The port number of the destination server
         - Timeout: Waiting time (in seconds) until the connection is established
         - Character Encoding: The encoding used for communication
     3. Click the "Start" button to attempt connection to the server.

How to Send Data
-------------------------------------------------------

   * Entering Data to Send
      - Enter the string you want to send in the "Send Data" input field at the top-right of the screen.
      - If sending line by line, separate each line with a newline.
      - Empty lines will not be sent.

   * Manual Sending
      - Press the "Manual Send" button to send data according to the following rules:
        - Send all text at once: Sends the entire contents of the input field at once
        - Send text line by line: Sends each line in order from the top (advances one line per button press)
      - Regardless of sending timing, received data is retrieved at specified intervals.
      - However, when control codes "ACK, NAK, ENQ, EOT, CR, LF, CRLF" are received, data is retrieved immediately.

   * Automatic Sending
      - Press the "Auto Send" button to send data line by line from the top according to the following rules:
        - Send/receive using response messages (ACK/NAK): When a response is received, the next data is sent automatically (3-second timeout)
        - Send at specified intervals: The next data is sent automatically after the specified time has elapsed

Notes on Sending Data
-----------------------------------------------

   * Newline characters entered in the "Send Data" input field are not transmitted.
     To send newline codes, include them in the message such as "\<CR\>\<LF\>".
   * When using control codes, represent them with bracketed notation.
     Supported control codes are as follows:

      - 0x00: \<NUL\>
      - 0x01: \<SOH\>
      - 0x02: \<STX\>
      - 0x03: \<ETX\>
      - 0x04: \<EOT\>
      - 0x05: \<ENQ\>
      - 0x06: \<ACK\>
      - 0x07: \<BEL\>
      - 0x08: \<BS\>
      - 0x09: \<HT\>
      - 0x0A: \<LF\>
      - 0x0B: \<VT\>
      - 0x0C: \<FF\>
      - 0x0D: \<CR\>
      - 0x0E: \<SO\>
      - 0x0F: \<SI\>
      - 0x10: \<DLE\>
      - 0x11: \<DC1\>
      - 0x12: \<DC2\>
      - 0x13: \<DC3\>
      - 0x14: \<DC4\>
      - 0x15: \<NAK\>
      - 0x16: \<SYN\>
      - 0x17: \<ETB\>
      - 0x18: \<CAN\>
      - 0x19: \<EM\>
      - 0x1A: \<SUB\>
      - 0x1B: \<ESC\>
      - 0x1C: \<FS\>
      - 0x1D: \<GS\>
      - 0x1E: \<RS\>
      - 0x1F: \<US\>
      - 0x7F: \<DEL\>

License
-----------------------------------------------
This project is licensed under the MIT License.

