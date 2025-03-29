from math import sin, cos, atan2 as arctan, sqrt, copysign, degrees as deg
from numpy import float32 as f32
from typing import Literal
import re
import inspect
from collections import Counter
from pprint import pp

# XZPoss w/ z neo z.
# add miscs
# MAKE A SAFE EVAL - maybe prevent dict{} and all that
# water is at least e-14 precise, not e-17 (i think)
# fix functions
# aq and tq in optimize doesnt work
# Lava
# Web air
# Custom Defined Recursive Functions
# # This also means adding conditionals
# Fix type annotations in custom defined functions


class OverwriteError(Exception):
    pass

class Player:
    pi = 3.14159265358979323846

    _fortyfive_methods = ["walk45", "walkair45", "walkjump45", "sprint45", "sprintair45", "sprintjump45", "sneak45", "sneakair45", "sneakjump45", "sneaksprint45", "sneaksprintair45", "sneaksprintjump45", "walkwater45", "sprintwater45", "sneakwater45", "sword45", "swordair45", "swordsneak45", "swordsneakair45", "swordwater45", "swordsneakwater45", "swordjump45", "swordsneakjump45", "web45", "webair45", "sprintwebair45", "sprintweb45", "webjump45", "sprintwebjump45", "sneakweb45", "sneakwebair45", "sneaksprintweb45", "sneaksprintwebjump45", "sneaksprintwebair45", "sneakwebjump45", "snwebj45"]

    _can_have_input = ["walk", "walkair", "walkjump", "sprint", "sprintair", "sprintjump", "sneak", "sneakair", "sneakjump", "sneaksprint", "sneaksprintair", "sneaksprintjump", "walkwater", "sprintwater", "sneakwater", "lava", "sword", "swordair", "swordsneak", "swordsneakair", "swordwater", "swordsneakwater", "swordjump", "swordsneakjump", "web", "webair", "sprintweb", "sprintwebair", "webjump", "sprintwebjump", "sneakweb", "sneakwebair", "sneaksprintweb", "sneaksprintwebjump", "sneaksprintwebair", "sneakwebjump", "snwebj"]

    mm_to_dist = dist_to_block = lambda mm: (mm + copysign(f32(0.6), mm))
    dist_to_mm = block_to_dist = lambda dist: (dist - copysign(f32(0.6), dist))

    sprintjump_boost = f32(0.2)

    JUMP = "jump"
    GROUND = "ground"
    AIR = "air"
    WATER = "water"
    LAVA = "lava"

    FUNCTIONS = {}

    FUNCTIONS_BY_TYPE = {"fast-movers": [
        "sprint", "s", "sprint45", "s45", "sprintjump", "sprintjump45", "sj", "sj45", "sprintair", "sa", "sprintair45", "sa45", "sprintstrafejump", "sprintstrafejump45", "strafejump", "strafejump45", "stfj", "stfj45", "sneaksprint", "sneaksprintair", "sneaksprintjump", "sns", "snsa", "snsj", "sneaksprint45", "sneaksprintair45", "sneaksprintjump45", "sns45", "snsa45", "snsj45", "sneaksprintweb", "snsweb", "sneaksprintweb45", "snsweb45", "sneaksprintwebair", "snsweba", "sneaksprintwebair45", "snsweba45", "sneaksprintwebjump", "snswebj", "sneaksprintwebjump45", "snswebj45"
    ], "slow-movers": [
        "walk", "w", "walkair", "wa", "walkjump", "wj", "walk45", "w45", "walkair45", "wa45", "walkjump45", "wj45", "sneak", "sneak45", "sn", "sn45", "sneakair", "sneakair45", "sna", "sna45", "sneakjump", "snj", "sneakjump45", "snj45", "walkwater", "wwt", "wt", "water", "walkwater45", "wwt45", "water45", "wt45", "sprintwater", "swt", "sprintwater45", "swt45", "sneakwater", "snwt", "sneakwater45", "snwt45", "sword", "swordair", "swordsneakair", "swordsneak", "sword45", "swordair45", "swordsneakair45", "swordsneak45", "swordjump", "swordjump45", "swordwater", "swordwater45", "swordsneakwater", "swordsneakwater45", "web", "web45", "webair", "weba", "webair45", "weba45", "sweb", "sweb45", "swebair", "sweba", "swebair45","sweba45", "sprintweb", "sprintwebair", "sprintweb45", "sprintwebair45", "webjump", "webj", "webjump45", "webj45", "sprintwebjump", "swebj", "sprintwebjump45","swebj45", "sneakweb", "snweb", "snweb45", "sneakweb45", "sneakwebair", "snweba", "sneakwebair45", "snweba45", "sneakwebjump45", "snwebj45", "sneakwebjump", "snwebj"
    ], "stoppers": [
        "stop", "stopground", "st", "stopair", "sta", "stopjump", "stj", "stopwater", "stwt", "stopweb", "stweb", "stopwebair", "stweba"
    ], "returners": [
        "outz", "zmm", "zb", "outvz", "outx", "xmm", "xb", "outvx", "vec", "help", "print", "effectsmultiplier", "effects", "printdisplay", "dimensions", "dim", "outangle", "outa", "outfacing", "outf", "outturn", "outt"
    ], "calculators": [
        "bwmm", "xbwmm", "wall", "xwall", "inv", "xinv", "blocks", "xblocks", "repeat", "r", "possibilities", "poss", "xpossibilities", "xposs", "xzpossibilities", "xzposs"
    ], "setters": [
        "face", "facing", "f", "turn", "setposz", "z", "setvz", "vz", "setposx", "x", "setvx", "vx", "setslip", "slip", "setprecision", "precision", "pre", "inertia", "sprintairdelay", "sdel", "version", "v", "anglequeue", "aq", "tq", "turnqueue", "speed", "slow", "sndel", "sneakdelay", "var", "function", "func", "alias", "toggle", "singleaxisinertia", "sai"
    ]}


    def __init__(self) -> None:
        self.x = 0.0
        self.z = 0.0
        self.vx = 0.0
        self.vz = 0.0

        self.default_ground_slip = f32(0.6)
        self.current_slip = f32(0.6)
        self.previous_slip = None

        self.total_angles = 65536

        self.rotation = f32(0.0)
        self.last_rotation = f32(0.0)
        self.last_turn = f32(0.0)

        self.rotation_queue: list[tuple[str, f32]] = []

        self.air_sprint_delay = True

        self.sneak_delay = False

        self.precision = 7

        self.inertia_threshold = 0.005

        self.inertia_axis = 1

        self.inputs = ""

        self.reverse = False

        self.previously_sprinting = False

        self.previously_sneaking = False

        self.previously_blocking = False # maybe

        self.previously_in_web = False

        self.state = self.GROUND

        self.record = {}

        self.swift = 0 # This is because the function will be called speed
        self.slow = 0
        
        self.local_vars = {"px": 0.0625, "blocks": 0.6, "zneo": -0.6, "ladder":0.3, "vine":0.3}
        self.local_funcs = {}

        self.output: list[tuple[str | Literal['normal', 'z-expr', 'x-expr', 'expr']]] = []

        self.closed_vars = {} # For declaring functions only

        self.toggled = []

    @staticmethod
    def add_alias(func: object, *alias, dictionary: dict = FUNCTIONS):
        "Creates a new key, value pair whose keys are `*alias` and its value is `func`"
        for a in alias:
            dictionary[a] = func
    
    @staticmethod
    def clean_backslashes(string: str):
        "Replaces backslashes if possible. Anything with `\` followed by a char will be replaced."
        return string.replace("\,", ",").replace("\(", "(").replace("\)", ")").replace("\#", "#").replace("\{", "{").replace("\}", "}").replace("\=", "=") # i hate myself

    def safe_eval(self, expr: str, datatype: type, locals_dict: dict):
        "Evaluate and convert `expr` to `datatype`. If `datatype = str`, it returns the `expr` as normal."
        if datatype in [float, int, f32]:
            if "__" in expr:
                    raise RuntimeError(f"Rejected unsafe expression {expr}")
            
            result = eval(expr, {"__builtins__": {}}, locals_dict)
            converted_value = datatype(result) if result is not None else None
            return converted_value
        else:
            return expr

    def add_output(self, string: str):
        """
        Appends to the `Player` object's `output` attribute, used for displaying results as normal
        """
        string = Player.clean_backslashes(self.formatted(str(string)))
        self.output.append((string, "normal"))


    def add_output_with_label(self, label: str, string: str = '', expr_type: str = 'z-expr'):
        """
        Appends to the `Player` object's `output` attribute, used for displaying results in the form `label: string`

        All strings can be formatted by putting variable names inside curly brackets `{}`

        `expr_type` is either `z-expr`, `x-expr`, or just `expr`
        """
        label = Player.clean_backslashes(self.formatted(label))
        string = Player.clean_backslashes(self.formatted(str(string)))
        self.output.append((f"{label}: {string}", expr_type))
    
    def format_number(self, value: float, centered_about: float = 0, return_as_string = False):
        """
        Returns `value` as a number or an expression as a string. Automatically rounds the decimals according to the `Player` object's `precision` attribute.
        
        If `centered_about = 0`, return `value` as a string. \\
        Otherwise, return a mathematical expression as a string such that the expression evaluates to `value` by adding or subtracting from `centered_about`. Note that `centered_about` will not be rounded.

        ```py
        >> p = Player()
        >> p.format_number(3.1415926)
        "3.1415926"
        >> p.precision = 3 # now all numbers will round to 3 decimal places
        >> p.format_number(3.1415926)
        "3.142"
        >> p.format_number(3.1415926, 2.71828)
        "2.71828 + 0.423"
        >> p.format_number(1.616, 2.71828)
        "2.71828 - 1.102"
        ```
        """
        if centered_about:
            return f"{centered_about} {'-' if centered_about - value > 0 else '+'} {f'{abs(value - centered_about):.{self.precision}f}'}"

        else:
            return f"{value:.{self.precision}f}"
    
    def formatted(self, string: str):
        "Formats string just like an f-string"
        formatted_string = ""

        item_to_eval = ""
        in_expr = False
        depth = 0

        for char in string:
            if char == "{":
                in_expr = not in_expr
                if not in_expr:
                    item_to_eval = ""
                    formatted_string += char
                else:
                    item_to_eval += char
                depth += 1

            elif char == "}":
                if depth == 0:
                    raise SyntaxError("Unmatched Brackets")

                depth -= 1
                if in_expr:
                    item_to_eval += char

                    item_to_eval = item_to_eval[1:len(item_to_eval) - 1]
                    # print(f"{item_to_eval = }")
                    if item_to_eval:
                        x = eval(item_to_eval, {"__builtins__": {}}, self.local_vars)
                        x = str(x)

                    formatted_string += x
                    item_to_eval = ''
                else: 
                    formatted_string += item_to_eval + char
                    item_to_eval = ''

                in_expr = not in_expr
            elif in_expr:
                item_to_eval += char
            else:
                formatted_string += char
        
        if depth != 0:
            raise SyntaxError("Unmatched Brackets")

        return formatted_string
    
    def get_angle(self):
        "Returns the next angle from the rotation queue or if no angle is in the rotation queue, return the default facing."

        if self.rotation_queue:
            turn_type, angle = self.rotation_queue.pop(0)
            if turn_type == "angle":
                self.rotation = angle
            elif turn_type == "turn":
                self.rotation += angle
            return self.rotation
        return self.rotation

    def move(self, duration: int, rotation: f32 = None, rotation_offset: float = 0.0, slip: f32 = None, is_sprinting: bool = False, is_sneaking: bool = False, speed: int = None, slow: int = None, state: Literal["ground", "air", "jump", "water"] = "ground", is_blocking: bool = False, in_web: bool = False):
        """
        Moves the player for `duration` ticks with a slip value of `slip`.

        The player will move facing `rotation` if given, otherwise, it will use the rotation queue and/or the default rotation.

        `rotation_offset` is used if you wish to preserve the facing despite the actual angle being different, particularly useful for displaying info while 45ing (`rotation_offset = 45`) or strafe jumping (`rotation_offset = 17.4786857811690446`).

        Although there is no hard restriction, in later versions, `is_sprinting` and `is_sneaking` can be set to `True` at the same time.
        """
        sj_boost = self.sprintjump_boost
        if self.previous_slip is None:
            self.previous_slip = self.default_ground_slip

        if rotation_offset == 45:
            self.inputs = "wa"
        
        if speed is None:
            speed = self.swift
        if slow is None:
            slow = self.slow

        self.state = state

        override_rotation = False
        if (rotation is not None):
            override_rotation = True
            rotation = f32(rotation + rotation_offset)

        if not slip: # If slip is not given, assume its ground slip since air slip (0.1) is always passed into the argument
            slip = self.default_ground_slip
        
        # print(f"AT MOVE, {duration = }")

        for _ in range(duration):
            # print(f"I got here with dur {duration}")
            if not override_rotation:
                rotation = f32(self.get_angle() + rotation_offset)
            # print(f"{rotation  = }")
                
            # MOVING THE PLAYER
            self.x += self.vx
            self.z += self.vz

            forward, strafe = self.movement_values()
            # print(forward, strafe)

            if self.reverse:
                forward *= f32(-1)
                strafe *= f32(-1)
                sj_boost *= -1

            # Finalize Momentum
            self.vx *= f32(0.91) * self.previous_slip
            self.vz *= f32(0.91) * self.previous_slip

            # Apply inertia or web
            if self.inertia_axis == 1:
                if abs(self.vx) < self.inertia_threshold or self.previously_in_web:
                    self.vx = 0.0
                if abs(self.vz) < self.inertia_threshold or self.previously_in_web:
                    self.vz = 0.0
            elif self.inertia_axis == 2:
                if sqrt(self.vz**2 + self.vx**2) < self.inertia_threshold or self.previously_in_web:
                    self.vx = 0.0
                    self.vz = 0.0

            # Get Movement Multiplier M
            M = self.movement_multiplier(slip, is_sprinting, speed, slow, state)

            # Sprint jump boost
            if state == self.JUMP and is_sprinting:
                facing = f32(rotation * f32(0.017453292)) # TO CHANGE
                self.vx -= self.mcsin(facing) * sj_boost
                self.vz += self.mccos(facing) * sj_boost

            # BLOCKING
            # if ((self.state == self.AIR) and (self.previously_blocking) or (is_blocking)):
            if is_blocking:
                forward = f32(float(forward) * 0.2)
                strafe  = f32(float(strafe) * 0.2)

            # SNEAKING
            if (self.sneak_delay and self.previously_sneaking) or (not self.sneak_delay and is_sneaking):
                forward = f32(float(forward) * 0.3)
                strafe = f32(float(strafe) * 0.3)

            forward *= f32(0.98)
            strafe *= f32(0.98)

            distance = f32(strafe * strafe + forward * forward)

            # Avoid division by 0
            if distance >= f32(0.0001):

                # Normalize distance IF above 1
                distance = f32(sqrt(float(distance)))
                if distance < f32(1.0):
                    distance = f32(1.0)

                # Modifies strafe and forward to account for movement
                distance = M / distance
                forward = forward * distance
                strafe = strafe * distance

                # Adds rotated vectors to velocity
                sin_yaw = f32(self.mcsin(rotation * f32(Player.pi) / f32(180.0)))
                cos_yaw = f32(self.mccos(rotation * f32(Player.pi) / f32(180.0)))

                self.vx += float(strafe * cos_yaw - forward * sin_yaw)
                self.vz += float(forward * cos_yaw + strafe * sin_yaw)

            if in_web:
                self.vx = self.vx / 4
                self.vz = self.vz / 4
            
            
            # Prep for next tick
            self.previous_slip = slip
            self.previously_sprinting = is_sprinting
            self.previously_sneaking = is_sneaking
            self.previously_blocking = is_blocking
            self.previously_in_web = in_web
            self.last_turn = rotation - self.last_rotation
            self.last_rotation = rotation

            # Record possibilities
            self.possibilities_helper()
            
            to_remove = []
            for f in range(len(self.toggled)):
                g = self.toggled[f]
                ticks = g[0]
                func = g[1]
                self.simulate(func, return_defaults=False, locals=self.local_vars)
                g[0] -= 1

                if ticks == 0:
                    to_remove.append(self.toggled[f])

            self.toggled = [x for x in self.toggled if x not in to_remove]                    

    def possibilities_helper(self):
        "Auxilary function for dealing with `possibilities()` functions"
        if not self.record:
            return
        
        record_axis = self.record["type"]
        
        x_offset = self.record.get("x offset", 0) * copysign(1, self.x)
        z_offset = self.record.get("z offset", 0) * copysign(1, self.z)
        x_increment = copysign(self.record.get("x increment", 0), self.x)
        z_increment = copysign(self.record.get("z increment", 0), self.z)
        min_dist = self.record["min_distance"]
        near_misses = self.record["miss"]

        if record_axis == "z":
            z_distance = self.z + f32(z_offset)
            z_pixel_offset = z_distance % z_increment
            if abs(z_pixel_offset) <= min_dist:

                self.add_output_with_label(f"Tick {self.record['tick']}", self.format_number(z_distance, z_distance-z_pixel_offset), "z-expr")
            else:
                z_offset_miss = z_increment - z_pixel_offset
                if near_misses is not None and (abs(z_offset_miss) <= near_misses):
                    
                    self.add_output_with_label(f"Tick {self.record['tick']}", self.format_number(z_distance + z_increment - z_pixel_offset - z_offset_miss, z_distance + z_increment - z_pixel_offset), "z-expr")


        elif record_axis == "x":
            x_distance = self.x + f32(x_offset)
            x_pixel_offset = x_distance % x_increment
            if abs(x_pixel_offset) <= min_dist:
                self.add_output_with_label(f"Tick {self.record['tick']}", self.format_number(x_distance, x_distance-x_pixel_offset), "x-expr")
            else:
                x_offset_miss = x_increment - x_pixel_offset
                if near_misses is not None and (abs(x_offset_miss) <= near_misses):
                    self.add_output_with_label(f"Tick {self.record['tick']}", self.format_number(x_distance + x_increment - x_pixel_offset - x_offset_miss, x_distance + x_increment - x_pixel_offset), "x-expr")

        elif record_axis == "xz":
            z_distance = self.z + f32(z_offset)
            z_pixel_offset = z_distance % z_increment
            x_distance = self.x + f32(x_offset)
            x_pixel_offset = x_distance % x_increment
            if abs(z_pixel_offset) <= min_dist and abs(x_pixel_offset) <= min_dist:
                self.add_output_with_label(f"Tick {self.record['tick']}", expr_type= 'expr')
                
                self.add_output_with_label("\tX", self.format_number(x_distance, x_distance-x_pixel_offset), 'x-expr')
                self.add_output_with_label("\tZ", self.format_number(z_distance, z_distance-z_pixel_offset), 'z-expr')

            else:
                z_offset_miss = z_increment - z_pixel_offset
                x_offset_miss = x_increment - x_pixel_offset
                if near_misses is not None and not (abs(x_offset_miss) > near_misses or abs(z_offset_miss) > near_misses):
                    self.add_output_with_label(f"Tick {self.record['tick']}", expr_type='expr')
                    self.add_output_with_label("\tX", self.format_number(x_distance + x_increment - x_pixel_offset - x_offset_miss, x_distance + x_increment - x_pixel_offset), 'x-expr')
                    self.add_output_with_label("\tZ", self.format_number(z_distance + z_increment - z_pixel_offset - z_offset_miss, z_distance + z_increment - z_pixel_offset), 'z-ex[r]')
   
        self.record['tick'] += 1



    def movement_multiplier(self, slip, is_sprinting, speed, slow, state):
        """
        Calculates and returns the movement multiplier `M`.

        See https://www.mcpk.wiki/wiki/Horizontal_Movement_Formulas for the fomula used to calculate `M`

        NOTE ON WATER: it seems that the equation for water is the same as air with S = 0.8/0.91 and M being either 1 or 0 multiplied by 0.98 or 1
        """
        if state == self.AIR:
            M = f32(0.02)
            # In water, walk and sprint are the same, potion effects do not affect water or air, shiftng is different

            if state == self.AIR:
                if (self.air_sprint_delay and self.previously_sprinting) or (not self.air_sprint_delay and is_sprinting):
                    M = f32(M + M * 0.3)

        elif state == self.WATER or state == self.LAVA:
            M = f32(0.02)
        

        else: # either on jump or on ground
            M = f32(0.1)

            # Deal with potion effects 
            if speed > 0:
                M = f32(M * (1.0 + f32(0.2) * float(speed)))
            if slow > 0:
                M = f32(M * max(1.0 + f32(-0.15) * float(slow), 0))

            if is_sprinting:
                M = f32(M * (1.0 + f32(0.3)))

            drag = f32(0.91) * slip
            M *= f32(0.16277136) / (drag * drag * drag)
        
        return M

    def movement_values(self):
        """
        Returns two values `forward` and `strafe` either valued at `-1`, `0`, or `1`, based on `self.inputs`.

        if "w" is in the inputs, `forward = 1`. If "a" is in inputs, `strafe = 1`, etc.
        """

        if "w" in self.inputs:
            forward = f32(1.0)
        elif "s" in self.inputs:
            forward = f32(-1.0)
        else:
            forward = f32(0.0)

        if "a" in self.inputs:
            strafe = f32(1.0)
        elif "d" in self.inputs:
            strafe = f32(-1.0)
        else:
            strafe = f32(0.0)

        return forward, strafe

############ START OF END USER'S FUNCTIONS ############

    def walk(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`walk`, `w`

---
The player walks for `duration` ticks while facing `rotation` and a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
walk # equivalent to walk(1)
walk(3, -5, slip=0.8) # walk 3 ticks facing -5 with a slip of 0.8
w.sd # walk 1 tick with s+d
```
        """
        self.move(duration, rotation, slip=slip, state=self.GROUND, speed=speed, slow=slow)

    def walk45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`walk45`, `w45`

---
The player walks for `duaration` ticks while 45ing in the direction of `rotation` and a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
walk45 # equivalent to walk45(1) or walk.wa(1, 45)
w45(3, -5, slip=0.8) # walk while 45ing for 3 ticks facing -5 with a slip of 0.8
w45.wd # raises TypeError
```
        """
        self.move(duration, rotation, 45, slip=slip, state=self.GROUND, speed=speed, slow=slow)


    def sprint(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sprint`, `s`

---
The player sprints for `duration` ticks while facing `rotation` and a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
sprint # equivalent to sprint(1)
sprint(2, -20, slip=0.8) # sprint 2 ticks facing -20 with a slip of 0.8
s.wa # sprint 1 tick with w+a
```
        """
        self.move(duration, rotation, slip=slip, is_sprinting=True, state=self.GROUND, speed=speed, slow=slow)

    def sprint45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sprint45`, `s45`

---
The player sprints for `duration` ticks while 45ing in the direction of `rotation` and a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
sprint45 # equivalent to sprint45(1) or sprint.wa(1, 45)
sprint45(2, -20, slip=0.8) # sprint while 45ing for 2 ticks facing -20 with a slip of 0.8
s45.wa # raises TypeError
```
        """
        self.move(duration, rotation, 45, slip=slip, is_sprinting=True, state=self.GROUND, speed=speed, slow=slow)


    def walkair(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`walkair`, `wa`

---
The player moves midair without sprint for `duration` ticks while facing `rotation`. \\
If `rotation` isn't provided, use the player's default rotation. 

This function can be modified by an input.

---
### Examples
```py
walkair # equivalent to walkair(1)
walkair(4, 3) # move forward midair for 4 ticks facing -3
wa.wa # move in midair with w+a
```
        """
        # print(f"{duration = }")
        self.move(duration, rotation, slip=1.0, state=self.AIR)

    def walkair45(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`walkair45`, `wa45`

---
The player moves midair without sprint for `duration` ticks while 45ing in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation. 

This function can NOT be modified by an input.

---
### Examples
```py
walkair45 # equivalent to walkair45(1) or walkair.wa(1, 45)
walkair45(4, 3) # while 45ing, move forward midair for 4 ticks facing 3
wa45.wa # raises TypeError
```
        """
        self.move(duration, rotation, 45, slip=1.0, state=self.AIR)
    

    def sprintair(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sprintair`, `sa`

---
The player moves midair with sprint for `duration` ticks while facing `rotation`. \\
If `rotation` isn't provided, use the player's default rotation. 

This function can be modified by an input.

---
### Examples
```py
sprintair # equivalent to sprintair(1)
sprinair(2, 9) # move forward midair with sprint for 2 ticks facing 9
sa.wd # move in midair with sprint holding w+d
```

---
### NOTE
In versions 1.8 to 1.19, the first sprint air tick is unsprinted if followed by a nonsprinted tick. In 1.20+, this delay is removed. \\
`version(1.8) walkjump sprintair(11)` is equivalent to `version(1.20) walkjump(2) sprintair(10)`
        """
        self.move(duration, rotation, slip=1.0, is_sprinting=True, state=self.AIR)
    
    def sprintair45(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sprintair45`, `sa45`

---
The player moves midair with sprint for `duration` ticks while 45ing in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation. 

This function can NOT be modified by an input.

---
### Examples
```py
sprintair45 # equivalent to sprintair45(1) or sprintair.wa(1, 45)
sprintair(3, -14) # move forward midair with sprint while 45ing for 3 ticks facing -14
sa45.wd # raises TypeError
```

---
### NOTE
In versions 1.8 to 1.19, the first sprint air tick is unsprinted if followed by a nonsprinted tick. In 1.20+, this delay is removed. \\
`version(1.8) walkjump45(5) sprintair45(7) sprint45` is equivalent to `version(1.20) walkjump(6) sprintair(6) sprint45`
        """
        self.move(duration, rotation, 45, slip=1.0, is_sprinting=True, state=self.AIR)
    

    def walkjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`walkjump`, `wj`

---
The player jumps without sprint and remains in midair for `duration - 1` ticks while facing `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
walkjump # equivalent to walkjump(1)
wj(6) # equivalent to wj wa(5)
wj.sa(3) # walkjump with s+a and move midair with s+a for 2 more ticks
```
        """
        if duration > 0: 
            self.move(1, rotation, slip=slip, state=self.JUMP, speed=speed, slow=slow)
            self.walkair(duration - 1, rotation)

    def walkjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`walkjump45`, `wj45`

---
The player jumps without sprint and remains in midair for `duration - 1` ticks, all while 45ing in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
walkjump45 # equivalent to walkjump45(1) or walkjump.wa(1, 45)
wj45(3) # equivalent to wj45 wa45(2)
wj45.s(3) # raises TypeError
```
        """
        if duration > 0:
            self.move(1, rotation, 45, slip=slip, state=self.JUMP, speed=speed, slow=slow)
            self.walkair45(duration - 1, rotation)


    def sprintjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sprintjump`, `sj`

---
The player jumps with sprint and remains in midair for `duration - 1` ticks while facing `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
sprintjump # equivalent to sprintjump(1)
sj(6) # equivalent to sj sa(5)
sj.wd(5) # sprintjump with w+d and (while sprinting) move midair with w+d for 4 more ticks
```
        """
        if duration > 0:
            self.move(1, rotation, slip=slip, is_sprinting=True, state=self.JUMP, speed=speed, slow=slow)
            self.sprintair(duration - 1, rotation)

    def sprintjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sprintjump45`, `sj45`

---
The player jumps with sprint and remains in midair for `duration - 1` ticks with a ground slipperiness of `slip`. \\ 
Only while midair will the player 45 in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
sprintjump45 # equivalent to sprintjump
sj45(3) # equivalent to sj45 sa45(2) or sj sa45(2)
sj45.s(2) # raises TypeError
```

---
### Important Note
When unsprinted, one can maximize the speed bonus of a 45 strafe by continuously facing 45 and strafing with the opposite key. \\
When sprinted, one must jump facing straight, and only turning to 45 midair to maximize the speed bonus. \\
Hence `sj45(15) = sj sa45(14) = sj sa.wa(14, 45)` but `sj45(15)` is stronger than `sj.wa(15, 45)`.
        """

        if duration > 0:
            self.move(1, rotation, slip=slip, is_sprinting=True, state=self.JUMP, speed=speed, slow=slow)
            self.sprintair45(duration - 1, rotation)

    def sprintstrafejump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sprintstrafejump`, `strafejump`, `stfj`

---
The player jumps with sprint and strafe, then release strafe and moves midair for `duration - 1` ticks, jumping in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
strafejump # equivalent to strafejump(1)
stfj(6) # equivalent to stfj sa(5) or sj.wa(1, 17.4786857811690446) sa(5)
stfj.wd(5) # raises TypeError
```

---
### Important Note
A sprinted strafe jump is weaker than a normal jump, that is, `stfj` gives less speed than `sj`. \\
`sprintstrafejump` is particularly useful for calculating pure distances for certain momentums where sequences starting with `sj` overuses momentum while those starting with `wj` underuses momentum.
        """
        # self.move(1, rotation, 17.4786857811690446, slip=slip, is_sprinting=True, state=self.JUMP)
        if duration > 0:
            self.inputs = "wa"
            self.move(1, rotation, self.get_optimal_strafe_jump_angle(speed=speed, slow=slow, slip=slip), slip=slip, is_sprinting=True, state=self.JUMP, speed=speed, slow=slow)

            self.inputs = "w"
            self.sprintair(duration - 1, rotation)

    def sprintstrafejump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sprintstrafejump45`, `strafejump45`, `stfj45`

---
The player jumps with sprint and strafe, then moves in midair for `duration - 1` ticks, jumping and 45ing in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
strafejump45 # equivalent to strafejump45(1)
stfj45(3) # equivalent to stfj45 sa45(2) or sj.wa(1, 17.4786857811690446) sa45(2)
stfj45.wd(5) # raises TypeError
```

---
### Important Note
When sprinting, the best way to maximize speed is to jump facing straight AND without strafe, then turning to 45 only while midair. \\
Since a sprinted strafe jump is weaker, then `stfj45(12)` gives less distance than `sj45(12)`. \\
`sprintstrafejump45` is particularly useful for calculating pure distances for certain momentums where sequences starting with `sj` overuses momentum while those starting with `wj` underuses momentum.
        """

        # self.move(1, rotation, 17.4786857811690446, slip=slip, is_sprinting=True, state=self.JUMP)
        if duration > 0:
            self.inputs = "wa"
            self.move(1, rotation, self.get_optimal_strafe_jump_angle(speed=speed, slow=slow, slip=slip), slip=slip, is_sprinting=True, state=self.JUMP, speed=speed, slow=slow)

            self.sprintair45(duration - 1, rotation)

    
    def sneak(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneak`, `sn`

---
The player sneaks (without sprint) for `duration` ticks while facing `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
sneak # equivalent to sneak(1)
sn(2, slip=0.98) # sneak for 2 ticks with a slip of 0.98
sn.s(4) # sneak with s for 4 ticks
```
        """
        self.move(duration, rotation, slip=slip, is_sneaking=True, state=self.GROUND, speed=speed, slow=slow)

    def sneak45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneak45`, `sn45`

---
The player sneaks (without sprint) for `duration` ticks while 45ing in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
sneak45 # equivalent to sneak45(1) or sneak.wa(1,45)
sn45(5, slip=0.98) # sneak for 5 ticks with a slip of 0.98 while 45ing
sn45.s(4) # raises TypeError
```
        """
        self.move(duration, rotation, 45, slip=slip, is_sneaking=True, state=self.GROUND, speed=speed, slow=slow)
    

    def sneakair(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sneakair`, `sna`

---
The player sneaks (without sprint) while midair for `duration` ticks while facing `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can be modified by an input.

---
### Examples
```py
sneakair # equivalent to sneakair(1)
sna(2, -37) # while midair, sneak for 2 ticks facing -37
sna.sa(4) # while midair, sneak with s+a for 4 ticks
```
        """
        self.move(duration, rotation, slip=1.0, is_sneaking=True, state=self.AIR)
    
    def sneakair45(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sneakair45`, `sna45`

---
The player sneaks (without sprint) while midair for `duration` ticks while 45ing in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can NOT be modified by an input.

---
### Examples
```py
sneakair45 # equivalent to sneakair45(1) or sneakair.wa(1, 45)
sna45(5, slip=0.6) # sneak in midair for 5 ticks with a slip of 0.6 while 45ing
sna45.s(2) # raises TypeError
```
        """
        self.move(duration, rotation, 45, slip=1.0, is_sneaking=True, state=self.AIR)
    

    def sneakjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneakjump`, `snj`

---
While sneaking (without sprint), the player jumps and moves midair for `duration - 1` ticks while facing `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
sneakjump # equivalent to sneakjump(1)
snj(12) # equivalent to snj sna(11)
snj.wd(4) # sneakjump with w+d, then while sneaking midair, move with s+a for 3 ticks
```
        """
        if duration > 0:
            self.move(1, rotation, slip=slip, is_sneaking=True, state=self.JUMP, speed=speed, slow=slow)
            self.sneakair(duration - 1, rotation)

    def sneakjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneakjump45`, `snj45`

---
While sneaking (without sprint), the player jumps and moves midair for `duration - 1` ticks while 45ing in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT modified by an input.

---
### Examples
```py
sneakjump45 # equivalent to sneakjump.wa(1, 45)
snj45(12) # equivalent to snj45 sna45(11)
snj.wd(4) # raises TypeError
```
        """
        if duration > 0:
            self.move(1, rotation, 45, slip=slip, is_sneaking=True, state=self.JUMP, speed=speed, slow=slow)
            self.sneakair45(duration - 1, rotation)
    
    def stop(self, duration: int = 1, /, *, slip: f32 = None):
        """
### Aliases
`stop`, `stopground`, `st`

---
The player does not input any movement while on ground for `duration` ticks with ground slipperiness `slip`. \\
If `slip` isn't provided, use the player's default ground slipperiness.

Note that this does not mean that the player immediately stops moving as the residual momentum from previous ticks can still cause the player to move.

---
### Examples
```py
stop(4)
wa.s(11) st(3) # the player still moves a bit after the wa.s(11)
```
        """
        self.move(duration, slip=slip, state=self.GROUND)
    
    def stopair(self, duration: int = 1, /):
        """
### Aliases
`stopair`, `sta`

---
The player does not input any movement while midair for `duration` ticks.

Note that this does not mean that the player immediately stops moving as the residual momentum from previous ticks can still cause the player to move.

---
### Examples
```py
stopair(6)
sj sta sa(10) # the player still moves during the sta tick
```
        """
        self.move(duration, slip=1.0, state=self.AIR)
    
    def stopjump(self, duration: int = 1, /, *, slip: f32 = None):
        """
### Aliases
`stopjump`, `stj`

---
The player jumps without any inputted movement for `duration` ticks with a ground slipperiness of `slip`.

Note that this does not mean that the player immediately stops moving as the residual momentum from previous ticks can still cause the player to move.

---
### Examples
```py
stopjump(5) # equivalent to stopjump stopair(4) or stop stopair(4)
w.sd(5) stj(12) # the player still moves throughout the 12 ticks of no inputs
```
        """
        if duration > 0:
            self.move(1, slip=slip, state=self.JUMP)
            self.stopair(duration - 1)
    
    def sneaksprint(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneaksprint`, `sns`

---
The player sneaks and sprints for `duration` ticks while facing `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
sneaksprint # equivalent to sneaksprint(1)
sns(2, slip=0.98) # sneak and sprint for 2 ticks with a slip of 0.98
sns.wa(4) # sneak and sprint with w+a for 4 ticks
```

---
### Note
In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        self.move(duration, rotation, slip=slip, is_sprinting=True, is_sneaking=True, state=self.GROUND, speed=speed, slow=slow)
    
    def sneaksprint45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneaksprint45`, `sns45`

---
The player sneaks (without sprint) for `duration` ticks while 45ing in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
sneaksprint45 # equivalent to sneaksprint45(1) or sneak.wa(1,45)
sn45(5, 1) # while 45ing, sneak for 5 ticks facing 1
sns45.sd(8) # raises TypeError
```

---
### Note
In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        self.move(duration, rotation, 45, slip=slip, is_sprinting=True, is_sneaking=True, state=self.GROUND, speed=speed, slow=slow)
    
    def sneaksprintair(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sneaksprintair`, `snsa`

---
The player sneaks and sprints while midair for `duration` ticks while facing `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can be modified by an input.

---
### Examples
```py
sneaksprintair # equivalent to sneaksprintair(1)
snsa(2, -37) # while midair, sneak and sprint for 2 ticks facing -37
snsa.wd(2) # while midair, sneak with w+d for 2 ticks
```

---
### Note
In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        self.move(duration, rotation, slip=1.0, is_sprinting=True, is_sneaking=True, state=self.AIR)
    
    def sneaksprintair45(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sneaksprintair45`, `snsa45`

---
The player sneaks and sprints while midair for `duration` ticks, 45ing in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can NOT be modified by an input.

---
### Examples
```py
sneaksprintair45 # equivalent to sneaksprintair.wa(1, 45)
snsa45(2, 11) # while midair, sneak, sprint, and 45 for 2 ticks facing 11
snsa45.wd(2) # raises TypeError
```

---
### Note
In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        self.move(duration, rotation, 45, slip=1.0, is_sprinting=True, is_sneaking=True, state=self.AIR)
    
    def sneaksprintjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneaksprintjump`, `snsj`

---
While sneaking amd sprinting, the player jumps and moves midair for `duration - 1` ticks while facing `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can be modified by an input.

---
### Examples
```py
sneaksprintjump # equivalent to sneaksprintjump(1)
snsj(12) # equivalent to snsj snsa(11)
snsj.wd(4) # sprint+sneak jump with w+d, then while sprint+sneaking midair, move with w+d for 4 ticks
```

---
### Note
In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        if duration > 0:
            self.move(1, rotation, slip=slip, is_sprinting=True, is_sneaking=True, state=self.JUMP, speed=speed, slow=slow)
            self.sneaksprintair(duration - 1, rotation)
    
    def sneaksprintjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
### Aliases
`sneaksprintjump45`, `snsj45`

---
While sneaking amd sprinting, the player jumps and moves midair for `duration - 1` ticks while 45ing in the direction of `rotation` with a ground slipperiness of `slip`. \\
If `rotation` isn't provided, use the player's default rotation. \\
If `slip` isn't provided, use the player's default ground slipperiness.

This function can NOT be modified by an input.

---
### Examples
```py
sneaksprintjump45 # equivalent to sneaksprintjump45(1) or snsj45
snsj45(3) # equivalent to snsj45(1, 9.1148519592841453) snsa45(2)
snsj45.wd(4) # raises TypeError
```

---
### Notes
In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.

While sneaking and sprinting, it is stronger to strafe jump facing at a 9.1148519592841453 angle instead of jumping while facing 0 WITHOUT strafing. In other words \\
`snsj45 = snsj.wa(1, 9.1148519592841453)` is stronger than `snsj`
        """
        if duration > 0:
            self.inputs = "wa"
            self.move(1, rotation, self.get_optimal_strafe_jump_angle(speed=speed, slow=slow, slip=slip, is_sneaking=True), slip=slip, is_sprinting=True, is_sneaking=True, state=self.JUMP, speed=speed, slow=slow)
            self.sneaksprintair45(duration - 1, rotation)

    def walkwater(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`walkwater`, `water`, `wwt`, `wt`

---

(Sprint) Swimming in water for `duration` ticks facing `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can be modified by an input.

---
### Examples
```py
water # equivalent to water(1) or wt
water(5, 3) # swim in water for 5 ticks facing 3
wt.wd(10) # swim in water for 10 ticks holding w+d
```

---
### Notes
Swimming in 1.8 is the same as swimming without sprint in later versions. \\
Swimming in this manner is treated like air movement with `slip = 0.8/0.91`. \\
Potion effects and sprinting or walking (for 1.8) does not make a difference while in water, however sprinted air delay is affected by whether you were sprinting inside water.

        """
        self.move(duration, rotation, slip=f32(0.8/0.91), state=self.WATER)

    def sprintwater(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases
`sprintwater`, `swt`

---

(Sprint) Swimming in water for `duration` ticks facing `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can be modified by an input.

---
### Examples
```py
CHANGE TO SPRINT
```

---
### Notes
Swimming in 1.8 is the same as swimming without sprint in later versions. \\
Swimming in this manner is treated like air movement with `slip = 0.8/0.91`. \\
Potion effects and sprinting or walking (for 1.8) does not make a difference while in water, however sprinted air delay is affected by whether you were sprinting inside water.

        """
        self.move(duration, rotation, slip=f32(0.8/0.91), state=self.WATER, is_sprinting=True)

    def walkwater45(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases


---

(Sprint) Swimming in water for `duration` ticks while 45ing in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can NOT be modified by an input.

---
### Examples
```py
water45 # equivalent to water45(1) or wt45
water45(5, 3) # while 45ing, swim in water for 5 ticks facing 3
wt.wd(10) # raises TypeError
```

---
### Notes
Swimming in 1.8 is the same as swimming without sprint in later versions. \\
Swimming in this manner is treated like air movement with `slip = 0.8/0.91`. \\
Potion effects and sprinting or walking (for 1.8) does not make a difference.

        """
        self.move(duration, rotation, 45, slip=f32(0.8/0.91), state=self.WATER)

    def sprintwater45(self, duration: int = 1, rotation: f32 = None, /):
        """
### Aliases


---

(Sprint) Swimming in water for `duration` ticks while 45ing in the direction of `rotation`. \\
If `rotation` isn't provided, use the player's default rotation.

This function can NOT be modified by an input.

---
### Examples
```py
water45 # equivalent to water45(1) or wt45
water45(5, 3) # while 45ing, swim in water for 5 ticks facing 3
wt.wd(10) # raises TypeError
```

---
### Notes
Swimming in 1.8 is the same as swimming without sprint in later versions. \\
Swimming in this manner is treated like air movement with `slip = 0.8/0.91`. \\
Potion effects and sprinting or walking (for 1.8) does not make a difference.

        """
        self.move(duration, rotation, 45, slip=f32(0.8/0.91), state=self.WATER, is_sprinting=True)


    def stopwater(self, duration: int = 1, /):
        """
### Aliases
`stopwater`, `stw`

---
The player does not input any movement while inside water `duration` ticks. \\

Note that this does not mean that the player immediately stops moving as the residual momentum from previous ticks can still cause the player to move.

---
### Examples
```py
stopwater(4)
water.w(7) stw(3) # the player still moves a bit after the water.w(7)
```
        """
        self.move(duration, slip=f32(0.8/0.91), state=self.WATER)

    def sneakwater(self, duration: int = 1, rotation:f32 = None, /):
        """
        Sneak while in water
        """
        self.move(duration, rotation, slip=f32(0.8/0.91), state=self.WATER, is_sneaking=True)

    def sneakwater45(self, duration: int = 1, rotation:f32 = None, /):
        """
        Sneak45 while in water
        
        """
        self.move(duration, rotation, 45, slip=f32(0.8/0.91), state=self.WATER, is_sneaking=True)

    def sneaksprintwater(self, duration: int = 1, rotation:f32 = None, /):
        """
        Sneak and sprint while in water

        ---
        ### Note
        In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        self.move(duration, rotation, slip=f32(0.8/0.91), state=self.WATER, is_sneaking=True, is_sprinting=True)

    def sneaksprintwater45(self, duration: int = 1, rotation:f32 = None, /):
        """
        Sneak45 and sprint while in water

        ---
        ### Note
        In game, sprinted sneak is activated if and only if 1 tick before sneaking, the player is sprinting.
        """
        self.move(duration, rotation, 45, slip=f32(0.8/0.91), state=self.WATER, is_sneaking=True, is_sprinting=True)
    
    def sword(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block on the ground.
        """

        self.move(duration, rotation, slip=slip, speed=speed, slow=slow, state=self.GROUND, is_blocking=True)


    def swordair(self, duration: int = 1, rotation: f32 = None, /):
        """
        Sword block midair.
        """
        self.move(duration, rotation, slip=1.0, state=self.AIR, is_blocking=True)
    
    def swordsneak(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block on the ground.
        """

        self.move(duration, rotation, slip=slip, speed=speed, slow=slow, state=self.GROUND, is_blocking=True, is_sneaking=True)
    
    def swordsneakair(self, duration: int = 1, rotation: f32 = None, /):
        """
        Sneak and sword block midair.
        """
        self.move(duration, rotation, slip=1.0, state=self.AIR, is_sneaking=True, is_blocking=True)

    def sword45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block on the ground.
        """

        self.move(duration, rotation, 45, slip=slip, speed=speed, slow=slow, state=self.GROUND, is_blocking=True)


    def swordair45(self, duration: int = 1, rotation: f32 = None, /):
        """
        Sword block midair.
        """
        self.move(duration, rotation, 45, slip=1.0, state=self.AIR, is_blocking=True)
    
    def swordsneak45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block on the ground.
        """

        self.move(duration, rotation, 45, slip=slip, speed=speed, slow=slow, state=self.GROUND, is_blocking=True, is_sneaking=True)
    
    def swordsneakair45(self, duration: int = 1, rotation: f32 = None, /):
        """
        Sneak and sword block midair.
        """
        self.move(duration, rotation, 45, slip=1.0, state=self.AIR, is_sneaking=True, is_blocking=True)

    def swordwater(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, slip=f32(0.8/0.91), state=self.WATER, is_blocking=True)

    def swordsneakwater(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, slip=f32(0.8/0.91), state=self.WATER, is_blocking=True, is_sneaking=True)

    def swordwater45(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, 45, slip=f32(0.8/0.91), state=self.WATER, is_blocking=True)

    def swordsneakwater45(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, 45, slip=f32(0.8/0.91), state=self.WATER, is_blocking=True, is_sneaking=True)
    
    def swordjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block jump on the ground.
        """
        if duration > 0:
            self.move(1, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, is_blocking=True)
            self.swordair(duration-1, rotation)

    def swordjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block jump and 45 on the ground.
        """
        if duration > 0:
            self.move(1, rotation, 45, slip=slip, speed=speed, slow=slow, state=self.JUMP, is_blocking=True)
            self.swordair45(duration-1, rotation)

    def swordsneakjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block, sneak, and jump on the ground.
        """
        if duration > 0:
            self.move(1, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, is_blocking=True, is_sneaking=True)
            self.swordsneakair(duration-1, rotation)

    def swordsneakjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Sword block, sneak, and jump and 45 on the ground.
        """
        if duration > 0:
            self.move(1, rotation, 45, slip=slip, speed=speed, slow=slow, state=self.JUMP, is_blocking=True, is_sneaking=True)
            self.swordsneakair45(duration-1, rotation)
    
    def web(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Web on ground
        """
        self.move(duration, rotation, slip=slip, speed=speed, slow=slow, state=self.GROUND, in_web = True)

    def web45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Web45 on ground
        """
        self.move(duration, rotation, rotation_offset = 45, slip=slip, speed=speed, slow=slow, state=self.GROUND, in_web = True)

    def sprintweb(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Web on ground
        """
        self.move(duration, rotation, slip=slip, speed=speed, slow=slow, state=self.GROUND, in_web = True, is_sprinting=True)

    def sprintweb45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Web45 on ground
        """
        self.move(duration, rotation, rotation_offset = 45, slip=slip, speed=speed, slow=slow, state=self.GROUND, in_web = True, is_sprinting=True)
    
    def webair(self, duration: int = 1, rotation: f32 = None, /):
        """
        Web on ground
        """
        self.move(duration, rotation, slip=1.0, state=self.AIR, in_web = True)

    def webair45(self, duration: int = 1, rotation: f32 = None, /):
        """
        Web45 on ground
        """
        self.move(duration, rotation, rotation_offset = 45, slip=1.0, state=self.AIR, in_web = True)

    def sprintwebair(self, duration: int = 1, rotation: f32 = None, /):
        """
        Web on ground
        """
        self.move(duration, rotation, slip=1.0, state=self.AIR, in_web = True, is_sprinting=True)

    def sprintwebair45(self, duration: int = 1, rotation: f32 = None, /):
        """
        Web45 on ground
        """
        self.move(duration, rotation, rotation_offset = 45, slip=1.0, state=self.AIR, in_web = True, is_sprinting=True)
    
    def webjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Web on ground
        """
        if duration > 0:
            self.move(1, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True)
            self.webair(duration-1, rotation)
    
    def sprintwebjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        if duration > 0:
            self.move(1, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True, is_sprinting=True)
            self.sprintwebair(duration-1, rotation)
    
    def webjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        """
        Web on ground
        """
        if duration > 0:
            self.move(1, rotation, rotation_offset=45, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True)
            self.webair45(duration-1, rotation)
    
    def sprintwebjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        if duration > 0:
            self.move(1, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True, is_sprinting=True)
            self.sprintwebair45(duration-1, rotation)
    
    def sneakweb(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        self.move(duration, rotation, slip=slip, speed=speed, slow=slow, state=self.GROUND, in_web = True, is_sneaking=True)

    def sneakwebair(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, slip=1.0, in_web=True, is_sneaking=True, state=self.AIR)
    
    def sneakweb45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        self.move(duration, rotation, rotation_offset=45, slip=slip, speed=speed, slow=slow, state=self.GROUND, in_web = True, is_sneaking=True)

    def sneakwebair45(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, rotation_offset=45, slip=1.0, in_web=True, is_sneaking=True, state=self.AIR)
    
    def sneakwebjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        self.move(duration, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True, is_sneaking=True)

    def sneakwebjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        self.move(duration, rotation, rotation_offset=45, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True, is_sneaking=True)
    
    def sneaksprintweb(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        self.move(duration, rotation, slip=slip, in_web=True, is_sneaking=True, is_sprinting=True, state=self.GROUND, speed=speed, slow=slow)
    
    def sneaksprintweb45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        self.move(duration, rotation, slip=slip, rotation_offset=45, in_web=True, is_sneaking=True, is_sprinting=True, state=self.GROUND, slow=slow, speed=speed)

    def sneaksprintwebair(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, slip=1.0, in_web=True, is_sneaking=True, is_sprinting=True, state=self.AIR)
    
    def sneaksprintwebair45(self, duration: int = 1, rotation: f32 = None, /):
        self.move(duration, rotation, slip=1.0, rotation_offset=45, in_web=True, is_sneaking=True, is_sprinting=True, state=self.AIR)

    def sneaksprintwebjump(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        if duration > 0:
            self.move(1, rotation, slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True, is_sprinting=True, is_sneaking=True)
            self.sneaksprintwebair(duration-1, rotation)
    
    def sneaksprintwebjump45(self, duration: int = 1, rotation: f32 = None, /, *, slip: f32 = None, speed: int = None, slow: int = None):
        if duration > 0:
            self.inputs = "wa"
            self.move(1, rotation, self.get_optimal_strafe_jump_angle(speed=speed, slow=slow, slip=slip, is_sneaking=True), slip=slip, speed=speed, slow=slow, state=self.JUMP, in_web = True, is_sprinting=True, is_sneaking=True)
            self.sneaksprintwebair45(duration-1, rotation)


    def stopweb(self, duration: int = 1, /, *, slip: f32 = None):
        """
        Web on ground
        """
        self.move(duration, slip=slip, state=self.GROUND, in_web=True)
    
    def stopwebair(self, duration: int = 1, /):
        self.move(duration, in_web=True, state=self.AIR)
    

    # Sneak jump (fml)
    # sneak sprint
    # sprint strafe jump


    def lava(self, duration: int = 1, rotation:f32 = None, /):
        # self.move(duration, rotation, slip=f32(0.9/0.91), state=self.LAVA, is_sneaking=True)
        self.move(duration, rotation, slip=f32(0.5/0.91), state=self.LAVA)

    # PRIVATE FUNCTION
    def get_optimal_strafe_jump_angle(self, speed: int = None, slow: int = None, slip: f32 = None, is_sneaking: bool = False):
        player = Player.copy_player(self)
        player.x = 0.0
        player.z = 0.0
        player.vx = 0.0
        player.vz = 0.0
        player.rotation_queue = []
        player.rotation = 0.0
        if speed is not None:
            player.swift = speed
        if slow is not None:
            player.slow = slow
        if slip is not None:
            player.default_ground_slip = slip

        # print(player.swift, player.slow)
        
        if is_sneaking:
            player.simulate("snsj.wa")
        else:
            player.simulate("sj.wa")
        
        # print(abs(deg(arctan(-player.vx, player.vz))))
        return abs(deg(arctan(-player.vx, player.vz)))

    # RETURNERS:
    def outz(self, centered_about: float = 0, /, label: str = "outz"):
        """
        Displays your Z position.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"outz"`. For example,

        >>> p = Player()
        >>> p.z = 2.345296
        >>> p.outz()                    # outz: 2.345296 
        >>> p.outz(centered_about = 1)  # outz: 1.0 + 1.345296
        >>> p.outz(label = "new label") # new label: 2.345296
        

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(self.z, centered_about), "z-expr")
    
    def zmm(self, centered_about: float = 0, /, label: str = "zmm"):
        """
        Displays your Z position in terms of momentum used. See `dist_to_mm` for the conversion.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"zmm"`. For example,
        ```py
        >> p = Player()
        >> p.z = 2.345296
        >> p.zmm()                    # zmm: 1.745296 
        >> p.zmm(centered_about = 1)  # zmm: 1.0 + 0.745296
        >> p.zmm(label = "new label") # new label: 1.745296 
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(Player.dist_to_mm(self.z), centered_about), "z-expr")
    
    def zb(self, centered_about: float = 0, /, label: str = "zb"):
        """
        Displays your Z position in terms of blocks traversed. See `dist_to_blocks` for the conversion.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"zb"`. For example,
        ```py
        >> p = Player()
        >> p.z = 2.345296
        >> p.zb()                    # zb: 2.945296
        >> p.zb(centered_about = 1)  # zb: 1.0 + 1.945296
        >> p.zb(label = "new label") # new label: 2.945296
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(Player.dist_to_block(self.z), centered_about), "z-expr")
    
    def outvz(self, centered_about: float = 0, /, label: str = "vz"):
        """
        Displays your Z velocity.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"vz"`. For example,
        ```py
        >> p = Player()
        >> p.vz = 2.345296
        >> p.outvz()                    # outvz: 2.945296
        >> p.outvz(centered_about = 1)  # outvz: 1.0 + 1.945296
        >> p.outvz(label = "new label") # new label: 2.945296
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(self.vz, centered_about), "z-expr")
        m = self.vz - centered_about
        return m

    def outx(self, centered_about: float = 0, /, label: str = "outx"):
        """
        Displays your X position.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"outx"`. For example,
        ```py
        >> p = Player()
        >> p.x = 2.345296
        >> p.outx()                    # outx: 2.345296 
        >> p.outx(centered_about = 1)  # outx: 1.0 + 1.345296
        >> p.outx(label = "new label") # new label: 2.345296
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(self.x, centered_about), "x-expr")
    
    def xmm(self, centered_about: float = 0, /, label: str = "xmm"):
        """
        Displays your X position in terms of momentum used. See `dist_to_mm` for the conversion.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"xmm"`. For example,
        ```py
        >> p = Player()
        >> p.x = 2.345296
        >> p.xmm()                    # xmm: 1.745296 
        >> p.xmm(centered_about = 1)  # xmm: 1.0 + 0.745296
        >> p.xmm(label = "new label") # new label: 1.745296 
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(Player.dist_to_mm(self.x), centered_about), "x-expr")
    
    def xb(self, centered_about: float = 0, /, label: str = "xb"):
        """
        Displays your X position in terms of blocks traversed. See `dist_to_blocks` for the conversion.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"xb"`. For example,
        ```py
        >> p = Player()
        >> p.x = 2.345296
        >> p.xb()                    # xb: 2.945296
        >> p.xb(centered_about = 1)  # xb: 1.0 + 1.945296
        >> p.xb(label = "new label") # new label: 2.945296
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(Player.dist_to_block(self.x), centered_about), "x-expr")

    def outvx(self, centered_about: float = 0, /, label: str = "vx"):
        """
        Displays your X velocity.

        Use `centered_about` to display the position relative to that number. \\
        Use `label` to change the label on the display, default `"vx"`. For example,
        ```py
        >> p = Player()
        >> p.vx = 2.345296
        >> p.outvx()                    # outvx: 2.945296
        >> p.outvx(centered_about = 1)  # outvx: 1.0 + 1.945296
        >> p.outvx(label = "new label") # new label: 2.945296
        ```

        On mothball, you don't included `"` or `'` delimiters in your `label` argument. Doing so will result in the `"` and `'` displaying in the label.
        """
        self.add_output_with_label(label.strip(), self.format_number(self.vx, centered_about), "x-expr")

    def vec(self):
        """
        Displays your total speed and the angle.

        Unlike other functions such as `outz`, `xmm`, `vz`, etc, you cannot change the display. It will always show in the form
        ```py
        Speed: float
        Angle: float
        ```
        """
        self.add_output_with_label("Speed", self.format_number(sqrt(self.vx**2 + self.vz**2)), "expr")
        self.add_output_with_label("Angle", self.format_number(deg(arctan(-self.vx, self.vz))), "expr")
    
    def outangle(self, centered_about: float = 0, /, label: str = "facing"):
        """
        ### Aliases
        `outfacing`, `outa`, `outf`

        ---

        Displays the current angle the player is facing.

        Example: `tq(4,7,-3,5,-12) sj45(4) outangle sa45(4)` outputs `facing: 13` because the simulation's default facing at that point is `13`.
        """
        self.add_output_with_label(label.strip(), self.format_number(self.rotation, centered_about), "expr")
    
    def outturn(self, centered_about: float = 0, /, label: str = "turn"):
        """
        ### Aliases
        `outt`

        ---

        Displays the player's last turn.

        Example: `aq(2,10, -13) sj(3) outturn` outputs `turn: -23`
        """
        self.add_output_with_label(label.strip(), self.format_number(self.last_turn, centered_about), "expr")

    def effectsmultiplier(self, speed: int = None, slow: int = None):
        """
        Returns the total effects multiplier based on the player's speed and slowness effects.

        If `speed_lvl` or `slow_lvl` isn't provided, use the player's current speed/slowness respectfully.

        The effects multiplier is calculated by
        ```py
        max((1 + (0.2 * speed)) * (1 - (0.15 * slow)), 0)
        ```

        The base multiplier is 1 with no speed or slowness.
        """

        if speed is None:
            speed = self.swift
        if slow is None:
            slow = self.slow

        if speed < 0 or 256 < speed:
            raise ValueError(f"argument 'speed' should be an integer between 0 and 256 inclusive, not {speed}")
        if slow < 0 or 256 < slow:
            raise ValueError(f"argument 'slow' should be an integer between 0 and 256 inclusive, not {slow}")

        multiplier = max((1 + (0.2 * speed)) * (1 - (0.15 * slow)), 0) * 100
        self.add_output(f"Speed {speed} Slow {slow} ({int(round(multiplier))}% base speed)")

    def printdisplay(self, string: str = "", /):
        """
        Prints `string` to the output (in order).
        """
        if self.reverse:
            string = "".join([x for x in reversed(string)])
        self.add_output(string)

    # SETTERS
    def face(self, angle_in_degrees: f32, /):
        "Sets the player's default facing in degrees"
        self.rotation = angle_in_degrees
    
    def turn(self, angle_in_degrees: f32, /):
        "Rotates the player's default facing in degrees"
        self.rotation += angle_in_degrees

    def setposz(self, value: float, /):
        "Sets the player's Z position"
        self.z = value
    
    def setvz(self, value: float, /):
        "Sets the player's Z velocity"
        self.vz = value

    def setposx(self, value: float, /):
        "Sets the player's X position"
        self.x = value
    
    def setvx(self, value: float, /):
        "Sets the player's X velocity"
        self.vx = value
    
    def setslip(self, value: f32, /):
        "Sets the player's ground slipperiness"
        self.default_ground_slip = value
    
    def setprecision(self, decimal_places: int, /):
        "Sets the decimal precision for displaying outputs, must be an integer between `0` and `16` inclusive, raises `ValueError` otherwise."
        if decimal_places < 0 or decimal_places > 16:
            raise ValueError(f"precision() only takes integers between 0 to 16 inclusive, got {decimal_places} instead.")
        self.precision = decimal_places
    
    def inertia(self, value: f32, /):
        "Sets the player's inertia threshold"
        self.inertia_threshold = value
    
    def toggle(self, ticks: int, *functions: str):
        for function in functions:
            # func = Player.FUNCTIONS.get()
            # if func is None:
            #     raise NameError(f"Function {function} not found.")
            # if func in self.toggled:
            #     self.toggled.add(function)
            # elif func in self.toggled:
            #     self.toggled.remove(function)
            self.toggled.append([ticks, function])
            # This is dangerous


    def sprintairdelay(self, toggle: str, /):
        """
        `toggle` will toggle off if it is the string `"false"`, else it will assume true.

        Toggles the player's sprint air delay. If toggled, it takes 1 tick longer to activate sprint in midair if the previous tick was unsprinted midair. 
        
        Versions 1.8 to 1.19 have a sprint air delay while later versions don't, so if you intend to calculate 1.20+ movement, set sprint air delay to `false`.
        """
        toggle = toggle.lower().strip()
        if toggle == "false":
            self.air_sprint_delay = False
        else:
            self.air_sprint_delay = True
    
    def sneakdelay(self, toggle: str, /):
        """
        `toggle` will toggle true if it is the string `"true"`, else it will assume false.

        Toggles the player's sneak delay. If toggled, it takes 1 tick longer to activate sneak if the previous tick didn't sneak. 
        
        Versions 1.8 to 1.19 dont have a sneak delay while later versions do, so if you intend to calculate 1.20+ movement, set sprint air delay to `true`.
        """
        toggle = toggle.lower().strip()
        if toggle == "true":
            self.sneak_delay = True
        else:
            self.sneak_delay = False
    
    def singleaxisinertia(self, toggle: str, /):
        """
        Set's inertia to affect individual axis.
        """
        toggle = toggle.lower().strip()
        if toggle == "true":
            self.inertia_axis = 1
        else:
            self.inertia_axis = 2


    def version(self, string: str, /):
        "String should be in the form `1.n`, for example the minimum `1.8` is default. Max is currently `1.20`"
        components = string.split(".")
        try:
            one, version_number = components
            patch_number = None
        except:
            try:
                one, version_number, patch_number = components
            except:
                raise ValueError(f"{string} is not a valid version")

    
        if one != "1":
            raise ValueError(f"{string} is not a valid version")
        if int(version_number) > 8:
            self.inertia(0.003)
        if int(version_number) > 19:
            self.sprintairdelay("false")
            self.sneakdelay("true")
    
    def speed(self, multiplier: int, /):
        """
        Gives the player speed, where `speed(0)` is equivalent to no speed effects and `speed(256)` is the maximum speed effect.
        
        `multiplier` is a positive integer from 0 to 256, raises ValueError if integer provided is not within this range.
        """
        if multiplier < 0 or 256 < multiplier:
            raise ValueError(f"speed() takes an integer between 0 and 256 inclusive, not {multiplier}")
        self.swift = multiplier
    
    def slowness(self, multiplier: int, /):
        """
        Gives the player slowness, where `slow(0)` is equivalent to no slow effects and `slow(7)` is the maximum slowness effect.
        
        `multiplier` is a positive integer from 0 to 256, raises ValueError if integer provided is not within this range.

        Slowness is calculated with `max(1 + (-0.15) * multiplier, 0)` so `slow(7)` already gives the maximum slowness effect which would scale ground velocity by `0`. This also means that \\
        `slow(7) = slow(8) = ... = slow(256)`

        If the slowness effect was unbounded, then `slow(7)` and stronger effects would result in moving backwards.
        """
        if multiplier < 0 or 256 < multiplier:
            raise ValueError(f"slow() takes an integer between 0 and 256 inclusive, not {multiplier}")
        self.slow = multiplier
    
    def var(self, variable_name: str, value: str):
        """
        Assigns `value` to `variable_name`
        
        A valid variable name is any sequence of alphabet letters a-z or A-Z, numerical digits (0-9), an underscore `_`, or any combination of them. \\
        A number cannot be the first character in the variable name.

        `var()` will attempt to convert the value to the appropiate datatype, which only supports
        ```py
        int | float | str
        ```
        """
        # if len(variable_name) > 1 and variable_name in Player.FUNCTIONS.keys():
        #     raise ValueError(f"There is no reason for you to name your variable '{variable_name}' as that is already a function.")

        find_var_regex = r"^([a-zA-Z_][a-zA-Z0-9_]*)$"
        if not re.findall(find_var_regex, variable_name): # Either has one match or no matches
            raise SyntaxError(f"'{variable_name}' is not a valid variable name")
        
        try: value = int(value)
        except ValueError: 
            try: value = float(value)
            except ValueError:
                try: value = eval(value, {"__builtins__": {}}, self.local_vars)
                except:
                    try:  # PLEASE PREVENT OTHER FUNCTIONS
                        self.simulate(value)
                        value = self.output[-1][0].split()
                        if len(value) == 2:
                            value = float(value[-1])
                        elif len(value) == 4:
                            value = float(f"{value[-2]}{value[-1]}")
                        
                    except:
                        pass
        
        self.local_vars[variable_name] = value

    # Setting rotations
    def anglequeue(self, *angles: f32):
        """
        Adds `angles` to the rotation queue, each angle being used for 1 tick.
        
        In mothball syntax, `anglequeue(1,-2,3) walk(3)` is the same as `face(1) walk face(-2) walk face(3) walk`
        """
        for angle in angles:
            self.rotation_queue.append(("angle", angle))
            # print(self.rotation_queue)
    
    def turnqueue(self, *angles: float):
        """
        Adds `angles` to the rotation queue, each tick turning `angle` degrees.
        
        In mothball syntax, `turnqueue(1,-2,3) walk(3)` is the same as `turn(1) walk turn(-2) walk turn(3) walk`
        """
        for angle in angles:
            self.rotation_queue.append(("turn", angle))

    # Nested functions
    def repeat(self, sequence: str, count: int, /):
        "Run `sequence` for `count` times. Raises `ValueError` if `count < 0`"
        
        if count < 0:
            raise ValueError(f"repeat() must have a nonnegative argument 'count'")
        
        for _ in range(count):
            self.simulate(sequence, return_defaults=False)
    
    def possibilities(self, sequence: str, min_distance: float, offset: float = 0.6, /, *, increment: float = 0.0625, miss: float = None):
        """
        Displays ticks where while `sequence` is run, the player reaches certain block milestones ONLY ON Z (as determined by `increment`, default 0.0625) less than or equal to `min_distance`, useful to check which tiers results in precise landings.
        
        Use `offset` to offset each tick accordingly. An offset of 0.6 (which is default) is for jumping from block to block. An offset of -0.6 is for z neos. An offset of 0 will just record pure distances, helpful for example doing "block avoid" jumps.

        `increment` is set to 0.0625 by default, but in modern versions you can set it to 0.03125 for useful results with newer blocks.

        if a float for 'miss` is provided, it will also display ticks that are `miss` away from reaching a milestone.
        """

        if not self.record: # JUST FOR NOW
            self.record = {"type":"z", "tick":1, "min_distance": min_distance, "z offset": offset, "z increment": increment, "miss": miss}
        else:
            raise TypeError(f"Nested posibilities functions are not allowed.")
        self.simulate(sequence, return_defaults=False)
        self.record = {}
    
    def xpossibilities(self, sequence: str, min_distance: float, offset: float = 0.6, /, *, increment: float = 0.0625, miss: float = None):
        """
        Displays ticks where while `sequence` is run, the player reaches certain block milestones ONLY ON X (as determined by `increment`, default 0.0625) less than or equal to `min_distance`, useful to check which tiers results in precise landings.
        
        Use `offset` to offset each tick accordingly. An offset of 0.6 (which is default) is for jumping from block to block. An offset of 0 will just record pure distances, helpful for example doing "block avoid" jumps.

        `increment` is set to 0.0625 by default, but in modern versions you can set it to 0.03125 for useful results with newer blocks.

        if a float for 'miss` is provided, it will also display ticks that are `miss` away from reaching a milestone.
        """
        if not self.record:
            self.record = {"type": "x", "tick":1, "min_distance": min_distance, "x offset": offset, "x increment": increment, "miss": miss}
        else:
            raise TypeError(f"Nested posibilities functions are not allowed.")
        self.simulate(sequence, return_defaults=False)
        self.record = {}
    
    def xzpossibilities(self, sequence: str, min_distance: float, x_offset: float = 0.6, z_offset: float = 0.6, /, *, x_increment: float = 0.0625, z_increment: float = 0.0625, miss: float = None):
        """
        Displays ticks where while `sequence` is run, the player reaches certain block milestones (as determined by `increment`, default 0.0625) less than or equal to `min_distance`, useful to check which tiers results in precise landings.
        
        Use `offset` to offset each tick accordingly. An offset of 0.6 (which is default) is for jumping from block to block. An offset of 0 will just record pure distances, helpful for example doing "block avoid" jumps.

        `increment` is set to 0.0625 by default, but in modern versions you can set it to 0.03125 for useful results with newer blocks.

        if a float for 'miss` is provided, it will also display ticks that are `miss` away from reaching a milestone.
        """

        if not self.record:
            self.record = {"type": "xz", "tick":1, "min_distance": min_distance, "x offset": x_offset, "z offset": z_offset, "x increment":x_increment, "z increment":z_increment, "miss": miss}
        else:
            raise TypeError(f"Nested posibilities functions are not allowed.")
        self.simulate(sequence, return_defaults=False)
        self.record = {}


    def ballhelp(self, func: str):
        "Gets help about function `func`"
        # NOTE: probably format the string better to include color, etc
        f = Player.FUNCTIONS.get(func)
        if f is None:
            f = self.local_funcs.get(func)
            if f is None:
                raise NameError(f"Function {func} not found")
            

        f_sig = inspect.signature(f).parameters
        self.add_output(f"Help with {func}:")
        self.add_output(f"  Arguments:")
        

        for y in f_sig.values(): # PLEASE ADD * and /
            if y.name != "self":
                self.add_output(f"    {y}")
        
        self.add_output('')
        self.add_output(f.__doc__)

    # SOME EXTRA MISCS
    def dimensions(self, x: float, z: float, /): # NOT FINALIZED
        """
        Returns information regarding `x` by `z` block jump. Note that `x` and `z` are in terms of blocks, that is, assuming you jump from one corner of the block to the other corner.

        In the future, there may be different functions that allow `x` and `z` in terms of displacement or momentum used.
        """

        # self.add_output("Jump Dimension Info", f"A {x} × {z} block jump is equivalent to\n                     {self.format_number(Player.dist_to_block(sqrt(Player.block_to_dist(x)**2 + Player.block_to_dist(z)**2)), return_as_string=True)} block jump.\n                     Angle: {self.format_number(deg(arctan(Player.block_to_dist(z), Player.block_to_dist(x))), return_as_string=True)}")

        self.add_output("Jump Dimension Info")
        self.add_output(f"\tA {x} × {z} block jump is equivalent to")

        self.add_output(f"\t{self.format_number(Player.dist_to_block(sqrt(Player.block_to_dist(x)**2 + Player.block_to_dist(z)**2)), return_as_string=True)} block jump.")

        self.add_output(f"\tAngle: {self.format_number(deg(arctan(Player.block_to_dist(z), Player.block_to_dist(x))), return_as_string=True)}")
    
    
    @staticmethod
    def copy_player(player: "Player"):
        "Copies the player"
        p = Player()
        p.rotation_queue = player.rotation_queue
        p.rotation = player.rotation
        p.state = player.state
        p.default_ground_slip = player.default_ground_slip
        p.previous_slip = player.previous_slip
        p.air_sprint_delay = player.air_sprint_delay
        p.sneak_delay = player.sneak_delay
        p.previously_sprinting = player.previously_sprinting
        p.swift = player.swift
        p.slow = player.slow
        p.local_vars = player.local_vars

        return p
    
    def optimize(self, x: float, z: float, sequence: str, conversion: "function" = lambda x: x, /) -> tuple[float, float] | float:
        p1 = Player.copy_player(self)
        p1.inertia_threshold = 0.0
        p1.simulate(sequence)

        p2 = Player.copy_player(self)
        p2.inertia_threshold = 0.0
        p2.vz = 1.0
        p2.vx = 1.0
        p2.simulate(sequence)

        if x:
            if p1.x == p2.x:
                raise ZeroDivisionError(f"Float division by 0, perhaps you reset your position at the end of a sequence or nested same axis optimize functions?")
            vx = (p1.x - conversion(x)) / (p1.x - p2.x)
        if z:
            if p1.z == p2.z:
                raise ZeroDivisionError(f"Float division by 0, perhaps you reset your position at the end of a sequence or nested same axis optimize functions?")
            vz = (p1.z - conversion(z)) / (p1.z - p2.z)
        
        if x and z:
            return vx, vz
        elif x:
            return vx
        elif z:
            return vz
    
    def bwmm(self, zmm: float, sequence: str, /):
        "Attempts to find the speed such that executing `sequence` results in using `zmm` blocks of momentum on the Z axis. A warning is raised if the simulation using the calculated speed doesn't match `zmm`, meaning that inertia was encountered while simulating."
        vz = self.optimize(None, zmm, sequence, Player.mm_to_dist)

        self.simulate(f" z(0) vz({vz}) outvz(label=Vz Needed) {sequence} zmm(label=Zmm Used) ", return_defaults=False)

        if abs(Player.dist_to_mm(self.z) - zmm) > 1e-5:
            self.add_output_with_label("Warning", "encountered inertia on Z while optimizing!", "warning")

    def wall(self, z: float, sequence: str, /):
        "Attempts to find the speed such that executing `sequence` results in a displacement of `z` on the Z axis. A warning is raised if the simulation using the calculated speed doesn't match `z`, meaning that inertia was encountered while simulating."
        vz = self.optimize(None, z, sequence)

        self.simulate(f" z(0) vz({vz}) outvz(label=Vz Needed) {sequence} outz(label=Z dist)")
        
        if abs(self.z - z) > 1e-5:
            self.add_output_with_label("Warning", "encountered inertia on Z while optimizing!", "warning")
    
    def blocks(self, zb: float, sequence: str, /):
        "Attempts to find the speed such that executing `sequence` results in traversing `zb` blocks on the Z axis. A warning is raised if the simulation using the calculated speed doesn't match `zb`, meaning that inertia was encountered while simulating."
        vz = self.optimize(None, zb, sequence, Player.block_to_dist)

        self.simulate(f" z(0) vz({vz}) outvz(label=Vz Needed) {sequence} zb(label=Z blocks)")
        
        if abs(Player.dist_to_block(self.z) - zb) > 1e-5:
            self.add_output_with_label("Warning", "encountered inertia on Z while optimizing!", "warning")
    
    def xbwmm(self, xmm: float, sequence: str, /):
        "Attempts to find the speed such that executing `sequence` results in using `xmm` blocks of momentum on the X axis. A warning is raised if the simulation using the calculated speed doesn't match `xmm`, meaning that inertia was encountered while simulating."
        vx = self.optimize(xmm, None, sequence, Player.mm_to_dist)

        self.simulate(f" x(0) vx({vx}) outvx(label=Vx Needed) {sequence} xmm(label=Xmm Used) ", return_defaults=False)

        if abs(Player.dist_to_mm(self.x) - xmm) > 1e-5:
            self.add_output_with_label("Warning", "encountered inertia on X while optimizing!", "warning")

    def xwall(self, x: float, sequence: str, /):
        "Attempts to find the speed such that executing `sequence` results in a displacement of `x` on the X axis. A warning is raised if the simulation using the calculated speed doesn't match `x`, meaning that inertia was encountered while simulating."
        vx = self.optimize(x, None, sequence)

        self.simulate(f" x(0) vx({vx}) outvx(label=Vx Needed) {sequence} outx(label=X dist)")
        
        if abs(self.x - x) > 1e-5:
            self.add_output_with_label("Warning", "encountered inertia on X while optimizing!", "warning")
    
    def xblocks(self, xb: float, sequence: str, /):
        "Attempts to find the speed such that executing `sequence` results in traversing `xb` blocks on the X axis. A warning is raised if the simulation using the calculated speed doesn't match `xb`, meaning that inertia was encountered while simulating."
        vx = self.optimize(xb, None, sequence, Player.block_to_dist)

        self.simulate(f" x(0) vx({vx}) outvx(label=Vx Needed) {sequence} xb(label=X blocks)")
        
        if abs(Player.dist_to_block(self.x) - xb) > 1e-5:
            self.add_output_with_label("Warning", "encountered inertia on X while optimizing!", "warning")

    # We need to fix nested functions

    def function(self, name: str, *args: str, code: str, docstring: str = ''):
        # `name` has to be checked which will be done later

        name = self.formatted(name)
        # parse args in python-like syntax (arg_name: type_anno = default_val)
        param_regex = r"^([a-zA-Z][a-zA-Z0-9]*)(?:(?:\s*:\s*)([a-z0-9]+))?(?:(?:\s*=\s*)([a-zA-Z0-9]+))?$"
        
        if name in Player.FUNCTIONS.keys():
            raise OverwriteError(f"'{name}' is already a function for {Player.FUNCTIONS[name].__name__}")
        

        arguments = []
        current_arg_kind = inspect.Parameter.POSITIONAL_OR_KEYWORD

        for arg in args:
            arg = arg.strip()
            # print(arg)

            
            if arg == "/" and current_arg_kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                for i in range(len(arguments)):
                    arguments[i] = (arguments[i][0], inspect.Parameter.POSITIONAL_ONLY)
            
            elif arg == "*":
                current_arg_kind = inspect.Parameter.KEYWORD_ONLY
            
            else:
                results = re.findall(param_regex, arg)
                if not results:
                    raise SyntaxError()

                arguments.append((results[0], current_arg_kind))
            
        # these functions are for a custom object instance
        args = ("self",) + args

        # self.simulate() is handled by another python script
        code_string = f"""
def {name}({",".join(args)}):
    '{docstring}'
    l = {{}}

    for x in inspect.signature({name}).parameters.keys():
        x = x.split()
        l[x[0]] = eval(x[0])
    
    self.local_vars |= l

    # print(f'''Function {name} has local vars {{self.local_vars = }}''')
    # print()

    self.simulate('''{code}''', locals = self.local_vars, return_defaults=False)

    self.local_vars = {{a:b for a,b in self.local_vars.items() if a not in l}}

self.local_funcs['{name}'] = {name}
    """
        
        exec(code_string, globals() | {'self': self})
    
    
    def alias(self, func_name: str, *names: str):
        "New alias"
        # check names
        func = Player.FUNCTIONS.get(func_name)
        if func is None:
            func = self.local_funcs.get(func_name)
            if func is None:
                raise NameError(f"function '{func_name}' not found")
            else:
                self.add_alias(func, *names, dictionary=self.local_funcs)

        self.add_alias(func, *names)


    # ALIASES
    # MOVEMENT
    add_alias(walk, "w", "walk")
    add_alias(sprint, "s", "sprint")
    add_alias(walkair, "wa", "walkair")
    add_alias(sprintair, "sa", "sprintair")
    add_alias(walkjump, "wj", "walkjump")
    add_alias(sprintjump, "sj", "sprintjump")
    add_alias(sneak, "sn", "sneak")
    add_alias(sneakair, "sna", "sneakair")
    add_alias(sneakjump, "snj", "sneakjump")
    add_alias(sneaksprint, "sns", "sneaksprint")
    add_alias(sneaksprintair, "snsa", "sneaksprintair")
    add_alias(sneaksprintjump, "snsj", "sneaksprintjump")
    add_alias(sprintstrafejump, "sprintstrafejump", "strafejump", "stfj")
    add_alias(stop, "stopground", "stop", "st")
    add_alias(stopair, "stopair", "sta")
    add_alias(stopjump, "stopjump", "stj")
    add_alias(stopwater, "stopwater", "stwt")
    add_alias(walkwater, "walkwater", "wwt", "water", "wt")
    add_alias(sprintwater, "sprintwater", "swt")
    add_alias(sneakwater, "sneakwater", "snwt")
    add_alias(lava, "lava")
    add_alias(sword, "sword", "sw")
    add_alias(swordair, "swordair", "swa")
    add_alias(swordsneak, "swordsneak", "snsw")
    add_alias(swordsneakair, "swordsneakair", "snswa")
    add_alias(swordwater, "swordwater", "snwt")
    add_alias(swordsneakwater, "swordsneakwater")
    add_alias(swordjump, "swordjump")
    add_alias(swordsneakjump, "swordsneakjump")
    add_alias(web, "web")
    add_alias(sprintweb, "sprintweb", "sweb")
    add_alias(webair, "webair", "weba")
    add_alias(sprintwebair, "sprintwebair", "swebair", "sweba")
    add_alias(webjump, "webjump", "webj")
    add_alias(sprintwebjump, "sprintwebjump", "swebj")
    add_alias(sneakwebjump, "sneakwebjump", "snwebj")
    add_alias(sneakwebjump45, "sneakwebjump45", "snwebj45")
    add_alias(sneakweb, "sneakweb", "snweb")
    add_alias(sneakwebair, "sneakwebair", "snweba")
    add_alias(stopweb, "stopweb", "stweb")
    add_alias(stopwebair, "stopwebair", "stweba")
    add_alias(sneaksprintweb, "sneaksprintweb", "snsweb")
    add_alias(sneaksprintweb45, "sneaksprintweb45", "snsweb45")
    add_alias(sneaksprintwebair, "sneaksprintwebair", "snsweba")
    add_alias(sneaksprintwebair45, "sneaksprintwebair45", "snsweba45")
    add_alias(sneaksprintwebjump, "sneaksprintwebjump", "snswebj")
    add_alias(sneaksprintwebjump45, "sneaksprintwebjump45", "snswebj45")
    
    # WITH 45
    add_alias(walk45, "w45", "walk45")
    add_alias(sprint45, "s45", "sprint45")
    add_alias(walkair45, "wa45", "walkair45")
    add_alias(sprintair45, "sa45", "sprintair45")
    add_alias(walkjump45, "wj45", "walkjump45")
    add_alias(sprintjump45, "sj45", "sprintjump45")
    add_alias(sneak45, "sn45", "sneak45")
    add_alias(sneakair45, "sna45", "sneakair45")
    add_alias(sneakjump45, "snj45", "sneakjump45")
    add_alias(sprintstrafejump45, "sprintstrafejump45", "strafejump45", "stfj45")
    add_alias(sneaksprint45, "sns45", "sneaksprint45")
    add_alias(sneaksprintair45, "snsa45", "sneaksprintair45")
    add_alias(sneaksprintjump45, "snsj45", "sneaksprintjump45")
    add_alias(sprintwater45, "sprintwater45", "swt45")
    add_alias(walkwater45, "walkwater45", "wwt45", "water45", "wt45")
    add_alias(sneakwater45, "sneakwater45", "snwt45")
    add_alias(sword45, "sword45")
    add_alias(swordair45, "swordair45")
    add_alias(swordsneak45, "swordsneak45")
    add_alias(swordsneakair45, "swordsneakair45")
    add_alias(swordwater45, "swordwater45")
    add_alias(swordsneakwater45, "swordsneakwater45")
    add_alias(swordjump45, "swordjump45")
    add_alias(swordsneakjump45, "swordsneakjump45")
    add_alias(web45, "web45")
    add_alias(sprintweb45, "sprintweb45", "sweb45")
    add_alias(webair45, "webair45", "weba45")
    add_alias(sprintwebair45, "sprintwebair45", "swebair45", "sweba45")
    add_alias(webjump45, "webjump45", "webj45")
    add_alias(sprintwebjump45, "sprintwebjump45", "swebj45")
    add_alias(sneakweb45, "sneakweb45", "snweb45")
    add_alias(sneakwebair45, "sneakwebair45", "snweba45")

    # RETURNERS
    add_alias(outz, "outz")
    add_alias(zmm, "zmm")
    add_alias(zb, "zb")
    add_alias(outvz, "outvz")
    add_alias(outx, "outx")
    add_alias(xmm, "xmm")
    add_alias(xb, "xb")
    add_alias(outvx, "outvx")
    add_alias(vec, "vec")
    add_alias(outangle, "outangle", "outa", "outfacing", "outf")
    add_alias(outturn, "outturn", "outt")
    add_alias(effectsmultiplier, "effectsmultiplier", "effects")
    add_alias(printdisplay, "print", "printdisplay")

    # SETTERS
    add_alias(face, "f", "face", "facing")
    add_alias(turn, "turn")
    add_alias(setposz, "setposz", "z")
    add_alias(setvz, "setvz", "vz")
    add_alias(setposx, "setposx", "x")
    add_alias(setvx, "setvx", "vx")
    add_alias(setslip, "setslip", "slip")
    add_alias(setprecision, "setprecision", "precision", "pre")
    add_alias(inertia, "inertia")
    add_alias(sprintairdelay, "sprintairdelay", "sdel")
    add_alias(sneakdelay, "sneakdelay", "sndel")
    add_alias(singleaxisinertia, "singleaxisinertia", "sai")
    add_alias(version, "version", "v")
    add_alias(speed, "speed")
    add_alias(slowness, "slowness", "slow")
    add_alias(var, "var")
    add_alias(function, "function", "func")
    add_alias(alias, "alias")
    # add_alias(toggle, "toggle") # broken

    add_alias(anglequeue, "anglequeue", "aq")
    add_alias(turnqueue, "turnqueue", "tq")

    add_alias(repeat, "repeat", "r")
    add_alias(possibilities, "possibilities", "poss")
    add_alias(xpossibilities, "xpossibilities", "xposs")
    add_alias(xzpossibilities, "xzpossibilities", "xzposs")
    

    add_alias(ballhelp, "help", "ballhelp")
    
    add_alias(dimensions, "dimensions", "dim")
    # Fix this for displaying (multilines)

    # OPTIMIZERS
    add_alias(bwmm, "bwmm")
    add_alias(xbwmm, "xbwmm")
    add_alias(wall, "wall", "inv")
    add_alias(xwall, "xwall", "xinv")
    add_alias(blocks, "blocks")
    add_alias(xblocks, "xblocks")

    def get_suggestions(self, string: str):
        """
        Given `string`, return a list of suggestions from all possible mothball commands that best matches `string`.

        For example, if `wtrsprint` was inputted, a possible suggestion is `sprintwater`.
        """
        
        matches_start = []
        matches_part = [] # If string in word
        matches_char_count = {}

        for command in Player.FUNCTIONS.keys():
            # 1. Matches start
            if command.startswith(string):
                matches_start.append(command)
            elif string in command:
                matches_part.append(command)
            else:
                cmd_count = Counter(command)
                str_count = Counter(string)

                off_by = 0
                for char, count in str_count.items():
                    try:
                        if count == cmd_count[char]:
                            off_by -= 1
                        else:
                            off_by += count - cmd_count[char]
                    except KeyError: # not a character
                        off_by += 1
                off_by += abs(len(command) - len(string))
                if off_by < len(command): matches_char_count[command] = off_by

                
                
        # pp(matches_char_count)
        matches_char_count = sorted(matches_char_count, key=lambda e: matches_char_count[e])

        return matches_start + matches_part + matches_char_count
    
    def remove_comments(self, string: str):
        "Removes comments delimited by `#`"
        result = ""
        in_comment = False
        follows_slash = False

        for char in string:
            if char == "#" and not follows_slash:
                in_comment = not in_comment
                continue

            if not in_comment:
                result += char

            if char == "\\" and not follows_slash:
                follows_slash = True
                
            
            else:
                follows_slash = False
        
        return result

    def parse(self, string: str, splitters: tuple = ("\n", " ", "\r", "\t")) -> list: 
        """
        Splits the string at any of the splitters that are outside of parenthesis. By default, it splits at any whitespace. 
        
        Returns a list of strings (or tokens), raises `SyntaxError` if parenthesis are unmatched.

        ```py
        >> tokens = Player.parse(\"walk(1) sprintjump.wa(2, 5) sprintair(10)\")
        >> tokens
        [\"walk(1)\", \"sprintjump.wa(2, 5)\", \"sprintair(10)\"]
        ```

        Comments are delimited by the `#` symbol. Anything between comments will be ignored.

        ```py
        >> tokens = Player.parse(
        \"\"\"walkjump(1) 
        # this is a comment # 
        sprintair(11) sprint 
        # and this is another comment\"\"\"
        )
        >> tokens
        [\"walkjump(1)\", \"sprintair(11)\", \"sprint\"]
        ```
        """

        result = []
        depth = 0
        token = ""
        
        follows_slash = False
        follows_comma = False

        # Delete comments
        string = self.remove_comments(string)

        # Regex to change '|' into 'x(0) z(0)'
        replace_bar_regex = r"(\|)"
        string = re.sub(replace_bar_regex, "x(0) z(0)", string)

        
        for char in string + splitters[0]:

            if char == "\\":
                follows_slash = True
                token += char
                continue
            # elif char == ",":
            #     if follows_comma:
            #         raise SyntaxError("Expected expression")
            #     follows_comma = True
            #     continue

            elif char == "(" and not follows_slash:
                depth += 1
            elif char == ")" and not follows_slash:
                depth -= 1

                if depth < 0:
                    raise SyntaxError("Unmatched closing parethesis")
            

            if char in splitters and depth == 0 and not follows_slash:
                token = token.strip()
                result.append(token) if token else None
                token = ""

            else:
                token += char

            follows_slash = False
            follows_comma = False
        
        if depth:
            raise SyntaxError("Unmatched open parethesis")

        # print(f"{string=} gave {result=}")
        return result
    
    def tokenize(self, string: str, locals: dict = None) -> dict:
        """
        Tokenizes the string to a dictionary containing the function, positional arguments, and keyword arguments of appropiate types. 
        
        Returns as a dictionary in the form
        ```py
        {"function": function, "inputs": str, "args": list, "kwargs": dict}
        ```

        where `inputs` is a string which will be used as a function modifier. 

        Raises `SyntaxError` if a positional argument follows a keyword argument. \\
        Raises `TypeError` if these functions: (`stop`, `stopair`, `stopjump`, and 45 movement) recieves an input.
        Raises any other error encountered while converting datatypes.
        """

        tokenize_regex = r'(\W)?([^.\(\-)]+)(?:\.([^\(\.]+))?(?:\((.*)\))?(.+)?'
        # tokenize_regex = r'([^.\(\-)]+)(?:\.([^\(\.]+))?(?:\((.*)\))?(.+)?'


        # func: ([^.\(\-)]+)
        # inputs: (?:\.([^\(]+))?
        # args: (?:\((.*)\))?
        # error: (.+)?

        error, func_name, inputs, args, error2 = re.findall(tokenize_regex, string, flags=re.DOTALL)[0]
        # print(f"result: {func_name} {inputs} {args} {error2}")

        if error and error != "-":
            
            raise SyntaxError(f"Unknown item {error} in {string}")
        elif error2:
            raise SyntaxError(f"Unknown item {error2} in {string}")
        
        if string[0] == "-":
            self.reverse = True
        else:
            self.reverse = False


        func = Player.FUNCTIONS.get(func_name)
        if func is None:
            func = self.local_funcs.get(func_name) # CHANGES
            if func is None:
                error_msg = f"{func_name} is not a valid function. "
                suggestions = self.get_suggestions(func_name)
                
                if suggestions:
                    suggestions = suggestions[0:min(4, len(suggestions))]
                    error_msg += f"Did you mean {', '.join(suggestions)}?"

                raise NameError(error_msg)

        
        positional_args = []
        keyword_args = {}

        # TEST TEST TEST!!!!!! -> removes "None" from the args
        args = self.parse(args, splitters=",")
        # args = [x for x in self.parse(args, splitters=",") if x not in [None, "None"]]
        
        
        keyword_regex = r"^\s*?(\w+)\s*=\s*(.+)\s*$"
        after_keyword = False

        for arg in args:
            result = re.findall(keyword_regex, arg, flags=re.DOTALL)

            if result: # keyword
                key,value = result[0]
                if key in keyword_args:
                    raise SyntaxError(f"Repeated keyword argument {key}")

                keyword_args[key.strip()] = value.strip()
                after_keyword = True
            else: # positional
                if after_keyword:
                    raise SyntaxError("Positional argument cannot follow keyword arguments")
                
                positional_args.append(arg)
        
        positional_args, keyword_args = self.check_types(func, positional_args, keyword_args, locals=locals)

        if func.__name__ not in Player._can_have_input:
            if inputs:
                raise TypeError(f"{func.__name__}() cannot be modified by an input")
            if func.__name__ in Player._fortyfive_methods:
                inputs = "w"

        elif not inputs:
            inputs = "w"
        elif inputs not in ["w","wa","wd", "s", "sa", "sd", "a", "d"]:
            raise ValueError(f"function {func_name} received bad input '{inputs}', it can only be w, s, a, d, wa, wd, sa, wd.")

        return {"function": func, "inputs": inputs, "args": positional_args, "kwargs": keyword_args}
    
    def check_types(self, func, args: list, kwargs: dict, locals = None):
        """
        Type checks each argument in `args` and `kwargs` according to the  annotations in `func`. If successful, returns a list of positional args and a dict of keyword args.

        Raises any appropiate error encountered while converting strings to the necessary datatypes.
        """
        if locals is None:
            locals = self.local_vars

        converted_args = []
        converted_kwargs = {}

        signature = inspect.signature(func).parameters.values()

        positional_only = {x.name:x.annotation for x in signature if x.kind == inspect.Parameter.POSITIONAL_ONLY and x.name != "self"}
        # print(positional_only)
        positional_or_keyword = {x.name:x.annotation for x in signature if x.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and x.name != "self"}
        keyword_only = {x.name:x.annotation for x in signature if x.kind == inspect.Parameter.KEYWORD_ONLY}
        var_positional = {x.name:x.annotation for x in signature if x.kind == inspect.Parameter.VAR_POSITIONAL}

        # Watch out for potential errors
        required_positionals = {x.name:x.annotation for x in signature if x.kind == inspect.Parameter.POSITIONAL_ONLY and x.default == inspect.Parameter.empty and x.name != "self"}

        # Idea: First check the positional arguments using positional_only and positional_or_keyword. 
        # Once positional_only runs out, start using positional_or_keyword.
        # Once both runs out, use var_positional
        # Raise error if there's too many positional arguments (var_positional is empty)

        ### Check the positional arguments ###
        can_be_positional = positional_only | positional_or_keyword
        # print(can_be_positional)

        if len(required_positionals) > len(args):
            number_of_missing = len(required_positionals) - len(args)
            raise TypeError(f"{func.__name__} missing {number_of_missing} positional-only argument{'s' if number_of_missing > 1 else ''}: {', '.join(list(required_positionals)[len(args):])}")

        for i in range(min(len(args), len(can_be_positional))):

            # RISKY RISKY RISKY RISKY RISKY
            datatype = list(can_be_positional.values())[i]
            if datatype == inspect.Parameter.empty:
                datatype = str

            converted_value = self.safe_eval(args[i], datatype, locals)

            if list(can_be_positional)[i] == "duration" and func.__name__ not in self.local_funcs:
                if converted_value is not None and converted_value < 0:
                    raise ValueError(f"Positional argument 'duration' should be a non-negative integer")
                elif converted_value is None:
                    converted_value = 1
            elif list(can_be_positional)[i] == "label":

                if converted_value is None:
                    converted_value = func.__name__


            converted_args.append(converted_value)
        
        # print(args, can_be_positional)
        if len(args) < len(can_be_positional):
            a = len(args) - len(can_be_positional)
            can_be_positional = {x:can_be_positional[x] for x in list(can_be_positional)[a:]}
        
        elif var_positional and len(args) > len(can_be_positional):
            for j in args[len(can_be_positional):]:
                c = self.safe_eval(j, list(var_positional.values())[0], locals)
                converted_args.append(c)
                # print(converted_args)
        
        elif not var_positional and len(args) > len(can_be_positional):
            raise TypeError(f"{func.__name__} accepts at most {len(can_be_positional)} positional arguments, got {len(args)} instead")
        
        can_be_keyword = can_be_positional | keyword_only

        ### Check the keyword args ###
        for kw, value in kwargs.items():
            datatype = can_be_keyword.get(kw)

            # print(kw, datatype)

            if datatype is None:
                raise TypeError(f"{func.__name__} has no keyword argument '{kw}'")
            
            elif datatype in [int, float, f32]:
                converted_kwargs[kw] = self.safe_eval(value, datatype, locals)
            else:
                # if kw == "label": # is this even needed
                #     if value is None:
                #         value = func.__name__

                converted_kwargs[kw] = datatype(value)
                
        
        return converted_args, converted_kwargs
        
    def run(self, token):
        """
        Runs the token.

        `token` is a dictionary in the form
        ```py
        {"function": function, "inputs": str, "args": list, "kwargs": dict}
        ```
        
        where `inputs` is a string which will be used as a function modifier.
        """

        func = token["function"]
        self.inputs = token["inputs"]
        args = token["args"]
        kwargs = token["kwargs"]

        func(self, *args, **kwargs)
    
    def simulate(self, sequence: str, return_defaults = True, locals: dict = None):

        parsed_tokens = self.parse(sequence)

        # print(parsed_tokens)

        for token in parsed_tokens:
            runnable = self.tokenize(token, locals=locals)
            # pp(runnable)
            self.run(runnable)

        
        if return_defaults and not self.output:
            self.add_output_with_label("Z", self.z, "z-expr")
            self.add_output_with_label("VZ", self.vz, "z-expr")
            self.add_output_with_label("X", self.x, "x-expr")
            self.add_output_with_label("VX", self.vx, "x-expr")
    
    def show_output(self):
        for tup in self.output:
            print(tup[0])
    
    def mcsin(self, rad):
        if self.total_angles == -1:
            return sin(rad)
        elif self.total_angles == 65536:
            index = int(rad * f32(10430.378)) & 65535
        else:
            index = int(1 / (2 * Player.pi) * self.total_angles * rad) & (self.total_angles - 1)
        return f32(sin(index * self.pi * 2.0 / self.total_angles))

    def mccos(self, rad):
        if self.total_angles == -1:
            return cos(rad)
        elif self.total_angles == 65536:
            index = int(rad * f32(10430.378) + f32(16384.0)) & 65535
        else:
            index = int(1 / (2 * Player.pi) * self.total_angles * rad + self.total_angles / 4) & (self.total_angles - 1)
        return f32(sin(index * self.pi * 2.0 / self.total_angles))


    ## TEST ZONE
    # def sneaktap(self, count: int = 1, duration: int = 1):
    #     for i in range(count):
    #         self.simulate(f"sn{f'.{self.inputs}' if self.inputs else ''}({duration})", return_defaults=False)
    #         while self.vz != 0 or self.vx != 0:
    #             self.simulate("st", return_defaults=False)

    # _can_have_input.append("sneaktap")
    # add_alias(sneaktap, "snt")

if __name__ == "__main__":
    a = Player()

    # a.simulate("snt(1,1) s(5) outz(1-2*px)") # equivalent to sn st(10) s(5) ... (top secret test)
    # a.show_output()
