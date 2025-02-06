import colorama
import keyboard
import random
import time
import re
import os
size = 10

screen_values = ["B"]*(size**2)

def clear_screen():
    print("\033c", end="")

def generate_random_color(letter:str):
    x = ""
    color_chosen = random.choice(["r","g","b","y"])
    if color_chosen == "r":
        x = colorama.Fore.RED + letter + colorama.Fore.RESET
    elif color_chosen == "g":
        x = colorama.Fore.GREEN + letter + colorama.Fore.RESET
    elif color_chosen == "b":
        x = colorama.Fore.BLUE + letter + colorama.Fore.RESET
    elif color_chosen == "y":
        x = colorama.Fore.YELLOW + letter + colorama.Fore.RESET
    return x

def generate_colored_string(x:str):
    result = ""
    for i in x:
        result += generate_random_color(i)
    return result

def interpret_value(value, registers):
    if (match := re.search(r"GT\((.+)\)", value)):
        return int(registers[match.group(1)])
    elif (match := re.search(r"ST\((.+)\)", value)):
        return str(match.group(1))
    elif value in registers:
        return str(value)
    else:
        try:
            return int(value)
        except ValueError:
            return value


def check_break():
    if keyboard.is_pressed("alt"):
        return True
    return False

def interpret_code(code:str):
    global screen_values
    running = True

    def goto_line(x):
        global pointer
        pointer = x-2

    registers = {}
    for item in "ABCDEFabcdef":
        registers[item] = 0
    pointer = 0
    while True:
        if check_break():
            break
        rp = False
        line = code.splitlines()[pointer]
        commands = line.split(" ")
        command = commands[0]

        if command == "ADD":
            x = interpret_value(commands[1],registers)
            y = interpret_value(commands[2],registers)

            registers[x] += y
        elif command == "HALT":
            break
        elif command == "SET":
            x = interpret_value(commands[1],registers)
            y = interpret_value(commands[2],registers)

            registers[x] = y
        elif command == "SUB":
            x = interpret_value(commands[1],registers)
            y = interpret_value(commands[2],registers)

            registers[x] -= y
        elif command == "SETSC":
            x = interpret_value(commands[1],registers)
            y = interpret_value(commands[2],registers)
            z = interpret_value(commands[3],registers)
            screen_values[(size*int(y))+int(x)] = z  
        elif command == "WAIT":
            x = interpret_value(commands[1],registers)
            if check_break():
                break
            time.sleep(0.1*int(x))                  
        elif command == "DISP":
            sc = ""
            i = 0
            for y in range(size):
                for x in range(size):
                    colors = ["B","W","R"]
                    x = screen_values[i]
                    if x in colors:
                        if x == "B":
                            sc += "  "
                        elif x == "W":
                            sc += "# "
                        elif x == "R":
                            sc += colorama.Fore.RED + "# " + colorama.Fore.RESET
                    i += 1
                sc += "\n"
            clear_screen()
            print(sc)
            time.sleep(0.1)
        elif command == "GOTO":
            x = interpret_value(commands[1],registers)
            pointer = x-2
        elif command == "RP":
            pointer = 0
            rp = True
        elif command == "LINE":
            d = interpret_value(commands[1],registers)
            x = interpret_value(commands[2],registers)
            y = interpret_value(commands[3],registers)
            a = interpret_value(commands[4],registers)
            ac = interpret_value(commands[5],registers)  
            if d == 0:
                for i in range(int(a)):
                    screen_values[(size*int(y))+int(x+i)] = ac
            elif d == 1:
                for i in range(int(a)):
                    screen_values[(size*int(y+i))+int(x)] = ac
        elif command == "CLRSC":
            screen_values = ["B"]*(size**2)
        elif command == "GOTOIF":
            x = interpret_value(commands[1], registers)
            y = interpret_value(commands[2], registers)
            z = interpret_value(commands[3], registers)
            l = interpret_value(commands[4], registers)
            if z == "GR":
                if int(x) > int(y):
                    goto_line(l)
            elif z == "LS":
                if int(x) < int(y):
                    goto_line(l)
            elif z == "EQ":
                if int(x) == int(y):
                    goto_line(l)
            elif z == "GREQ":
                if int(x) >= int(y):
                    goto_line(l)
            elif z == "LSEQ":
                if int(x) <= int(y):
                    goto_line(l)              
        elif command == "CIRCLE":
            cx = interpret_value(commands[1], registers)
            cy = interpret_value(commands[2], registers)
            r = interpret_value(commands[3], registers)
            col = interpret_value(commands[4], registers)
            
            x, y = 0, r
            p = 1 - r
            
            def plot_circle_points(cx, cy, x, y, col):
                points = [
                    (cx + x, cy + y), (cx - x, cy + y),
                    (cx + x, cy - y), (cx - x, cy - y),
                    (cx + y, cy + x), (cx - y, cy + x),
                    (cx + y, cy - x), (cx - y, cy - x)
                ]
                for px, py in points:
                    if 0 <= px < size and 0 <= py < size:
                        screen_values[(size * py) + px] = col

            while x <= y:
                plot_circle_points(cx, cy, x, y, col)
                x += 1
                if p < 0:
                    p += 2 * x + 1
                else:
                    y -= 1
                    p += 2 * (x - y) + 1

        if not rp:
            pointer += 1

def Option(question: str, options: list) -> str:
    x = 0
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        print(question)
        for idx, option in enumerate(options):
            if idx == x:
                print('>', option)
            else:
                print(option)

        time.sleep(0.01)
        
        if keyboard.is_pressed('down') and not x + 1 > len(options) - 1:
            x += 1
            time.sleep(0.1)
        elif keyboard.is_pressed('up') and not x - 1 < 0:
            x -= 1
            time.sleep(0.1)
        elif keyboard.is_pressed('shift'):
            time.sleep(0.1)  # Wait briefly to avoid multiple key presses
            while keyboard.is_pressed('shift'):  # Wait until 'shift' is released
                time.sleep(0.01)
            return options[x]

def read_items():
    items = []
    with open("DCFC\\items.txt", "r") as file:
        for line in file:
            if line.startswith("NAME"):
                items.append(line.split(" ")[1].strip())
    return items

def read_name(code):
    for line in code.splitlines():
        c = line.split(" ")
        if c[0] == "NAME":
            return " ".join(c[1:])
    return "Unnamed"
def run_by_name(name:str):
    r = ""
    reading = False
    with open("DCFC\\items.txt", "r") as file:
        for line in file:
            if line.startswith("NAME") and line.split(" ")[1].strip() == name.strip():
                reading = True
            if reading and not line.startswith("[end]"):
                r += line
            if line.startswith("[end]"):
                reading = False
    return r

def save_(code):
    with open("DCFC\\items.txt", "a") as file:
        file.write("\n[new]\n" + code + "\n[end]\n")

lo = ["\\"," -","  /", "   |","    |","    |","   \\","  -", " /","|"]
m = 0
for _ in range(10*random.randint(3,10)):
    clear_screen()
    print(generate_colored_string(f"""DIGITAL
CARTRIDGE
FOR
COMPUTERS
"""))
    print(lo[m])
    print(f"0.0.7")
    time.sleep(0.1)
    
    if m + 1 < len(lo):
        m += 1
    else:
        m = 0

time.sleep(2)
while True:
    clear_screen()
    m = Option("",["Games","Insert new disk"])
    if m == "Insert new disk":
        x = input("Insert disk file (file.dsc)...")
        with open(x, "r") as file:
            print("Disk found.")
            time.sleep(1)
            code = file.read()
            p = True
            print("Running:",read_name(code))
            print(f"Saving: {read_name(code)}")
            save_(code)
            input("Press Enter to run...")
            try:
                interpret_code(code)
            except Exception as e:
                print(f":( Error occured: \nDev message: {e}")
                input('Failed > ')
                p = False
            if p:
                input("Click to continue")
    else:
        x = Option("Choose a game..",read_items())
        print(f"Running {x}")
        code = run_by_name(x)
        p = True
        print(f"Got {code}")
        try:
            interpret_code(code)
        except Exception as e:
            print(f":( Error occured: \nDev message: {e}")
            input('Failed > ')
            p = False
        if p:
            input("Click to continue")
        
