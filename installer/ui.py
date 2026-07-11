import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep
import keyword

import tty
import termios

# unicode icons
IOK         = "\u2714"
IFAIL       = "\u2718"
IPOST_ARROW = "\U0001F836"
IRETURN     = "\u23ce"
IUP         = "\u25b2"
IDOWN       = "\u25bc"

# styles
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

# colors
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
BLACK   = "\033[30m"

# background
BRED     = "\033[41m"
BGREEN   = "\033[42m"
BYELLOW  = "\033[43m"
BBLUE    = "\033[44m"
BMAGENTA = "\033[45m"
BCYAN    = "\033[46m"
BWHITE   = "\033[47m"

def select(title:str, options, currentIndex=0) -> int:
    hide_cursor()
    
    # stdin id
    fileno = sys.stdin.fileno()
    
    old_buffer = termios.tcgetattr(fileno)
    tty.setraw(fileno)
    menu_size = len(options) + 2 if title else len(options)

    while True:
        if title: sys.stdout.write(f"\r\n{title}\n")

        for i, option in enumerate(options):
            big_boy = max(options, key=len)
            opt_str = " " + option.ljust(len(big_boy)+1).capitalize()
            
            if i == currentIndex:
                sys.stdout.write(f"\r\033[K {BCYAN}{BLACK}{BOLD}{opt_str}{RESET}\n")
            else: sys.stdout.write(f"\r\033[K {DIM}{opt_str}{RESET}\n")
        
        sys.stdout.flush()
        key = sys.stdin.read(1)

        if key in ('\n', '\r'):
            break

        if key == '\x03':
            termios.tcsetattr(fileno, termios.TCSADRAIN, old_buffer)
            show_cursor()
            print()
            sys.exit(0)

        if key == '\x1b':
            direction = sys.stdin.read(2)
            
            if direction == "[A" and currentIndex > 0:
                currentIndex -= 1 

            if direction == "[B" and currentIndex < len(options) - 1:
                currentIndex += 1

        sys.stdout.write(f"\r\033[{menu_size}A")
    
    termios.tcsetattr(fileno, termios.TCSADRAIN, old_buffer)
    show_cursor()
    print()
    return currentIndex

# just a spinner
def spinner(label, target, *args, **kargs):
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    chars=["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    with ThreadPoolExecutor() as t:
        thread = t.submit(target, *args, **kargs)

        i = 0
        
        while thread.running():
            i+= 1
            sys.stdout.write(f"\r{CYAN}{chars[i % len(chars)]}{RESET} {BOLD}{label}{RESET}\r")
            sys.stdout.flush()
            sleep(0.033)

    try: 
        result = thread.result()
        sys.stdout.write(f"{GREEN}{IOK}{RESET} {DIM}{label}{RESET}\n")
        return result
    except Exception as e:
        sys.stdout.write(f"{RED}{IFAIL}{RESET} {DIM}{label}{RESET}\n")            
        print(e)

        return []
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def hide_cursor():    
    sys.stdout.write("\033[?25l")

def show_cursor():    
    sys.stdout.write("\033[?25h")