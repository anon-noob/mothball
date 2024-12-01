from math import copysign
from inspect import signature
from functools import wraps
from types import MethodType
from inspect import cleandoc
from copy import copy
from numpy import float32, int32, uint64
from evalidate import Expr, EvalException
import cogs.movement.parsers as parsers
from cogs.movement.utils import Function, SimError, fastmath_sin_table
import re
from cogs.movement.playerY import PlayerY
from cogs.movement.context import Context # for type hinting

f64 = float
f32 = float32
i32 = int32
u64 = uint64
PI = 3.14159265358979323846

commands_by_name = {}
types_by_command = {}
aliases = {}
types_by_arg = {}

def register_arg(arg, type, new_aliases = []):
    types_by_arg[arg] = type
    for alias in new_aliases:
        aliases[alias] = arg

register_arg('duration', int, ['dur', 't'])
register_arg('airborne', bool, ['air'])
register_arg('sneaking', bool, ['sneak', 'sn'])
register_arg('jumping', bool, ['jump'])
register_arg('water', bool, ['water'])
register_arg('web', bool, ['web']) # for web movement
register_arg('slime', bool, ['slime']) # for slime bounces
register_arg('jump_boost', int, ['jump_boost'])

def command(name=None, aliases=[]):
    def deco(f):
        nonlocal name, aliases

        @wraps(f)
        def wrapper(context):
            args_list = []

            for param, default_val in f._defaults.items():
                if default_val is not None: # Avoid setting a potentially bad default
                    context.args.setdefault(param, default_val)
                args_list.append(context.args.get(param))
    
            return f(context, *args_list)

        params = signature(wrapper).parameters
        defaults = []
        arg_types = []
        for k, v in list(params.items())[1:]:
            defaults.append((k, v.default))
            arg_types.append((k, v.annotation if v.default is None else type(v.default)))
        f._defaults = dict(defaults)
        types_by_command[wrapper] = dict(arg_types)
        
        if name is None:
            name = wrapper.__name__
        commands_by_name[name] = wrapper
        wrapper._aliases = [name] + aliases
        for alias in aliases:
            commands_by_name[alias] = wrapper
        
        return wrapper
    return deco


def move(ctx: Context):
    for _ in range(abs(ctx.args['duration'])):
        ctx.player.move(ctx)

def jump_helper(ctx: Context, after_jump_tick = lambda: None):
    if ctx.args['duration'] > 0:
        ctx.args['jumping'] = True
    ctx.player.move(ctx)
    ctx.args['jumping'] = False

    after_jump_tick()
    
    ctx.args.setdefault('airborne', True)
    for i in range(abs(ctx.args['duration']) - 1):
        ctx.player.move(ctx)


def get_local_env(ctx: Context):
    local_env = {}
    for env in ctx.envs:
        local_env.update(env)
    return local_env 

def colorize_number(number, remove_negative = False):
    if float(number) < 0: # negative (red)
        return f'[0m{"-" if not remove_negative else ""}[31m{number[1:]}'
    else: # positive (green)
        return f'[32m{number}'

def add_to_pre_output_as_normal_string(ctx: Context, string = ''):
    """
    Handles adding to the pre outout (`ctx.pre_out`) which is anything that should be displayed first on top before standard output.
    """
    ctx.adding_pre_output = False
    ctx.pre_out += string + '\n'

    # For noncolored pre output as backup
    ctx.uncolored_pre_out += f"{string}\n"

def add_to_pre_output(ctx: Context, label = None, string = '', label_color = "cyan"):
    label_colors = {
        "gray": 30,
        "yellow": 33,
        "blue": 34,
        "pink": 35,
        "cyan": 36,
        "white": 0
    }

    # For noncolored pre output as backup
    ctx.uncolored_pre_out += f"{label}: {string}\n"

    output = ""
    if ctx.adding_pre_output == False:
        output += "```ansi\n"
        ctx.adding_pre_output = True
    
    elif ctx.adding_pre_output == True and ctx.pre_out.endswith("\n```"):
        ctx.pre_out = ctx.pre_out.removesuffix("```")

    string = string.split("/")
    output += f"[{label_colors[label_color]}m{label}[0m: {'[0m/'.join([colorize_number(x) for x in string])}"
        
    ctx.pre_out += output + '\n```'


def add_to_output(ctx: Context, label = None, string = '', label_color = "cyan", mode="number"):
    """
    Handles adding to the standard output (`ctx.out`) to display (For coloring purposes)
    
    Given a label and string, the output will be colored and presented as `label: string`.
    """

    # TODO: PLEASE REFACTOR THIS SHIT

    label_colors = {
        "gray": 30,
        "yellow": 33,
        "blue": 34,
        "pink": 35,
        "cyan": 36,
        "white": 0
    }

    output = ""
    if ctx.adding_output == False:
        output += "```ansi\n"
        ctx.adding_output = True
 
    elif ctx.adding_output == True and ctx.out.endswith("\n```"):
        ctx.out = ctx.out.removesuffix("```")

    if mode == "number":
        nums_and_signs = string.split(" ")
        output += f"[{label_colors[label_color]}m{label}[0m: "

        if len(nums_and_signs) == 1: # one single number
            output += f"{colorize_number(nums_and_signs[0])}"
        
        elif len(nums_and_signs) == 3: # num1 + num2
            num1, sign, num2 = nums_and_signs
            output += f"{colorize_number(num1)} [0m{sign} {colorize_number('-' + num2 if sign == '-' else num2, remove_negative=True)}"

    else:
        output += f"[{label_colors[label_color]}m{label}[0m: "
        output += string    
    ctx.out += output + "\n```"

    # For noncolored output as backup
    ctx.uncolored_out += f"{label}: {string}\n"

def add_to_output_as_normal_string(ctx: Context, string = ''):
    "Handles adding to the standard output (`ctx.out`) to display as normal text."
    ctx.adding_output = False
    ctx.out += string + "\n"

    # For noncolored output as backup
    ctx.uncolored_out += f"{string}\n"

def zeroed_formatter(ctx: Context, num, zero):
    if zero is None or zero == 0:
        return ctx.format(num)
    
    formatted_offset = ctx.format(num - zero, sign=True)
    if any([formatted_offset.startswith(s) for s in ('+', '-')]):
        formatted_offset = f'{formatted_offset[0:1]} {formatted_offset[1:]}'
    else:
        formatted_offset = f'? {formatted_offset}'
    
    # print(f"NUMBER {num} -> FORMAT RESULTS {f'{ctx.format(zero)} {formatted_offset}'}")
    return f'{ctx.format(zero)} {formatted_offset}'

@command(aliases=['rep', 'r'])
def repeat(ctx: Context, inputs: str = '', n: int = 1):
    "Executes `inputs` `n` times"
    if ("print" in inputs or "println" in inputs) and n > 100:
        raise SimError(f"Looks like you're trying to do some heavy duty printing. Unfortunately we are low on electrons, so until then, we can't print this many times.")
    commands_args = parsers.string_to_args(inputs)

    for _ in range(n):
        for command, cmd_args in commands_args:
            parsers.execute_command(ctx, command, cmd_args)

@command(aliases=['def'])
def define(ctx: Context, name = '', input = ''):

    dictized = parsers.string_to_args(input)
    new_function = Function(name, dictized, ctx.pos_args[2:])

    lowest_env = ctx.envs[-1]
    lowest_env[name] = new_function

@command()
def var(ctx: Context, name = '', input = ''):
    """
    Assigns `input` to `name`
    
    A valid variable `name` is any sequence of alphabet letters a-z or A-Z, numerical digits (0-9), an underscore `_`, and any combination of them with only one restriction. \\
    A number cannot be the first character in the variable name.

    `var()` will attempt to convert the value to the appropiate datatype, which only supports integers, floats, or strings
    """
    var_regex = r"^([a-zA-Z_][a-zA-Z0-9_]*)$"
    if not re.findall(var_regex, name): # Either has one match or no matches
        raise SyntaxError(f"'{name}' is not a valid variable name")

    lowest_env = ctx.envs[-1]
    
    local_env = {}
    for env in ctx.envs:
        local_env.update(env)

    try:
        input = parsers.safe_eval(input, local_env)
    except:
        input = parsers.formatted(local_env, input)

    lowest_env[name] = input

@command(aliases=['j'])
def jump(ctx: Context, duration: int = 1, jump_boost: int = 0):
    """
    Jump up with (or without) jump boost. This will RESET your y position to 0.
    
    THIS IS STILL UNDER DEVELOPMENT and is subject to change. As this calculates the player position in the same order that it normally does, if you want to jump from a certain jump height, you would have to set the y value 1 tick after the jump. 
    
    For example, to jump starting from `y = 0.125`, you would write `jump y(0.125) air(11) ...`
    """
    ctx.player.y = 0.0
    ctx.player.vy = 0.0
    ctx.args.setdefault("jump_boost", jump_boost)
    jump_helper(ctx)

@command(aliases=['a'])
def air(ctx: Context, duration: int = 1):
    """
    The player is falling down.
    """
    ctx.args.setdefault("airborne", True)
    move(ctx)

@command()
def outy(ctx: Context, zero: f64 = None, label: str = "Y"):
    """
    Output's the player's y position.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    `zero` will also be truncated by the current decimal precision.
    """
    add_to_output(ctx, label, zeroed_formatter(ctx, ctx.player.y, zero))

@command(aliases=['outty'])
def outtopy(ctx: Context, zero: f64 = None, label: str = "Y"):
    """
    Output's the player height's y position.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    `zero` will also be truncated by the current decimal precision.
    """
    add_to_output(ctx, label,  zeroed_formatter(ctx, ctx.player.y + 1.8, zero))

@command()
def outvy(ctx: Context, zero: f64 = None, label: str = "Vy"):
    """Outputs the player's y velocity

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    `zero` will also be truncated by the current decimal precision.
    """
    add_to_output(ctx, label, zeroed_formatter(ctx, ctx.player.vy, zero))

@command(aliases=['sety', 'y'])
def setposy(ctx: Context, y = 0.0):
    "Set's the player's y position"
    ctx.player.y = y

@command(aliases=['setty', 'topy', 'ty'])
def setpostopy(ctx: Context, y = 0.0):
    "Set's the player height's y position, equivalent to `setposy(y - 1.8)`"
    ctx.player.y = y - 1.8

@command(aliases=['vy'])
def setvy(ctx: Context, vy = 0.0):
    "Set's the player's y velocity"
    ctx.player.vy = vy

@command(aliases=['ceiling', 'ceil'])
def setceiling(ctx: Context, ceiling: int = None):
    "Set's the ceiling for the simulation"
    ctx.player.ceiling = ceiling

@command(aliases=['bounce'])
def slime(ctx: Context, height: f64 = 0.0):
    """
    Bounce on a slime, continuing the simulation with a height of `height`.
    
    For example, if you are bouncing on a slime with a trapdoor on top, you would use `slime(0.1875)`
    """
    ctx.args.setdefault('duration', 1)
    ctx.args.setdefault('slime', True)
    move(ctx)
    ctx.player.y = height

@command(aliases=['webj'])
def webjump(ctx: Context, duration: int = 1, jump_boost: int = 0):
    "Jump while inside a web. This will RESET your y position to 0. Do `help(jump)` for more information."
    ctx.player.y = 0.0
    ctx.player.vy = 0.0
    ctx.args.setdefault("web", True)
    ctx.args.setdefault('jump_boost', jump_boost)
    jump_helper(ctx, after_jump_tick=lambda: ctx.args.setdefault("airborne", True))

@command(aliases=['weba'])
def webair(ctx: Context, duration: int = 1):
    "Falling down while inside a web"
    ctx.args.setdefault("web", True)
    ctx.args.setdefault("airborne", True)
    move(ctx)

@command(aliases=['jb'])
def jump_boost(ctx: Context, amplifier: int = 0):
    "Sets the jump boost potion effect for the simulation"
    ctx.player.jump_boost = amplifier

@command(aliases=['print'])
def println(ctx: Context, string: str = ""):
    """
    Print any basic text to your heart's desire. To print commas, place a \ before the comma.

    Example: print(Then if a player that can do a cheat but cannot be proven\, then he is not a cheater. - Sun Tzu\, The Art of Macroing)
    
    Pings and links will not print.
    """
    add_to_output_as_normal_string(ctx, string)

@command()
def help(ctx: Context, cmd_name = 'help'):
    """
    Get help with a function by displaying it's name, aliases, arguments, and defaults.
    arg_name: data_type = default_value

    Example: help(help) help(j) help(slime)
    """

    if cmd_name not in commands_by_name:
        raise SimError(f'Command `{cmd_name}` not found.')

    cmd = commands_by_name[cmd_name]
    cmd_name = cmd._aliases[0]
    params = []
    for k, v in list(signature(cmd).parameters.items())[1:]:
        out = '  '
        out += k
        anno_type = v.annotation if v.default is None else type(v.default)
        out += f': {anno_type.__name__}'
        out += ' = ' + (str(v.default) if anno_type != str else f'"{v.default}"')
        params.append(out)
    newln = '\n'

    help_output = f'Help with {cmd_name}:'
    help_output += '' if cmd.__doc__ is None else f'\n```{cleandoc(cmd.__doc__)}```'
    help_output += f'```\nAliases:\n{newln.join(map(lambda x: "  "+x, cmd._aliases))}'
    help_output += f'\nArgs:\n{newln.join(params)}```\n'

    add_to_output_as_normal_string(ctx, string=help_output)

@command(aliases = ['poss'])
def possibilities(ctx: Context, inputs = 'j(12)'):
    """
    (NAME OF FUNCTION MIGHT BE CHANGED)
    
    Displays the y position at each tick, and displays a range of y values that match the tier.

    For example, the 12th tick of a jump on flat ground would display `Tick 12: 0.10408 (0.0625 to -0.3125)`, indicating the range of y values that would result in a tier 0 (airtime 12) jump.
    """
    old_move = ctx.player.move

    tick = 1
    def move(self, ctx: Context):
        nonlocal tick, old_move

        old_move(ctx)

        if ctx.player.vy < 0:
            
            top_diff = self.y % 0.0625
            top = self.y - top_diff
            botdiff = (self.y + self.vy) % 0.0625
            bot = self.y + self.vy - botdiff + 0.0625
            # bot = self.y + self.vy - botdiff

            # add_to_output(ctx, f"Tick {tick}", f"{zeroed_formatter(ctx, self.y, 0)} ({zeroed_formatter(ctx, top, 0)} to {zeroed_formatter(ctx, bot, 0)})")
            add_to_output(ctx, f"Tick {tick}", f"{ctx.format(self.y)} ({top} to {bot})", mode = "normal")

        
        tick += 1
    
    ctx.player.move = MethodType(move, ctx.player)
    ctx.uncolored_out += '```'
    
    commands_args = parsers.string_to_args(inputs)
    for command, cmd_args in commands_args:
        parsers.execute_command(ctx, command, cmd_args)
    
    ctx.uncolored_out += '```'
    ctx.player.move = old_move
