# Myrmidon

**Note: a lot has changed in the most recent commit / update. Please stand by, and the documentation will be updated shortly.**

## Introduction

Myrmidon is a handheld gaming system built on the ESP8266 SOC. The current version is based on the NodeMCU board to make it easy to prototype. The goal of the project is to create an architecture that enables the system to load games off of SD cards and play them using an 8-button controller and a 96x64, 16-bit OLED display. A DIY system like this offers several advantages over a traditional handheld gaming device:

- **Cost:** The total hardware cost for a Myrmidon system is around 50 USD. Even a refurbished mainstream handheld from a few generations back will cost 60 USD or more.
- **Accessibility:** Myrmidon's software is open source, and its hardware is readily available with no "special sauce" or proprietary components. Even the game cartridges are simply standard SD cards. This means that you don't need any special license or expertise to develop for it; all you need is documentation and coding skill. In addition, if you have any special needs or ideas, it is easy to modify the circuitry yourself.
- **Sustainability:** Related to the above, Myrmidon's open nature means that people can never stop developing for the system and iterating on its design. If in the future some component becomes outdated and needs to be replaced or emulated, there won't be any reverse engineering, just engineering.
- **Fun:** Of course, the reason I made Myrmidon is none of these. It's simply that I, like many, am a hobby electronics enthusiast who thought it would be a fun challenge. Perhaps building a Myrmidon could be your next project!

## Getting Started

The easiest way to get started with Myrmidon is to run the included simulator in Simulator/MyrmidonSim/Release/. It should load the FlappyBall example game. Then you can look through the other directories (in particular, the Docs directory) to see how to write your own games for the system. After you've tinkered around enough in the simulator, you can then order the parts to build your own Myrmidon, if you want. Recommendations for parts can be found in Docs/Hardware.md.

## Documentation

The rest of the documentation is found in the Docs/ directory. It contains the following documentation files:

- Docs/hardware.md: Contains a list of components required to build a Myrmidon, along with recommendations on where to buy them and how to wire them together.
- Docs/engine.md: Contains instructions on how to set up the engine software and upload it to the ESP8266.
- Docs/m_machine.md: Contains information on how to use the M-Machine language and program games in it.

## Acknowledgements

Myrmidon is the intellectual property of Whirligig Studios / Whirligig231 and is available under the terms of the GPL v3. It uses the SSD_13XX library by sumotoy, available [here.](https://github.com/sumotoy/SSD_13XX)