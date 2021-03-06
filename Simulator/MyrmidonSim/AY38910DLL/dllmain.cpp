// dllmain.cpp : Defines the entry point for the DLL application.
#include "stdafx.h"

#include <iostream>
#include <cmath>
#include <cstdlib>

#include <SDL.h>
#undef main

#define SAMPLE_RATE 44100
#define BUFFER_LENGTH 128

#pragma pack(push, 1)
struct AY38910Registers {
	uint16_t periods[3];
	uint8_t noisePeriod;
	uint8_t mixer;
	uint8_t amplitudes[3];
	uint16_t envelopePeriod;
	uint8_t envelopeType;
};
#pragma pack(pop)

AY38910Registers r;

void setRegister(uint8_t address, uint8_t value) {
	((uint8_t*)&r)[address] = value;
}

// Credits to AlanFromJapan for this array
int midiToPeriod[] = {//MIDI note number
  15289, 14431, 13621, 12856, 12135, 11454, 10811, 10204,//0-7
  9631, 9091, 8581, 8099, 7645, 7215, 6810, 6428,//8-15
  6067, 5727, 5405, 5102, 4816, 4545, 4290, 4050,//16-23
  3822, 3608, 3405, 3214, 3034, 2863, 2703, 2551,//24-31
  2408, 2273, 2145, 2025, 1911, 1804, 1703, 1607,//32-39
  1517, 1432, 1351, 1276, 1204, 1136, 1073, 1012,//40-47
  956, 902, 851, 804, 758, 716, 676, 638,//48-55
  602, 568, 536, 506, 478, 451, 426, 402,//56-63
  379, 358, 338, 319, 301, 284, 268, 253,//64-71
  239, 225, 213, 201, 190, 179, 169, 159,//72-79
  150, 142, 134, 127, 119, 113, 106, 100,//80-87
  95, 89, 84, 80, 75, 71, 67, 63,//88-95
  60, 56, 53, 50, 47, 45, 42, 40,//96-103
  38, 36, 34, 32, 30, 28, 27, 25,//104-111
  24, 22, 21, 20, 19, 18, 17, 16,//112-119
  15, 14, 13, 13, 12, 11, 11, 10,//120-127
  0//off
};

bool squares[3] = { false, false, false };
int squareClocks[3] = { 0, 0, 0 };
bool noise = false;
int noiseClock = 0;
float envelope = 0.0f;
int envelopeDir = 0;
int envelopeClock = 0;

float emas = 0.0f;

double soundClockMicros = 0.0;
void processSound();

void computeAudio(void *userdata, uint8_t* stream, int len) {
	int lenF = len / 4;
	float* streamF = (float*)(stream);
	for (int i = 0; i < lenF; i++) {
		int diffClocks = (int)((1.0f / SAMPLE_RATE) * 2000000.0f);

		soundClockMicros += (1000000.0 / SAMPLE_RATE);
		processSound();

		// Advance square wave generators
		for (int j = 0; j < 3; j++) {
			squareClocks[j] += diffClocks;
			r.periods[j] = r.periods[j] & 4095;
			if (r.periods[j] == 0) {
				squareClocks[j] = 0;
				squares[j] = true;
			}
			else {
				while (squareClocks[j] >= r.periods[j] * 8) {
					squareClocks[j] -= r.periods[j] * 8;
					squares[j] = !squares[j];
				}
			}
		}

		// Advance noise generator
		noiseClock += diffClocks;
		r.noisePeriod = r.noisePeriod & 31;
		if (r.noisePeriod == 0) {
			noiseClock = 0;
			noise = true;
		}
		else {
			while (noiseClock >= r.noisePeriod * 16) {
				noiseClock -= r.noisePeriod * 16;
				noise = rand() & 1;
			}
		}

		// Advance envelope generator
		// TODO: When does the first period of the envelope start?
		envelopeClock += diffClocks;
		r.envelopePeriod = r.envelopePeriod & 4095;
		if (r.envelopePeriod == 0) {
			envelopeClock = 0;
			envelope = 1.0f;
		}
		else {
			while (envelopeClock >= r.envelopePeriod * 256) {
				envelopeClock -= r.envelopePeriod * 256;
				r.envelopeType = r.envelopeType & 15;

				if (r.envelopeType == 10 || r.envelopeType == 14)
					envelopeDir = (envelopeDir == 1) ? -1 : 1;
				else if (r.envelopeType == 8)
					envelopeDir = -1;
				else if (r.envelopeType == 12)
					envelopeDir = 1;
				else if (r.envelopeType < 8 || r.envelopeType == 9 || r.envelopeType == 15)
					envelopeDir = 0;
				else
					envelopeDir = 2;
			}

			float envelopeFrac = (float)envelopeClock / (r.envelopePeriod * 256);

			switch (envelopeDir) {
			case 1:
				envelope = envelopeFrac;
				break;
			case -1:
				envelope = 1.0f - envelopeFrac;
				break;
			case 2:
				envelope = 1.0f;
				break;
			default:
				envelope = 0.0f;
				break;
			}
		}

		// Compute each channel signal
		float channels[3];
		for (int j = 0; j < 3; j++) {
			// Tone enabled? Noise enabled? Neither?
			if ((r.mixer & (1 << j)) == 0) {
				channels[j] = squares[j] ? 1.0f : 0.0f;
			}
			else if ((r.mixer & (1 << (3 + j))) == 0) {
				channels[j] = noise ? 1.0f : 0.0f;
			}
			else {
				channels[j] = 1.0f;
			}

			// Multiply by amplitude (or envelope)
			if ((r.amplitudes[j] & 16) != 0) {
				channels[j] *= envelope;
			}
			else {
				channels[j] *= (float)(r.amplitudes[j] & 15) / 15.0f;
			}
		}

		// Mix!
		float value = (channels[0] + channels[1] + channels[2]) / 3.0f;
		emas = 0.01f * value + 0.99f * emas;
		streamF[i] = value - emas;
	}
}

uint8_t instructions[4096] = {
	0, 0x01, 128,
	0, 0x10, 68,
	9, 0x10, 72,
	9, 0x10, 75,
	9, 0x10, 80,
	27, 0x00, 0
};

uint8_t* patterns[256];
uint8_t* instructionPointer = instructions;

bool playheadEnabled = true;
uint8_t tickTime = 1;
uint16_t ticksToNext = 0;
uint8_t* patternStack[8];
uint8_t patternStackSize = 0;
uint32_t totalTicks[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };

uint16_t startPeriod[3][4] = { {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0} };
uint16_t targetPeriod[3][4] = { {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0} };
uint8_t chordSize[3] = { 1, 1, 1 };
uint8_t chordLength[3] = { 1, 1, 1 };
uint8_t chordTicks[3] = { 0, 0, 0 };
uint8_t pitchTicks[3] = { 0, 0, 0 };
uint8_t volumeMode[3] = { 3, 3, 3 }; // 0 = attack, 1 = decay, 2 = sustain, 3 = release
uint8_t volumeTicks[3] = { 0, 0, 0 };
uint8_t maxAmplitude[3] = { 127, 127, 127 };
uint8_t attack[3] = { 0, 0, 0 };
uint8_t decay[3] = { 0, 0, 0 };
uint8_t sustain[3] = { 255, 255, 255 };
uint8_t release[3] = { 0, 0, 0 };
uint8_t pitchSlide[3] = { 0, 0, 0 };

uint16_t startPeriodBass[4] = { 0, 0, 0, 0 };
uint16_t targetPeriodBass[4] = { 0, 0, 0, 0 };
uint8_t chordSizeBass = 1;
uint8_t chordLengthBass = 1;
uint8_t chordTicksBass = 0;
uint8_t pitchTicksBass = 0;
uint8_t bassRunning = 0;
uint8_t pitchSlideBass = 0;
uint8_t bassWaveform = 10;

uint8_t drumTimer = 255;
uint8_t drumType = 0; // 0 = kick, 1 = snare, 2 = closed hat, 3 = half hat, 4 = open hat, 5 = crash

void processSound() {
	if (!playheadEnabled)
		return;
	while (soundClockMicros > (uint32_t)(tickTime) * 100) {
		soundClockMicros -= (uint32_t)(tickTime) * 100;
		while (ticksToNext == 0) {
			// Process this instruction!
			if (instructionPointer == 0)
				instructionPointer = instructions;
			std::cout << std::hex << "0x" << (int)(*instructionPointer) << " 0x" << (int)(*(instructionPointer + 1)) << " 0x" << (int)(*(instructionPointer + 2)) << std::endl;
			switch (*(instructionPointer + 1)) {
			case 0x00:
				playheadEnabled = false;
				break;
			case 0x01:
				tickTime = *(instructionPointer + 2);
				if (tickTime == 0)
					tickTime = 1;
				break;
			case 0x02:
				break;
			case 0x03:
				ticksToNext = 256 * (uint16_t)(*(instructionPointer + 2));
				break;
			case 0x04:
				break;
			case 0x05:
				if (patternStackSize == 0) {
					playheadEnabled = false;
					break;
				}
				patternStackSize--;
				instructionPointer = patternStack[patternStackSize];
				break;
			case 0x06:
				patternStack[patternStackSize] = instructionPointer;
				patternStackSize++;
				totalTicks[patternStackSize] = 0;
				instructionPointer = patterns[*(instructionPointer + 2)];
				if (instructionPointer == 0) {
					instructionPointer = instructions;
					playheadEnabled = false;
				}
				break;
			case 0x07:
				totalTicks[patternStackSize] = 0;
				instructionPointer = patterns[*(instructionPointer + 2)];
				if (instructionPointer == 0) {
					instructionPointer = instructions;
					playheadEnabled = false;
				}
				break;
			case 0x10:
				if (*(instructionPointer + 2) == 128) {
					volumeMode[0] = 3;
					volumeTicks[0] = 0;
				}
				else {
					startPeriod[0][0] = midiToPeriod[*(instructionPointer + 2)];
					targetPeriod[0][0] = midiToPeriod[*(instructionPointer + 2)];
					pitchTicks[0] = 0;
					volumeMode[0] = 0;
					volumeTicks[0] = 0;
					chordSize[0] = 1;
				}
				break;
			case 0x11:
				maxAmplitude[0] = *(instructionPointer + 2);
				break;
			case 0x12:
				attack[0] = *(instructionPointer + 2);
				break;
			case 0x13:
				decay[0] = *(instructionPointer + 2);
				break;
			case 0x14:
				sustain[0] = *(instructionPointer + 2);
				break;
			case 0x15:
				release[0] = *(instructionPointer + 2);
				break;
			case 0x16:
				pitchSlide[0] = *(instructionPointer + 2);
				break;
			case 0x17:
				targetPeriod[0][chordSize[0]] = midiToPeriod[*(instructionPointer + 2)];
				if (volumeMode[0] == 0 && volumeTicks[0] == 0)
					startPeriod[0][chordSize[0]] = midiToPeriod[*(instructionPointer + 2)];
				chordSize[0]++;
				break;
			case 0x18:
				chordLength[0] = *(instructionPointer + 2);
				if (chordLength[0] == 0)
					chordLength[0] = 1;
				break;
			case 0x1a:
				if (*(instructionPointer + 2) == 128) {
					volumeMode[0] = 3;
					volumeTicks[0] = 0;
				}
				else {
					if (volumeMode[0] == 3) {
						startPeriod[0][0] = midiToPeriod[*(instructionPointer + 2)];
						targetPeriod[0][0] = midiToPeriod[*(instructionPointer + 2)];
						pitchTicks[0] = 0;
						volumeMode[0] = 0;
						volumeTicks[0] = 0;
						chordSize[0] = 1;
					}
					else {
						for (int i = 0; i < 4; i++)
							startPeriod[0][i] = targetPeriod[0][i];
						targetPeriod[0][0] = midiToPeriod[*(instructionPointer + 2)];
						pitchTicks[0] = 0;
						chordSize[0] = 1;
					}
				}
				break;
			case 0x20:
				if (*(instructionPointer + 2) == 128) {
					volumeMode[1] = 3;
					volumeTicks[1] = 0;
				}
				else {
					startPeriod[1][0] = midiToPeriod[*(instructionPointer + 2)];
					targetPeriod[1][0] = midiToPeriod[*(instructionPointer + 2)];
					pitchTicks[1] = 0;
					volumeMode[1] = 0;
					volumeTicks[1] = 0;
					chordSize[1] = 1;
				}
				break;
			case 0x21:
				maxAmplitude[1] = *(instructionPointer + 2);
				break;
			case 0x22:
				attack[1] = *(instructionPointer + 2);
				break;
			case 0x23:
				decay[1] = *(instructionPointer + 2);
				break;
			case 0x24:
				sustain[1] = *(instructionPointer + 2);
				break;
			case 0x25:
				release[1] = *(instructionPointer + 2);
				break;
			case 0x26:
				pitchSlide[1] = *(instructionPointer + 2);
				break;
			case 0x27:
				targetPeriod[1][chordSize[1]] = midiToPeriod[*(instructionPointer + 2)];
				if (volumeMode[1] == 0 && volumeTicks[1] == 0)
					startPeriod[1][chordSize[1]] = midiToPeriod[*(instructionPointer + 2)];
				chordSize[1]++;
				break;
			case 0x28:
				chordLength[1] = *(instructionPointer + 2);
				if (chordLength[1] == 0)
					chordLength[1] = 1;
				break;
			case 0x2a:
				if (*(instructionPointer + 2) == 128) {
					volumeMode[1] = 3;
					volumeTicks[1] = 0;
				}
				else {
					if (volumeMode[1] == 3) {
						startPeriod[1][0] = midiToPeriod[*(instructionPointer + 2)];
						targetPeriod[1][0] = midiToPeriod[*(instructionPointer + 2)];
						pitchTicks[1] = 0;
						volumeMode[1] = 0;
						volumeTicks[1] = 0;
						chordSize[1] = 1;
					}
					else {
						for (int i = 0; i < 4; i++)
							startPeriod[1][i] = targetPeriod[1][i];
						targetPeriod[1][0] = midiToPeriod[*(instructionPointer + 2)];
						pitchTicks[1] = 0;
						chordSize[1] = 1;
					}
				}
				break;
			case 0x30:
				if (*(instructionPointer + 2) == 128) {
					volumeMode[2] = 3;
					volumeTicks[2] = 0;
				}
				else {
					startPeriod[2][0] = midiToPeriod[*(instructionPointer + 2)];
					targetPeriod[2][0] = midiToPeriod[*(instructionPointer + 2)];
					pitchTicks[2] = 0;
					volumeMode[2] = 0;
					volumeTicks[2] = 0;
					chordSize[2] = 1;
				}
				break;
			case 0x31:
				maxAmplitude[2] = *(instructionPointer + 2);
				break;
			case 0x32:
				attack[2] = *(instructionPointer + 2);
				break;
			case 0x33:
				decay[2] = *(instructionPointer + 2);
				break;
			case 0x34:
				sustain[2] = *(instructionPointer + 2);
				break;
			case 0x35:
				release[2] = *(instructionPointer + 2);
				break;
			case 0x36:
				pitchSlide[2] = *(instructionPointer + 2);
				break;
			case 0x37:
				targetPeriod[2][chordSize[2]] = midiToPeriod[*(instructionPointer + 2)];
				if (volumeMode[2] == 0 && volumeTicks[2] == 0)
					startPeriod[2][chordSize[2]] = midiToPeriod[*(instructionPointer + 2)];
				chordSize[2]++;
				break;
			case 0x38:
				chordLength[2] = *(instructionPointer + 2);
				if (chordLength[2] == 0)
					chordLength[2] = 1;
				break;
			case 0x3a:
				if (*(instructionPointer + 2) == 128) {
					volumeMode[2] = 3;
					volumeTicks[2] = 0;
				}
				else {
					if (volumeMode[2] == 3) {
						startPeriod[2][0] = midiToPeriod[*(instructionPointer + 2)];
						targetPeriod[2][0] = midiToPeriod[*(instructionPointer + 2)];
						pitchTicks[2] = 0;
						volumeMode[2] = 0;
						volumeTicks[2] = 0;
						chordSize[2] = 1;
					}
					else {
						for (int i = 0; i < 4; i++)
							startPeriod[2][i] = targetPeriod[2][i];
						targetPeriod[2][0] = midiToPeriod[*(instructionPointer + 2)];
						pitchTicks[2] = 0;
						chordSize[2] = 1;
					}
				}
				break;
			case 0x40:
				if (*(instructionPointer + 2) == 128) {
					bassRunning = 0;
				}
				else {
					startPeriodBass[0] = midiToPeriod[*(instructionPointer + 2) + 60];
					targetPeriodBass[0] = midiToPeriod[*(instructionPointer + 2) + 60];
					bassRunning = 1;
					pitchTicksBass = 0;
					chordSizeBass = 1;
				}
				break;
			case 0x46:
				pitchSlideBass = *(instructionPointer + 2);
				break;
			case 0x47:
				targetPeriodBass[chordSizeBass] = midiToPeriod[*(instructionPointer + 2) + 60];
				if (pitchTicksBass == 0 && startPeriodBass[0] == targetPeriodBass[0])
					startPeriodBass[chordSizeBass] = midiToPeriod[*(instructionPointer + 2) + 60];
				chordSizeBass++;
				break;
			case 0x48:
				chordLengthBass = *(instructionPointer + 2);
				if (chordLengthBass == 0)
					chordLengthBass = 1;
				break;
			case 0x49:
				if (*(instructionPointer + 2))
					bassWaveform = 12;
				else
					bassWaveform = 10;
			case 0x4a:
				if (*(instructionPointer + 2) == 128) {
					bassRunning = 0;
				}
				else {
					if (!bassRunning) {
						startPeriodBass[0] = midiToPeriod[*(instructionPointer + 2) + 60];
						targetPeriodBass[0] = midiToPeriod[*(instructionPointer + 2) + 60];
						bassRunning = 1;
						pitchTicksBass = 0;
						chordSizeBass = 1;
					}
					else {
						for (int i = 0; i < 4; i++)
							startPeriodBass[i] = targetPeriodBass[i];
						targetPeriodBass[0] = midiToPeriod[*(instructionPointer + 2) + 60];
						pitchTicksBass = 0;
						chordSizeBass = 1;
					}
				}
				break;
			case 0x50:
				drumType = *(instructionPointer + 2);
				drumTimer = 0;
			}
			instructionPointer += 3;
			ticksToNext += *instructionPointer;
			if (!playheadEnabled)
				break;
		}
		ticksToNext--;
		totalTicks[patternStackSize]++;
		if (!playheadEnabled) {
			setRegister(8, 0);
			setRegister(9, 0);
			setRegister(10, 0);
		}
		else {
			for (int i = 0; i < 3; i++) {
				// Which note in the chord is this?
				uint8_t chordIndex;
				if (chordTicks[i] >= chordLength[i] * chordSize[i])
					chordTicks[i] = 0;
				chordIndex = chordTicks[i] / chordLength[i];
				chordTicks[i]++;

				// What's the pitch of the oscillator?
				uint16_t period;
				if (pitchSlide[i] == 0)
					period = targetPeriod[i][chordIndex];
				else
					period = (startPeriod[i][chordIndex] * (pitchSlide[i] - pitchTicks[i]) + targetPeriod[i][chordIndex] * pitchTicks[i]) / pitchSlide[i];
				if (pitchTicks[i] < pitchSlide[i])
					pitchTicks[i]++;
				setRegister(2 * i, period);
				setRegister(2 * i + 1, period >> 8);

				// What's the volume?
				uint8_t volume;
				switch (volumeMode[i]) {
				case 0:
					if (attack[i] == 0)
						volume = maxAmplitude[i];
					else
						volume = (uint16_t)maxAmplitude[i] * volumeTicks[i] / attack[i];
					if (volumeTicks[i] < attack[i])
						volumeTicks[i]++;
					if (volumeTicks[i] >= attack[i]) {
						volumeTicks[i] = 0;
						volumeMode[i] = 1;
					}
					break;
				case 1:
					if (decay[i] == 0)
						volume = (uint16_t)maxAmplitude[i] * sustain[i] / 255;
					else
						volume = ((uint16_t)maxAmplitude[i] * (decay[i] - volumeTicks[i]) + ((uint16_t)maxAmplitude[i] * sustain[i] / 255) * volumeTicks[i]) / decay[i];
					if (volumeTicks[i] < decay[i])
						volumeTicks[i]++;
					if (volumeTicks[i] >= decay[i]) {
						volumeTicks[i] = 0;
						volumeMode[i] = 2;
					}
					break;
				case 2:
					volume = (uint16_t)maxAmplitude[i] * sustain[i] / 255;
					volumeTicks[i] = 0;
					break;
				default:
					if (release[i] == 0)
						volume = 0;
					else
						volume = ((uint16_t)maxAmplitude[i] * sustain[i] / 255) * (release[i] - volumeTicks[i]) / release[i];
					if (volumeTicks[i] < release[i])
						volumeTicks[i]++;
					break;
				}

				setRegister(8 + i, volume >> 4);
			}

			// Do all that stuff for bass!
			// Which note in the chord is this?
			uint8_t chordIndex;
			if (chordTicksBass >= chordLengthBass * chordSizeBass)
				chordTicksBass = 0;
			chordIndex = chordTicksBass / chordLengthBass;
			chordTicksBass++;

			// What's the pitch of the oscillator?
			uint16_t period;
			if (pitchSlideBass == 0)
				period = targetPeriodBass[chordIndex];
			else
				period = (startPeriodBass[chordIndex] * (pitchSlideBass - pitchTicksBass) + targetPeriodBass[chordIndex] * pitchTicksBass) / pitchSlideBass;
			if (pitchTicksBass < pitchSlideBass)
				pitchTicksBass++;
			setRegister(11, period);
			setRegister(12, period >> 8);

			if (bassRunning) {
				setRegister(13, bassWaveform);
				setRegister(10, 16);
			}

			if (bassRunning)
				setRegister(7, 0b11111100);
			else
				setRegister(7, 0b11111000);

			// Drums?
			if (drumTimer < 255) {
				switch (drumType) {
				case 0:
					if (drumTimer == 0) {
						setRegister(7, 0b11111000);
						setRegister(4, 0);
						setRegister(5, 4);
						setRegister(10, 15);
					}
					else if (drumTimer == 1) {
						setRegister(7, 0b11111000);
						setRegister(4, 0);
						setRegister(5, 6);
						setRegister(10, 15);
					}
					else if (drumTimer == 2) {
						setRegister(7, 0b11111000);
						setRegister(4, 0);
						setRegister(5, 8);
						setRegister(10, 15);
					}
					else if (drumTimer == 3) {
						setRegister(7, 0b11111000);
						setRegister(4, 0);
						setRegister(5, 10);
						setRegister(10, 15);
					}
					break;
				case 1:
					if (drumTimer < 4) {
						setRegister(7, 0b11011100);
						setRegister(6, 31);
						setRegister(10, 15 - drumTimer * 4);
					}
					break;
				case 2:
					if (drumTimer < 2) {
						setRegister(7, 0b11011100);
						setRegister(6, 3);
						setRegister(10, 15 - drumTimer * 8);
					}
					break;
				case 3:
					if (drumTimer < 8) {
						setRegister(7, 0b11011100);
						setRegister(6, 3);
						setRegister(10, 15 - drumTimer * 2);
					}
					break;
				case 4:
					if (drumTimer < 128) {
						setRegister(7, 0b11011100);
						setRegister(6, 3);
						setRegister(10, 15 - drumTimer / 8);
					}
					break;
				case 5:
					if (drumTimer < 128) {
						setRegister(7, 0b11011100);
						setRegister(6, 15);
						setRegister(10, 15 - drumTimer / 8);
					}
					break;
				}

				drumTimer++;
			}

		}
	}
}

SDL_AudioDeviceID dev;

void init() {
	SDL_Init(SDL_INIT_AUDIO);

	SDL_AudioSpec want, have;

	SDL_memset(&want, 0, sizeof(want)); /* or SDL_zero(want) */
	want.freq = SAMPLE_RATE;
	want.format = AUDIO_F32;
	want.channels = 1;
	want.samples = BUFFER_LENGTH;
	want.callback = computeAudio; /* you wrote this function elsewhere -- see SDL_AudioSpec for details */

	dev = SDL_OpenAudioDevice(NULL, 0, &want, &have, SDL_AUDIO_ALLOW_FORMAT_CHANGE);
	if (dev == 0) {
		SDL_Log("Failed to open audio: %s", SDL_GetError());
	}
	else {
		if (have.format != want.format) { /* we let this one thing change. */
			SDL_Log("We didn't get Float32 audio format.");
		}

		for (uint8_t *i = instructions; i + 2 < instructions + 4096; i += 3) {
			if (*(i + 1) == 0x04) {
				patterns[*(i + 2)] = i;
			}
		}

		SDL_PauseAudioDevice(dev, 0); /* start audio playing. */
	}
}

void resetToneSettings() {
	tickTime = 1;

	for (int i = 0; i < 3; i++) {
		maxAmplitude[i] = 127;
		attack[i] = 0;
		decay[i] = 0;
		sustain[i] = 255;
		release[i] = 0;
		pitchSlide[i] = 0;
	}

	pitchSlideBass = 0;
	bassWaveform = 10;
}

void loadCommandBuffer(void *buffer) {
	memcpy_s(instructions, 4096, buffer, 4096);

	for (int i = 0; i < 256; i++)
		patterns[i] = nullptr;

	for (uint8_t *i = instructions; i + 2 < instructions + 4096; i += 3) {
		if (*(i + 1) == 0x04) {
			patterns[*(i + 2)] = i;
		}
	}
}

void startPattern(int pattern) {
	instructionPointer = patterns[pattern];

	playheadEnabled = true;
	ticksToNext = 0;
	totalTicks[0] = 0;
	patternStackSize = 0;

	soundClockMicros = 0.0;

	squares[0] = false;
	squares[1] = false;
	squares[2] = false;
	squareClocks[0] = 0;
	squareClocks[1] = 0;
	squareClocks[2] = 0;
	noise = false;
	noiseClock = 0;
	envelope = 0.0f;
	envelopeDir = 0;
	envelopeClock = 0;

	for (int i = 0; i < 3; i++) {
		for (int j = 0; j < 4; j++) {
			startPeriod[i][j] = 0;
			targetPeriod[i][j] = 0;
		}

		chordSize[i] = 1;
		chordLength[i] = 1;
		chordTicks[i] = 0;
		pitchTicks[i] = 0;
		volumeMode[i] = 3;
		volumeTicks[i] = 0;
	}

	for (int j = 0; j < 4; j++) {
		startPeriodBass[j] = 0;
		targetPeriodBass[j] = 0;
	}

	chordSizeBass = 1;
	chordLengthBass = 1;
	chordTicksBass = 0;
	pitchTicksBass = 0;
	bassRunning = 0;

	drumTimer = 255;
	drumType = 0;
}

void stopPlayback() {
	playheadEnabled = false;
	totalTicks[0] = 0;

	setRegister(8, 0);
	setRegister(9, 0);
	setRegister(10, 0);
}

int getTickPosition() {
	if (!playheadEnabled)
		return 0;
	return totalTicks[0];
}

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
		break;
    case DLL_THREAD_ATTACH:
		break;
    case DLL_THREAD_DETACH:
		break;
    case DLL_PROCESS_DETACH:
		SDL_CloseAudioDevice(dev);
        break;
    }
    return TRUE;
}

