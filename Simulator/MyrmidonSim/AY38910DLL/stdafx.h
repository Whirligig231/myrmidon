// stdafx.h : include file for standard system include files,
// or project specific include files that are used frequently, but
// are changed infrequently
//

#pragma once

#include "targetver.h"

#define WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers
// Windows Header Files
#include <windows.h>

extern "C" __declspec(dllexport) void init();
extern "C" __declspec(dllexport) void resetToneSettings();
extern "C" __declspec(dllexport) void loadCommandBuffer(void *buffer);
extern "C" __declspec(dllexport) void startPattern(int pattern);
extern "C" __declspec(dllexport) void stopPlayback();
extern "C" __declspec(dllexport) int getTickPosition();