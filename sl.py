#!/usr/bin/env python3
"""
sl - A Steam Locomotive runs across your terminal with transparent background
"""

import time
import sys
import shutil

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

# Wheel patterns (動く車輪)
WHEEL_PATTERNS = [
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ",
     "  \\_/      \\O=====O=====O=====O_/      \\_/            "],
    ["__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ",
     " |/-=|___|=O=====O=====O=====O   |_____/~\\___/        ",
     "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "],
]

# Smoke patterns that change over time - extended for longer visibility
SMOKE_PATTERNS = [
    "(   )", "(    )", "(   )", "(  )", "( )", "( )", "()",
    "()", "O", "O", "O", " ", " ", " "
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
    """Draw a line of text"""
    output = ""
    for i, char in enumerate(line):
        if char != ' ':
            output += draw_char(row, col + i, char)
    return output


class Smoke:
    """Represents a smoke puff"""
    def __init__(self, y, abs_x):
        self.y = y
        self.abs_x = abs_x  # Absolute screen position
        self.pattern = 0
        self.move_counter = 0
    
    def update(self):
        self.move_counter += 1
        # Move up slowly (stay horizontally fixed on screen)
        if self.move_counter % 2 == 0:
            self.y -= 1
        self.pattern += 1
    
    def draw(self):
        if self.pattern >= len(SMOKE_PATTERNS):
            return ""
        if self.abs_x < 0:
            return ""
        pattern = SMOKE_PATTERNS[self.pattern]
        output = ""
        for i, char in enumerate(pattern):
            if char != ' ' and self.abs_x + i >= 0:
                output += draw_char(self.y, self.abs_x + i, char)
        return output


def main():
    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
    
    base_row = rows // 2 - 4
    smokes = []
    frame = 0

    try:
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.write(HIDE_CURSOR)
        sys.stdout.flush()

        x = cols - 1
        while x > -90:
            sys.stdout.write(CLEAR_SCREEN)
            output = ""
            
            # Draw locomotive
            wheel_frame = frame % 2
            for i, line in enumerate(D51_LINES):
                if x + len(line) > 0:  # Only draw if visible
                    output += draw_line(base_row + i, x, line)
            
            # Draw wheels
            for i, line in enumerate(WHEEL_PATTERNS[wheel_frame]):
                if x + len(line) > 0:
                    output += draw_line(base_row + 7 + i, x, line)
            
            # Draw coal car - align with locomotive
            if x + 53 > 0:  # Only draw if visible
                for i, line in enumerate(COAL_LINES):
                    output += draw_line(base_row + 2 + i, x + 53, line)
            
            # Add new smoke - every 2 frames to balance performance
            if frame % 2 == 0 and x >= 0:
                # Store smoke at current screen x position
                smokes.append(Smoke(base_row - 1, x + 7))
            
            # Update and draw existing smoke
            for smoke in smokes[:]:
                output += smoke.draw()
                smoke.update()
                if smoke.pattern >= len(SMOKE_PATTERNS) or smoke.y < 0:
                    smokes.remove(smoke)
            
            sys.stdout.write(output)
            sys.stdout.flush()
            
            frame += 1
            x -= 1
            time.sleep(0.04)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write(CLEAR_SCREEN)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
