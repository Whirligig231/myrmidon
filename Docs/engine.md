# Setting Up the Myrmidon Engine

The Myrmidon "engine" refers to the machine code, compiled from C++, that forms the foundation of Myrmidon's software. It can be thought of as firmware in the sense that it remains on the board while different SD cards are slotted in with different software.

There are two primary ways to run the Myrmidon engine: with the desktop simulator or on an actual Myrmidon board.

## The Myrmidon Simulator

The Myrmidon simulator is located in Simulator/MyrmidonSim/. It is in the form of a Visual Studio 2019 solution for Win32. To build the project, open it in Visual Studio 2019 and select Build Solution; you may need to change some of the paths in the project settings to point to the correct locations on your drive. You will also need an installation of the [SDL2](https://www.libsdl.org/) library.

It is not necessary to build the project from source in order to use the simulator unless you are making modifications to it, as a binary is also included. This binary is located at Simulator/MyrmidonSim/Release/MyrmidonSim.exe. In order to run the binary, you must ensure that SDL2.dll is located in the same directory as the executable. You must also place the intended SD card files (the .bin files) in the same directory as MyrmidonSim.exe. Then, launching the executable should display the game in a new window. Use WASD for the directional buttons; keys K, L, J, and I are the buttons A, B, C, and D, respectively.

Although the binary is Win32-only, it has been tested and works in at least one version of WINE on macOS. Linux WINE is currently untested. The simulator also currently only uses cross-platform code (including the library SDL2), so you should be able to build it on other operating systems with no or minimal changes. The source code is written in C++11 and is located in Simulator/MyrmidonSim/MyrmidonSim/.

Some things to consider when using the simulator include:

- The simulation is displayed at an upscaled resolution of 768x512, or 8x resolution. This is so that it is easy to see what is happening on the screen. You must therefore use a large enough display for this window. (Most consumer displays these days are 1920x1080.)
- The simulation must be closed by clicking the X on the additional console window that opens behind the main window; clicking the X on the main window currently does nothing.
- The simulation will appear jittery at some frame rates because your monitor probably has a 60 Hz refresh rate. There is no Vsync feature, so some frames will take longer to appear onscreen than others. Your game will use the same loop for game logic as for rendering, so you should be able to tell whether frames are actually dropping by seeing if the physics and animations of your game are slower than normal.
- The SSD1331 panel uses a different color profile from a consumer LCD monitor, and the exact color reproduction will also depend on user settings such as color calibration and gamma. As such, the colors in the simulator are not 100% accurate to those on the OLED screen. You should check your game (or have someone else check your game) on a physical Myrmidon to make sure the colors are correct.
- Timing is not accurately simulated in the simulator, i.e. your game may run slower on a physical Myrmidon compared to the simulator. It is thus crucial to check a physical board to make sure your code is not too slow!

## Setting Up the Myrmidon Engine on a Physical Board

If you're using a "physical Myrmidon," i.e. an actual ESP8266-powered system, you need to program the board with the engine code in order to use it. Follow these steps:

1. Make sure you have the [Arduino IDE](https://www.arduino.cc/en/main/software) downloaded and installed.
2. In the Arduino IDE, go to File -> Preferences and note the "Additional Boards Manager URLs" field. Paste the URL http://arduino.esp8266.com/stable/package_esp8266com_index.json into it. Save your preferences.
3. Go to Tools -> Board -> Boards Manager... and type "esp8266" into the search field. Press ENTER; it should display an entry called "esp8266" by "ESP8266 Community." Click Install.
4. Select the following options:
	- Tools -> Board -> NodeMCU 1.0 (ESP-12E Module)
	- Tools -> Flash Size -> 4MB (FS:3MB OTA:~512KB)
	- Tools -> CPU Frequency -> 160 MHz
	- Tools -> Upload Speed -> 921600
5. Connect the ESP8266-12E to the PC using a micro USB cable.
6. Download and run either the [32-bit](https://github.com/nodemcu/nodemcu-flasher/tree/master/Win32/Release) or [64-bit](https://github.com/nodemcu/nodemcu-flasher/tree/master/Win64/Release) flashing utility. This will flash the board with the firmware required to program it.
7. Go back to the Arduino IDE and load Engine/myrmidon/myrmidon.ino.
8. With the ESP8266-12E still plugged in via USB, open the Tools -> Port submenu and select whichever serial port is showing as having a device connected. My version of the IDE doesn't display any information about the device, only that the port is available for programming. You can check the flasher used in step 6, as it tells you which port it is using. If you're really not sure, select Tools -> Get Board Info. If the VID is 10c4 and the PID is ea60, the device is definitely using a CP2102/CP2109 UART bridge controller, which is the chip the ESP8266-12E board uses, so it's almost certainly the correct board.
9. Select Sketch -> Upload (Ctrl+U). If all goes well, it should complete the upload.

In order to run Myrmidon, you'll also need a game on an SD card. Take an SD card and connect to it with your PC. Be sure that it's formatted with FAT32, and then put the .bin files for a game (for example, Games/FlappyBall/) into its *root* directory. Then eject the card and plug it into the Myrmidon, and power it up. If your installation and wiring are correct, you might see the Myrmidon logo on the screen for one second. If so, then congratulations, your Myrmidon should be ready to go!

If you don't see the Myrmidon logo, check the following:

- If the blue LED on the ESP8266-12E is blinking about once every 1.5 seconds, this means it can't read from the SD card. Be sure you have an SD card inserted with a game installed on it, and make sure that your SD card module is wired correctly.
- If the blue LED pulses for a second or so, stays off for a second, and then stays on, the device is running the game. If you don't see anything on the screen, then first, try powering the Myrmidon off and on. If there is still no image, try pressing the RST button on the ESP8266-12E to reset the microcontroller and the screen. If there is still no image, check that the SSD1331 display is wired correctly.