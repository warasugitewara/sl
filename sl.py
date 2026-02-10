#!/usr/bin/env python3
"""
sl - A Steam Locomotive runs across your terminal with transparent background
Based on mtoyoda/sl (https://github.com/mtoyoda/sl)
Python implementation with Wezterm transparent background support
"""

import time
import sys
import shutil
import argparse

# D51 locomotive parts
D51_LINES = [
    "      ====        ________                ___________ ",
    "  _D _|  |_______/        \\__I_I_____===__|_________| ",
    "   |(_)---  |   H\\________/ |   |        =|___ ___|   ",
    "   /     |  |   H  |  |     |   |         ||_| |_||   ",
    "  |      |  |   H  |__--------------------| [___] |   ",
    "  | ________|___H__/__|_____/[][]~\\_______|       |   ",
    "  |/ |   |-----------I_____I [][] []  D   |=======|__ ",
]

# Coal car (荷台) - with wheels
COAL_LINES = [
    "    _________________         ",
    "   _|                \\_____A  ",
    " =|                        |  ",
    " -|                        |  ",
    "__|________________________|_ ",
    "|__________________________|_ ",
    "   |_D__D__D_|  |_D__D__D_|   ",
    "    \\_/   \\_/    \\_/   \\_/    ",
]

# Wheel patterns (動く車輪) - 6 patterns to match original sl.c
WHEEL_PATTERNS = [
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ",
     "  \\_/      \\O=====O=====O=====O=====O_/      \\_/            "],
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|= O=====O=====O===== O  |_____/~\\___/        ",
     "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "],
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|=O  O  O  O  O       |_____/~\\___/        ",
     "  \\_/      \\O=====O=====O=====O_/      \\_/            "],
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ",
     "  \\_/      \\ O=====O=====O=====O /      \\_/            "],
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|= O=====O=====O===== O  |_____/~\\___/        ",
     "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "],
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|=O=====O=====O=====O   |_____/~\\___/        ",
     "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "],
]

# Smoke patterns (16 stages) - matches original sl.c
SMOKE_PATTERNS = [
    "(   )", "(    )", "(    )", "(   )", "(  )",
    "(  )", "( )", "( )", "()", "()",
    "O", "O", "O", "O", "O", " "
]

# Smoke movement patterns (dy, dx for each stage)
SMOKE_DY = [2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
SMOKE_DX = [-2, -1, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3]

# Smoke eraser patterns (same width as smoke for clearing)
SMOKE_ERASER = [
    "     ", "      ", "      ", "     ", "    ",
    "    ", "   ", "   ", "  ", "  ",
    " ", " ", " ", " ", " ", " "
]

# ANSI codes
ESC = "\033"
CLEAR_SCREEN = ESC + "[2J" + ESC + "[H"
HIDE_CURSOR = ESC + "[?25l"
SHOW_CURSOR = ESC + "[?25h"
WHITE = ESC + "[37m"
RESET = ESC + "[0m"


def move_cursor(row, col):
    return ESC + "[" + str(row) + ";" + str(col) + "H"


def draw_char(row, col, char):
    if char != ' ' and row >= 0 and col >= 0:
        return move_cursor(row, col) + WHITE + char + RESET
    return ""


def draw_line(row, col, line):
    """Draw a line of text - returns list of ANSI commands"""
    output = []
    for i, char in enumerate(line):
        if char != ' ':
            cmd = draw_char(row, col + i, char)
            if cmd:
                output.append(cmd)
    return output


class Smoke:
    """Represents a smoke puff - matches original sl.c behavior"""
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.pattern = 0
    
    def update_and_draw(self, output_buffer):
        """Execute one update cycle: erase, move, pattern update, redraw"""
        if self.pattern >= len(SMOKE_PATTERNS):
            return
        
        # Step 1: Erase at current position
        pattern_width = len(SMOKE_ERASER[self.pattern])
        for i in range(pattern_width):
            if self.x + i >= 0:
                cmd = draw_char(self.y, self.x + i, ' ')
                if cmd:
                    output_buffer.append(cmd)
        
        # Step 2: Move smoke (apply dy/dx for current pattern)
        if self.pattern < len(SMOKE_DY):
            self.y -= SMOKE_DY[self.pattern]
            self.x += SMOKE_DX[self.pattern]
        
        # Step 3: Advance pattern
        if self.pattern < len(SMOKE_PATTERNS) - 1:
            self.pattern += 1
        
        # Step 4: Draw at new position with new pattern
        if self.pattern < len(SMOKE_PATTERNS) and self.x >= 0:
            pattern = SMOKE_PATTERNS[self.pattern]
            for i, char in enumerate(pattern):
                if char != ' ' and self.x + i >= 0:
                    cmd = draw_char(self.y, self.x + i, char)
                    if cmd:
                        output_buffer.append(cmd)
    
    def draw_initial(self, output_buffer):
        """Draw smoke at initial position (pattern 0) - only called at spawn"""
        pattern = SMOKE_PATTERNS[self.pattern]
        for i, char in enumerate(pattern):
            if char != ' ' and self.x + i >= 0:
                cmd = draw_char(self.y, self.x + i, char)
                if cmd:
                    output_buffer.append(cmd)
    
    def draw_current(self, output_buffer):
        """Draw smoke at current position with current pattern - for frames between updates"""
        if self.pattern >= len(SMOKE_PATTERNS) or self.x < 0:
            return
        pattern = SMOKE_PATTERNS[self.pattern]
        for i, char in enumerate(pattern):
            if char != ' ' and self.x + i >= 0:
                cmd = draw_char(self.y, self.x + i, char)
                if cmd:
                    output_buffer.append(cmd)


def main():
    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Steam Locomotive animation for terminal')
    parser.add_argument('-loop', nargs='?', const=-1, type=int, default=1,
                        help='Loop animation. Use -loop for infinite loop or -loop N for N times')
    args = parser.parse_args()
    
    loop_count = args.loop
    infinite_loop = loop_count == -1
    
    base_row = rows // 2 - 5
    d51_length = 63
    
    try:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.flush()
        
        current_loop = 0
        while infinite_loop or current_loop < loop_count:
            smokes = []
            x = cols - 1
            while x > -d51_length:
                sys.stdout.write(CLEAR_SCREEN)
                output_buffer = []
                
                wheel_frame = (d51_length + x) % 6
                
                # Draw locomotive
                for i, line in enumerate(D51_LINES):
                    if x + len(line) > 0:
                        output_buffer.extend(draw_line(base_row + i, x, line))
                
                # Draw wheels
                for i, line in enumerate(WHEEL_PATTERNS[wheel_frame]):
                    if x + len(line) > 0:
                        output_buffer.extend(draw_line(base_row + 7 + i, x, line))
                
                # Draw coal car
                if x + 53 > 0:
                    for i, line in enumerate(COAL_LINES):
                        output_buffer.extend(draw_line(base_row + 2 + i, x + 53, line))
                
                # Smoke system: update every 4 frames, draw every frame
                if x % 4 == 0:
                    for smoke in smokes[:]:
                        smoke.update_and_draw(output_buffer)
                        if smoke.pattern >= len(SMOKE_PATTERNS) - 1:
                            smokes.remove(smoke)
                    
                    smoke_funnel_x = x + 7
                    new_smoke = Smoke(base_row - 1, smoke_funnel_x)
                    new_smoke.draw_initial(output_buffer)
                    smokes.append(new_smoke)
                else:
                    for smoke in smokes:
                        smoke.draw_current(output_buffer)
                
                sys.stdout.write("".join(output_buffer))
                sys.stdout.flush()
                
                x -= 1
                time.sleep(0.04)
            
            current_loop += 1

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
