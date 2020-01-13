# The M-Machine Language

## Introduction

The M-Machine language is a lightweight, assembly-like language created for the purpose of programming Myrmidon games. It was designed with two goals in mind. The primary goal is code size: with a small amount of RAM to work with, it is important that programs can be assembled into a small amount of bytecode. The secondary goal is ease of use; some assembly languages are very hard to learn due to their low-level nature, and I was trying to avoid some of this in M-Machine.

## Writing Code

M-Machine code can be written in any standard text editor. The file extension for M-Machine code is .mmc; for assembled bytecode, it is .bin. In a .mmc file, there are four types of line, separated by either Windows-style or Unix-style line endings:

- **Blank lines,** lines containing only whitespace, are ignored.
- **Comments** are lines in which the first non-whitespace character is a number sign **#**. These lines are ignored in assembly. For instance, `# This is a comment` would be a valid comment. Comments at the end of existing lines are currently not officially supported (though there's a good chance they'll work anyway under the current version of the assembler).
- **Labels** are lines in which the last non-whitespace character is a colon **:**. These lines define locations in code for the instructions *gz*, *gnz*, and *goto.*
- **Instructions** are lines that contain an instruction name and arguments. These form the body of your code and are assembled into bytecode.

Once you have written your code, you will need to use **MAssemble** to turn it into a bytecode file that Myrmidon can read and process. First, you will need a working installation of Python 3. MAssemble was written for Python 3.7, but earlier versions of Python 3 will probably still work. Then, open a command-line interface and type:

`python [path to massemble.py] [path to mmc]`

where `[path to massemble.py]` is the path to the Python script located at Utilities/massemble.py, and `[path to mmc]` is the path to your .mmc file. Note that if you have both Python 2 and Python 3 installed, some systems map `python` to Python 2 and `python3` to Python 3, in which case you should replace the former with the latter in your command.

Note that MAssemble can currently only handle a single page of instructions at once; instructions are 4 B each, so that's 1024 instructions. If you need to assemble anything longer, you should break it up into multiple .mmc files. Keep in mind that the labels defined in one .mmc will not carry over to another.

MAssemble will produce a .bin file of your code. If you're not sure what to do with it, rename it to 0001R.bin and put it either on an SD card or in the same folder as the simulator .exe. Then, Myrmidon should be able to run it.

## Memory and Storage on Myrmidon

The ESP8266 has 80 kiB of available RAM. Myrmidon uses that RAM as follows:

- 12 kiB are dedicated to the framebuffer, which is the current frame of graphics being drawn to the screen. This is manipulated using the various drawing instructions.
- A "checksums" array was planned for use in speeding up the graphics. It turned out there were issues with this approach, so the array is currently only a one-element array taking up four bytes, but in case I decide to reintroduce this system later, it could contain up to 384 B.
- 3 kiB are dedicated to the flagbuffer, a 4-bit buffer the same size as the screen used for collision detection features.
- 6 kiB are dedicated to the background, a 96x64, 256-color buffer intended for use as a background during gameplay.
- 6 kiB are dedicated to the spritesheets. There are two spritesheets, each 96x64 and 16 colors. These are where most of your game's graphics will be stored so they are ready to be drawn.
- 1 kiB is dedicated to the palette, a list of 256 colors and associated flags such as whether the color is transparent and how to count it for collision purposes.
- 2 B are used to track which colors in the palette should be used and which collision flags should be checked in collision instructions.
- 16 kiB are designated as user memory, shared between code and other data. This memory is divided into four pages of 4 kiB each.
- 512 B are used to keep track of routines and where they are located in memory.
- 33 B are used to keep track of the call stack.

The ESP8266 system itself, including the bootloader and libraries, needs about an additional 30 kiB. This leaves 5-6 kiB of remaining space, which is used for the M-Machine interpreter's internal state.

M-Machine has two principal address spaces. The first is for **registers,** which are addressed by 8 bits. The second is for **all user memory,** which is addressed by 16 bits. Each of these address types points to a **word,** which is 16 bits long. So when an address is incremented or decremented, it moves 16 bits up or down in user memory. Addresses outside of user memory have undefined behavior and may crash the system if used!

There are four pages of memory, each of 2048 words. These pages are consecutive and form one contiguous length of 8192 words. The first page thus contains addresses 0x0000 through 0x07FF; the second contains 0x0800 through 0x0FFF; the third contains 0x1000 through 0x17FF; and the fourth contains 0x1800 through 0x1FFF. Addresses higher than 0x1FFF should not be used. Addresses are represented in M-Machine code by a numerical constant, either in base 10 or in base 16 (and preceded by **0x**). While pages are consecutive, commands that move pages between RAM and ROM require page-aligned addresses, so it is helpful to remember where the page boundaries are.

The first three words in memory are special. The word at address 0x0000 is always set to 0, 0x0001 is always set to 1, and 0x0002 is always set to -1 (or 0xFFFF). Writing to these addresses will have no effect; unlike the use of invalid addresses, writing to these special addresses is supported and encouraged if you need to use an instruction without its output overwriting anything.

There are 256 registers, from @0 to @255. Each register is represented in M-Machine code by an at sign **@** followed by the numerical index of the register. The first 128 of these registers, @0 through @127, are mapped to words 0x0000 through 0x007F in memory. In particular, @0, @1, and @2 have the same special read-only behavior and constant values as the addresses 0x0000, 0x0001, and 0x0002. The first 29 registers can be referred to by the aliases 0, 1, -1, a, b, ..., x, y, and z, respectively. (So for example, g is the same as @9.)

The other 128 registers, @128 through @255, form what is called the *window.* These registers do not have a fixed position in memory. They occupy addresses 0x0080 through 0x00FF by default, but using the `window` instruction can change their position. This is because accessing memory addresses without registers mapped to them requires extra instructions, so if you need to access a specific chunk of memory frequently, it may be wise to move the window there for ease of use.

The term **"ROM"** is used in the context of Myrmidon to mean data stored on the SD card (or, in the case of the simulator, in the file system) instead of in RAM. It is, to an extent, a misnomer, as some of the pages are writeable. Each 4-kiB page in ROM is stored as a 4-digit hexadecimal index followed by either R or W and a .bin extension. An R indicates that the page is read-only, whereas W indicates that the page is writeable. There are a few other types of ROM files that can be read into the other parts of memory; see the documentation on those commands in the "Loading and Storing" section for more information.

## M-Machine Instruction Reference

Below is a comprehensive reference of every instruction used by the M-Machine language. Instructions are grouped based on their function. Each instruction consists of a name followed by zero or more **arguments.** Each argument is a register, a memory address, an **immediate** or constant numerical value, or a label (which is any identifier that does not contain a space). Note that if you want a faster reference for these commands, you can also check the M_Machine_Spec.xlsx spreadsheet.

In these instruction descriptions, `xx`, `yy`, and `zz` should be replaced by register names like `@58` or `t`, while `xxxx` or `yyyy` should be replaced by a constant or a memory address like `-53` or `0x0435`. `NAME` represents the name of a label. If an instruction includes e.g. `yy[yy]`, then `yy[yy]` can be either a register or a constant. Unless otherwise specified, every numerical value is a 16-bit integer (signedness will be specified if it matters).

In addition to a numerical constant, you can also use a parenthesized tuple of two or three numbers like `(3,54)` or `(255,255,0)` as an immediate, but you must *not* include spaces between the coordinates. This will be translated to a pixel coordinate pair or a 16-bit color, respectively; see the Graphics section for details on these formats.

### Control Flow

Several of these instructions have a special property wherein the assembler must mark the number of instructions between this instruction and the beginning or end of the correspondingly defined block. Keep this in mind if you're manually handling assembled bytecode.

- `nop`: Short for *no operation,* this instruction does nothing. It exists in case you need to pad out your code with instructions (see e.g. the `switch` instruction) without having the instruction do anything.
- `end`: Marks the end of an `if`, `while`, or `def` block. Note that in the case of `def`, you *must* `return` before the `end` instruction, unlike many languages!
- `if xx`: Begins an `if` block. Execution will skip to the corresponding `end` unless `xx` is nonzero.
- `while xx`: Begins a `while` block. If register `xx` is zero, all code until the corresponding `end` will be skipped. At the end of the block, execution will return here as long as `xx` is still nonzero.
- `else`: Place this after an `if` block and before the corresponding `end` (there should be no `end` before `else`). If the corresponding `if` test fails (i.e. its register is zero), it will skip here instead of to the `end`. If the test succeeds, on the other hand, execution will skip from the `else` to the `end`. So code between `else` and `end` will be executed precisely when code between `if` and `else` is not.
- `switch xx`: Jumps a number of instructions ahead equal to the value of `xx`. If `xx` is a signed 16-bit integer less than zero, this can be used to jump backwards. Execution will continue with the instruction *after* the one the statement points to. So `switch 0` is equivalent to `nop`, while `switch -1` will lock execution in an endless loop.
- `gz xx NAME`: Short for *goto if zero.* Jumps to a label, but only if `xx` is zero.
- `gnz xx NAME`: Short for *goto if nonzero.* Jumps to a label, but only if `xx` is nonzero.
- `def NAME`: Begins a `def` block, or *routine.* Routines are sections of code that are not executed when they are first defined; instead, you can use the `call` instruction to execute them. Note that `def` and `call` use a different label list from the other instructions that use labels, so you cannot e.g. use `goto` to call a routine defined by `def`. Note also that only 256 routines may be defined at any given time. A routine is also only defined when the `def` instruction is reached (or found using `skim`), so you cannot use `call` to call a routine that is not defined until later in the code. Lastly, note that there are no calling conventions *a priori;* i.e. there is no default mechanism for passing information between routines and the rest of the code.
- `call NAME`: Calls a routine that has been previously defined using `def`. Execution will return here after the `return` instruction. Note that the call stack is only 32 levels deep, so although recursion is possible, it should be used with extreme caution.
- `goto NAME`: Jumps to a label.
- `break`: Breaks out of a `while` block, immediately ending it and jumping to the code after its corresponding `end`. This will also break out of any `if` blocks inside the most recent `while` block. It cannot be used to break out of routines.
- `continue`: Ends the current iteration of a `while` block and jumps back to the `while` instruction. Unlike `break`, this instruction will continue the `while` loop from the beginning; thus, the `while` block will continue to be executed as long as its register is nonzero.
- `return`: Breaks out of a `def` block (i.e. routine) and returns to the place the routine was called from. This *must* be used to exit a routine; you cannot allow execution to reach the corresponding `end`!
- `reset`: Restarts the entire system. In the simulator, this exits the simulator instead.
- `print xx`: If Myrmidon is connected to a computer via USB, it will output the value of register `xx` over the serial connection at 9600 baud. If you are running the simulator, it will instead be printed to stdout. This is intended to be used strictly for debug purposes and should not be used for serious networking.

### Arithmetic

Many instructions here have signed and unsigned counterparts; the instruction without `s` at the beginning is unsigned, whereas the instruction with `s` is signed. Several instructions do not have separate signed and unsigned versions, as it does not matter. For instance, `==` works the same regardless.

For these and most other instructions, the first register is used as the output.

- `+ xx yy zz`: Sets `xx` to `yy` plus `zz`.
- `- xx yy zz`: Sets `xx` to `yy` minus `zz`. You can use `- xx 0 zz` to set `xx` to the negation of `zz`.
- `* xx yy zz`: Sets `xx` to `yy` times `zz`.
- `/ xx yy zz`: Sets `xx` to `yy` divided by `zz`, unsigned. This is integer division, i.e. the result is truncated to an integer.
- `s/ xx yy zz`: Sets `xx` to `yy` divided by `zz`, signed.
- `% xx yy zz`: Sets `xx` to `yy` mod `zz`, i.e. the remainder when `yy` is divided by `zz`. This operation is unsigned.
- `s% xx yy zz`: Sets `xx` to `yy` mod `zz`, signed.
- `frac xx yy zz`: Sets `xx` to the approximate fractional part of `yy` divided by `zz`, unsigned. In other words, `xx` will be such that `xx` divided by 65536 is approximately equal to `yy` divided by `zz`.
- `sfrac xx yy zz`: Sets `xx` to the approximate fractional part of `yy` divided by `zz`, signed. Note that here the output is still unsigned even though the inputs are signed.
- `== xx yy zz`: Sets `xx` to 1 if `yy` is equal to `zz` and 0 otherwise.
- `!= xx yy zz`: Sets `xx` to 1 if `yy` is not equal to `zz` and 0 otherwise.
- `< xx yy zz`: Sets `xx` to 1 if `yy` is less than `zz`, unsigned, and 0 otherwise. Note that there is no `>` instruction, as you can instead simply switch `yy` and `zz`.
- `s< xx yy zz`: Sets `xx` to 1 if `yy` is less than `zz`, signed, and 0 otherwise.
- `<= xx yy zz`: Sets `xx` to 1 if `yy` is less than or equal to `zz`, unsigned, and 0 otherwise. Note that there is no `>=` instruction, as you can instead simply switch `yy` and `zz`.
- `s<= xx yy zz`: Sets `xx` to 1 if `yy` is less than or equal to `zz`, signed, and 0 otherwise.
- `& xx yy zz`: Sets `xx` to the bitwise AND of `yy` and `zz`.
- `&& xx yy zz`: Sets `xx` to 1 if `yy` and `zz` are both nonzero and 0 otherwise.
- `| xx yy zz`: Sets `xx` to the bitwise OR of `yy` and `zz`. There is no `||` instruction, because `xx` will be nonzero in this instruction precisely if `yy` or `zz` is nonzero. If you really need a boolean OR, you can use this instruction and then `!= xx xx 0` afterwards.
- `^ xx yy zz`: Sets `xx` to the bitwise XOR of `yy` and `zz`.
- `<< xx yy zz`: Sets `xx` to `yy` but shifted left `zz` times. Here all arguments are unsigned.
- `>> xx yy zz`: Sets `xx` to `yy` but shifted right `zz` times. Here all arguments are unsigned.
- `? xx yy zz`: Sets `xx` to `zz`, but only if `yy` is zero. You can use this along with `=` (see the next section) to mimic the behavior of the `?:` ternary operator in other languages.
- `absgn xx yy zz`: Sets `xx` to the absolute value of `zz` and `yy` to its signum. If `zz` is positive, `xx` will be equal to `zz`, and `yy` will be 1. If `zz` is negative, `xx` will be the negation of `zz`, and `yy` will be -1. If `zz` is 0, `xx` and `yy` will both be 0.
- `sqrt xx yy zz`: Sets `xx` and `yy` to the square root of `zz`, unsigned. Here `xx` is the square root rounded down, while `yy` is the fractional part in the same manner as `frac`, i.e. as a "per 65536."
- `red xx yy zz`: Sets `xx` to `yy` with the red component changed to `zz`. Here `zz` is on a scale of 0 to 255. See the Graphics section for more on colors.
- `green xx yy zz`: Sets `xx` to `yy` with the green component changed to `zz`.
- `blue xx yy zz`: Sets `xx` to `yy` with the blue component changed to `zz`.
- `+c xx yy zz`: Sets `xx` to the carry when `yy` is added to `zz`, unsigned. This can be used to detect overflow or to perform more precise arithmetic.
- `-c xx yy zz`: Sets `xx` to the carry when `zz` is subtracted from `yy`. Here `yy` and `zz` are unsigned, but `xx` is signed.
- `*c xx yy zz`: Sets `xx` to the carry when `yy` is multiplied by `zz`, unsigned.
- `conc xx yy zz`: Sets `xx` to the low 8 bits of `yy` followed by the low 8 bits of `zz`.
- `high xx yy`: Sets `xx` to the high 8 bits of `yy`. There is no `low`; use `conc xx 00 yy` instead.

### Loading and Storing

These instructions deal with moving data between different sections of RAM and between RAM and ROM. As a reminder, pointers in these instructions are to words, where a word is two bytes. Valid addresses in user memory range between 0x0000 and 0x1FFF. There is no memory protection or other distinction between code and data; self-modifying code is thus possible, which conversely means that one must be careful to keep track of which addresses contain code.

Note that there is a latency associated with reading from or writing to ROM. While it is no more than a few frames in practice, it is noticeable, so you should not do it in the middle of intense gameplay.

- `= xx yy[yy]`: Sets `xx` to `yy[yy]`. This is what you will use most often to load constant values into registers.
- `load xx yy[yy]`: Sets `xx` to the value in memory at address `yy[yy]`.
- `store xx yy[yy]`: Sets the word in memory at address `yy[yy]` to `xx`.
- `window xx[xx]`: Moves the window to address `xx[xx]`. This will set register 128 to point to the same location as address `xx[xx]`, with registers 129-255 proceeding consecutively. Note that `xx[xx]` should not be greater than 0x1F80, or else some of the addresses in the window will be invalid!
- `skip xx[xx]`: Moves execution to address `xx[xx]`. Note that this *actually* moves the instruction pointer to word `xx[xx]` - 1, so that when the instruction pointer is incremented afterwards, execution will actually start at address `xx[xx]`. This will also clear the stack, so be careful doing this inside a routine!
- `skim xx[xx]`: "Skims" the code starting at address `xx[xx]` through the end of the corresponding page. This does not execute any code but instead runs all `def` instructions, defining their respective routine labels. This will do so even if the `def` is inside a block like `if` or `while`; it does not perform any tests. Note that `xx[xx]` does not have to be page-aligned; if it is not, the skimming will continue until the page ends, thus skimming only part of a page.

- `read xx yy[yy]`: Reads a page of ROM into memory. This will look for a file whose name is the four-digit hexadecimal value of `xx` followed by either R or W and a .bin extension. So if `xx` is set to 18, it will look for either 0012R.bin or 0012W.bin. Data will be placed into the page starting at `yy[yy]`, which must be page-aligned.
- `write xx yy[yy]`: Writes a page of memory to "ROM." This will take the page starting at address `yy[yy]`, which must be page-aligned, and write it to the file whose name is the four-digit hexadecimal value of `xx` followed by W and a .bin extension. The file must already exist for this operation to succeed. If the file ends in an R instead of a W, this will silently fail.
- `readb xx`: Reads a background from ROM. The filename of the background is the letter B followed by the four-digit hexadecimal value of `xx` and a .bin extension. (Thus, as opposed to RAM pages, backgrounds have the letter before the numerical index.) You can run the script background_encode.py in Python 3 to create these backgrounds from PNG files; see the comments at the start of background_encode.py.
- `reads xx yy`: Reads a spritesheet from ROM. The filename of the spritesheet is the letter S followed by the four-digit hexadecimal value of `xx` and a .bin extension. The register `yy` specifies whether to read the file into spritesheet 0 or spritesheet 1. You can run the script spritesheet_encode.py in Python 3 to create these spritesheets from PNG files; see the comments at the start of spritesheet_encode.py.
- `readp xx`: Reads a palette from ROM. The filename of the palette is the letter P followed by the four-digit hexadecimal value of `xx` and a .bin extension. You must generate palette files manually using a hexadecimal editor; they should be 1 kiB long and contain 256 colors, each 4 bytes long. See the documentation on `setp` for information on how colors work.
- `rex xx`: Reads a page from ROM, indexed by `xx`, into the current page and executes it. This always overwrites the current page, i.e. the page this instruction is located in. This would be equivalent to a `read` followed by `skip` if not for the fact that the `read` command would overwrite the code and prevent `skip` from executing. Thus, this instruction is intended for the use case where you wish to overwrite the currently executing page and begin executing the new page.

### Graphics

Most graphics commands operate on the **framebuffer,** which is a 96x64, full color buffer representing what will be drawn on the screen during the next `refresh`. Many of these commands will also affect the **flagbuffer,** which contains four extra bits of "color" that do not affect what gets drawn. The flagbuffer can be used for pixel-perfect collision detection.

Colors are specified either by a constant 16-bit value or an 8-bit palette index. The former is used by most commands whose colors come from registers, while the latter is used by spritesheets and backgrounds.

A 16-bit color has three components in the RGB565 format. The top 5 bits represent the red component, the middle 6 bits represent the green component, and the bottom 5 bits represent the blue component. The red and blue components are thus 0 to 31, while the green component is 0 to 63. Note that register @2, which is set to -1 in signed 16-bit format, can also be used to represent the color white.

The palette has 32 bits for each color. The first two bytes are a 16-bit color as above. The next two bytes are a 16-bit field of flags representing additional information regarding the color. The lowest bit, if set, makes the color transparent, so it will not be drawn. Bits 4-7 correspond to the four bits per pixel in the flagbuffer; if set, the corresponding flags will be set when the pixel is drawn to the framebuffer.

Many of these commands also involve pixel coordinates. A pixel coordinate pair is represented by a 16-bit value, with the upper 8 bits representing the x-coordinate and the lower 8 bits representing the y-coordinate. You can use the `conc` and `high` instructions to manipulate these. Coordinates start with `(0,0)` in the top left corner and end with `(95,63)` in the bottom right; the x-axis is left-to-right, while the y-axis is top-to-bottom. Coordinates of sprites and pieces of the background refer to the position of the top left pixel, so e.g. an 8x8 sprite drawn at `(10,10)` will have its bottom right corner at `(17,17)`.

For commands that draw a portion of the background or a spritesheet to the framebuffer, negative coordinates may be used if some of the portion should be off the left or top side of the screen. Negative coordinates are interpreted using two's complement notation on each byte of a 16-bit integer. If some of the portion to be drawn is offscreen, it will not be drawn (i.e. you need not worry about memory corruption).

- `refresh`: Transfers the framebuffer to the screen. The framebuffer (and flagbuffer) will remain the same afterwards. This is a time-consuming operation, taking up around 15 milliseconds on the hardware Myrmidon; thus, it should only be run once per frame.
- `clear xx`: Clears the framebuffer with a color given by register `xx`, and clears the flagbuffer to zero. This is currently the only way to clear the flags from the flagbuffer.
- `dbg [xx]`: Draws the entire background to the framebuffer. The register `xx` is optional; if specified, it gives an offset to start drawing from. The top left corner of the framebuffer will correspond to `xx` in the background; at the right and bottom sides, the background will wrap around to the top and left. If you want to use a negative offset, you should instead use offsets close to the width and height, e.g. `(95,0)` to start one pixel to the left.
- `dbg16 xx yy`: Draws a 16x16 portion of the background starting at pixel `xx` in the background to pixel `yy` in the framebuffer.
- `dbg8 xx yy`: Draws an 8x8 portion of the background starting at pixel `xx` in the background to pixel `yy` in the framebuffer.
- `dbg4 xx yy`: Draws a 4x4 portion of the background starting at pixel `xx` in the background to pixel `yy` in the framebuffer.
- `dbg xx yy zz`: Draws a portion of the background starting at pixel `xx` in the background to pixel `yy` in the framebuffer. The width and height of this portion are given by the coordinates in register `zz`.
- `dss xx`: Draws an entire spritesheet to the framebuffer. The register `xx` should be set to `(0,0)` or `0x0000` for spritesheet 0, or `(0,64)` or `0x0040` for spritesheet 1.
- `dss16 xx yy`: Draws a 16x16 portion of a spritesheet starting at pixel `xx` in the spritesheet to pixel `yy` in the framebuffer. For commands that draw portions of a spritesheet, rows 0-63 in the y-coordinate represent spritesheet 0, and rows 64-127 are spritesheet 1.
- `dss8 xx yy`: Draws an 8x8 portion of a spritesheet starting at pixel `xx` in the spritesheet to pixel `yy` in the framebuffer.
- `dss4 xx yy`: Draws a 4x4 portion of a spritesheet starting at pixel `xx` in the spritesheet to pixel `yy` in the framebuffer.
- `dss xx yy zz`: Draws a portion of a spritesheet starting at pixel `xx` in the spritesheet to pixel `yy` in the framebuffer. The width and height of this portion are given by the coordinates in register `zz`.
- `dpx xx yy`: Sets the pixel at `xx` to 16-bit color `yy`.
- `dchar xx yy zz`: Draws an ASCII character from spritesheet `xx` (0 or 1) to pixel `yy`. The character to draw is given by index `zz` (0-127). The spritesheet should contain 128 6x8 ASCII characters, in reading order, starting from the top left. See Miscellaneous/font.bin for the default font spritesheet.
- `dstr xx yy zz`: Draws a string of text. The font used is taken from spritesheet `xx`, and text is drawn starting at pixel `yy`. If text would go beyond the right edge, it will continue on a new line. The characters 0x0A (\n, newline) and 0x0D (\r, carriage return) are interpreted specially. 0x00 indicates the end of the string. The byte 0x7F will be skipped entirely, as if it is not there; this is used in case you need to add a "dummy character" to bring the next part of the string into word alignment.

- `clearp xx yy`: Fills the entire palette with color `xx` and flags given by `yy`. (Here "flags" means the latter two bytes of a 32-bit palette color.)
- `setp xx yy zz`: Sets the color at index `xx` in the palette to color `yy` with flags `zz`.
- `getp xx yy zz`: Gets the color at index `xx` in the palette, and sets `yy` to the 16-bit color and `zz` to the flags.
- `setpoffs xx[xx]`: Sets the palette offset. Any drawing commands that use the palette (but not the above palette commands!) will treat index `xx[xx]` as the first index in the palette. This makes it easy to store multiple sets of colors in the same palette and switch between them quickly when drawing different objects.

### Timing

- `frame [xx]`: Waits for the end of the current frame. The length of a frame is 33 ms if `xx` is unspecified and is equal to `xx` otherwise. This will wait until the last two (decimal) digits of the millisecond timer are a multiple of the frame length. So in the case of 33 ms, this technically means that both 99 and 00 are valid, meaning that a frame could last one millisecond between these two. This is not a great concern as long as the `refresh` command is used, as that will certainly take more than one millisecond, but otherwise care should be taken to ensure that every frame is at least two milliseconds long. Use `xx` = 50 for 20 FPS, 40 for 25 FPS, 33 for 30 FPS, 25 for 40 FPS, and 20 for 50 FPS. (Note that an entire frame will be dropped if your code is unable to keep up!)
- `delay xx[xx]`: Waits for `xx[xx]` milliseconds. Nothing else will happen during the delay.

### Input

Input is internally managed using an array of eight boolean values. To prevent bounce and other timing issues, this array is only updated every 25 milliseconds. Thus, if the user presses and releases a button within 25 milliseconds, it may be ignored. Fortunately, I've found that this is very hard to do, especially by accident.

The buttons are indexed as follows: 0, 1, 2, and 3 are up, down, left, and right, respectively. 4, 5, 6, and 7 are A, B, C, and D, which are the bottom, right, left, and top buttons on the right-hand side, respectively.

- `button xx yy[yy]`: Sets `xx` to 1 if the button indexed by `yy[yy]` is being held down at the moment and 0 otherwise.
- `buttonp xx yy[yy]`: Sets `xx` to 1 if the button indexed by `yy[yy]` was pressed since the previous poll and 0 otherwise.
- `buttonr xx yy[yy]`: Sets `xx` to 1 if the button indexed by `yy[yy]` was released since the previous poll and 0 otherwise.

### Collision

See Graphics for a description of how the flagbuffer is written. These commands use a notion called the **test flags,** which are stored separately in the Myrmidon's memory and contain information on which flags to test for. There are four collision flags, each represented with a different bit.

- `colflags xx[xx]`: Set the test flags to `xx[xx]`. The bottom four bits of `xx[xx]` represent whether to test for each of the four flags. So a value of 3 will test for the bottom two flags.
- `col xx`: Sets `xx` to 1 if any pixel in the flagbuffer has all of the test flags and 0 otherwise.
- `col16 xx yy`: Sets `xx` to 1 if any pixel in a 16x16 portion starting at pixel `yy` has all of the test flags and 0 otherwise.
- `col8 xx yy`: Sets `xx` to 1 if any pixel in an 8x8 portion starting at pixel `yy` has all of the test flags and 0 otherwise.
- `col4 xx yy`: Sets `xx` to 1 if any pixel in a 4x4 portion starting at pixel `yy` has all of the test flags and 0 otherwise.
- `col xx yy zz`: Sets `xx` to 1 if any pixel in a portion of the flagbuffer starting at pixel `yy` has all of the test flags and 0 otherwise. The coordinates in `zz` specify the width and height.

### String Processing

- `itoa xx yy[yy]`: Converts the unsigned 16-bit integer `xx` to a string. This string will be placed into memory at address `yy[yy]`. At least four words of space should be available at `yy[yy]` to hold the resulting string.
- `sitoa xx yy[yy]`: Converts the signed 16-bit integer `xx` to a string. This string will be placed into memory at address `yy[yy]`. At least four words of space should be available at `yy[yy]` to hold the resulting string.
- `strw xx yy`: Calculates the width of the string found at pointer `yy` and stores it in `xx`. This is the width required to draw the string, in pixels, if there were no wrapping behavior.
- `strh xx yy`: Calculates the height of the string found at pointer `yy` and stores it in `xx`. This is the height required to draw the string, in pixels, if there were no wrapping behavior.

### Miscellaneous

- `random xx yy[yy]`: Generates a random integer from 0 to `yy[yy]` - 1, inclusive, and stores it in `xx`. This should *not* be used for cryptographic purposes, as the random integers generated in this manner are not secure and may not be perfectly uniformly distributed either.