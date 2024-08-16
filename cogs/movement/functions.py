from math import atan2, degrees, radians, sqrt, copysign, atan, asin, acos, sin, cos
from inspect import signature
from functools import wraps
from types import MethodType
from inspect import cleandoc
from copy import copy
from numpy import float32, int32, uint64
from evalidate import Expr, EvalException
import cogs.movement.parsers as parsers
from cogs.movement.utils import Function, SimError, fastmath_sin_table
from cogs.movement.player import Player

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
register_arg('rotation', f32, ['rot', 'r'])
register_arg('forward', f32)
register_arg('strafe', f32)
register_arg('slip', f32, ['s'])
register_arg('airborne', bool, ['air'])
register_arg('sprinting', bool, ['sprint'])
register_arg('sneaking', bool, ['sneak', 'sn'])
register_arg('jumping', bool, ['jump'])
register_arg('water', bool, ['water']) # (New) Added water
register_arg('speed', int, ['spd'])
register_arg('slowness', int, ['slow', 'sl'])
register_arg('soulsand', int, ['ss'])

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


def move(ctx):
    for _ in range(abs(ctx.args['duration'])):
        ctx.player.move(ctx)

def jump(ctx, after_jump_tick = lambda: None):
    
    ctx.args['jumping'] = True
    ctx.player.move(ctx)
    ctx.args['jumping'] = False

    after_jump_tick()
    
    ctx.args.setdefault('airborne', True)
    for i in range(abs(ctx.args['duration']) - 1):
        ctx.player.move(ctx)


dist_to_dist = lambda dist: dist
dist_to_mm   = lambda dist: dist - f32(copysign(0.6, dist))
dist_to_b    = lambda dist: dist + f32(copysign(0.6, dist))
mm_to_dist   = dist_to_b
b_to_dist    = dist_to_mm


@command(aliases=['rep', 'r'])
def repeat(ctx, inputs = '', n = 1):
    "Executes `inputs` `n` times"
    commands_args = parsers.string_to_args(inputs)

    for _ in range(n):
        for command, cmd_args in commands_args:
            parsers.execute_command(ctx, command, cmd_args)

@command(aliases=['def'])
def define(ctx, name = '', input = ''):

    dictized = parsers.string_to_args(input)
    new_function = Function(name, dictized, ctx.pos_args[2:])

    lowest_env = ctx.envs[-1]
    lowest_env[name] = new_function

@command()
def var(ctx, name = '', input = ''):
    lowest_env = ctx.envs[-1]
    try:
        local_env = {}
        for env in ctx.envs:
            local_env.update(env)
        input = parsers.safe_eval(input, local_dict=local_env)
    except:
        pass
    lowest_env[name] = input


@command(aliases=['sn'])
def sneak(ctx, duration = 1, rotation: f32 = None):
    "Sneak on ground"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    move(ctx)

@command(aliases=['sns'])
def sneaksprint(ctx, duration = 1, rotation: f32 = None):
    """
    Sneak and sprint on ground.

    NOTE: Only works for versions 1.14+. To sneak and sprint, the player must be sprinting on the tick before they sneak.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['w'])
def walk(ctx, duration = 1, rotation: f32 = None):
    "Walk on the ground"
    ctx.args.setdefault('forward', f32(1))
    move(ctx)

@command(aliases=['s'])
def sprint(ctx, duration = 1, rotation: f32 = None):
    "Running on the ground"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['sn45'])
def sneak45(ctx, duration = 1, rotation: f32 = None):
    "Sneaking while 45 strafing"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    move(ctx)

@command(aliases=['sns45'])
def sneaksprint45(ctx, duration = 1, rotation: f32 = None):
    """
    Sneak, sprint, and 45 strafe on ground.

    NOTE: Only works for versions 1.14+. To sneak and sprint, the player must be sprinting on the tick before they sneak.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    move(ctx)

@command(aliases=['w45'])
def walk45(ctx, duration = 1, rotation: f32 = None):
    "Walk and 45 strafe on ground"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    move(ctx)

@command(aliases=['s45'])
def sprint45(ctx, duration = 1, rotation: f32 = None):
    "Run and 45 strafe on ground"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    move(ctx)

@command(aliases=['sna'])
def sneakair(ctx, duration = 1, rotation: f32 = None):
    "Sneak while midair. In 1.20+, activating sneak is delayed for 1 tick."
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['snsa'])
def sneaksprintair(ctx, duration = 1, rotation: f32 = None):
    """
    Sneak and sprint while midair.

    NOTES: Only works for versions 1.14+. To sneak and sprint, the player must be sprinting on the tick before they sneak.

    Sprinting in midair is delayed by 1 tick for versions below 1.20.
    
    Additionally, sneak activation is delayed by 1 tick in 1.20+.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['wa'])
def walkair(ctx, duration = 1, rotation: f32 = None):
    "Move midair without sprint"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['sa'])
def sprintair(ctx, duration = 1, rotation: f32 = None):
    "Move midair with sprint."
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['sneakair45', 'sn45a', 'sna45'])
def sneak45air(ctx, duration = 1, rotation: f32 = None):
    "Sneak and 45 strafe while midair"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['sneaksprintair45', 'sns45a', 'snsa45'])
def sneaksprint45air(ctx, duration = 1, rotation: f32 = None):
    """
    Sneak, sprint, and 45 while midair.

    NOTES: Only works for versions 1.14+. To sneak and sprint, the player must be sprinting on the tick before they sneak.

    Sprinting in midair is delayed by 1 tick for versions below 1.20.
    
    Additionally, sneak activation is delayed by 1 tick in 1.20+.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('sprinting', True)
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['walkair45', 'w45a', 'wa45'])
def walk45air(ctx, duration = 1, rotation: f32 = None):
    "45 strafe midair without sprint"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['sprintair45', 's45a', 'sa45'])
def sprint45air(ctx, duration = 1, rotation: f32 = None):
    """
    45 strafe midair with sprint
    
    Note that activating sprint midair is 1 tick delayed for versions below 1.20.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['snj'])
def sneakjump(ctx, duration = 1, rotation: f32 = None):
    "Jump while sneaking"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    jump(ctx)

@command(aliases=['snsj'])
def sneaksprintjump(ctx, duration = 1, rotation: f32 = None):
    """
    Jump while sneaking and sprinting
    
    Only works for versions 1.14+. To sneak and sprint, the player must be sprinting on the tick before they sneak.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('sprinting', True)
    jump(ctx)

@command(aliases=['wj'])
def walkjump(ctx, duration = 1, rotation: f32 = None):
    "Jump without sprint"
    ctx.args.setdefault('forward', f32(1))
    jump(ctx)

@command(aliases=['lwj'])
def lwalkjump(ctx, duration = 1, rotation: f32 = None):
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))

    def update():
        ctx.args['strafe'] = f32(0)

    jump(ctx, after_jump_tick = update)

@command(aliases=['rwj'])
def rwalkjump(ctx, duration = 1, rotation: f32 = None):
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(-1))

    def update():
        ctx.args['strafe'] = f32(0)

    jump(ctx, after_jump_tick = update)

@command(aliases=['sj'])
def sprintjump(ctx, duration = 1, rotation: f32 = None):
    "Jump with sprint"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sprinting', True)
    jump(ctx)

@command(aliases=['lsj'])
def lsprintjump(ctx, duration = 1, rotation: f32 = None):
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('sprinting', True)

    def update():
        ctx.args['strafe'] = f32(0)

    jump(ctx, after_jump_tick = update)

@command(aliases=['rsj'])
def rsprintjump(ctx, duration = 1, rotation: f32 = None):
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(-1))
    ctx.args.setdefault('sprinting', True)

    def update():
        ctx.args['strafe'] = f32(0)

    jump(ctx, after_jump_tick = update)

@command(aliases=['snj45'])
def sneakjump45(ctx, duration = 1, rotation: f32 = None):
    "Sneak and jump while 45 strafing"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    jump(ctx)

@command(aliases=['snsj45'])
def sneaksprintjump45(ctx, duration = 1, rotation: f32 = None):
    """
    Jump while sneaking, sprinting, and 45 strafing.
    
    Only works for versions 1.14+. To sneak and sprint, the player must be sprinting on the tick before they sneak.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('sprinting', True)
    ctx.args['function_offset'] = f32(9.1148519592841453)

    def update():
        ctx.args.setdefault('strafe', f32(1))
        ctx.args['function_offset'] = f32(45)

    jump(ctx, after_jump_tick = update)

@command(aliases=['wj45'])
def walkjump45(ctx, duration = 1, rotation: f32 = None):
    "Jump and 45 strafe without sprint"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    jump(ctx)

@command(aliases=['sj45'])
def sprintjump45(ctx, duration = 1, rotation: f32 = None):
    """
    Jump and 45 strafe with sprint.

    Note that the best way to 45 strafe eith sprint is to jump facing straight and then 45 strafe while midair.

    Hence `sprintjump45(1)` is equivalent to `sprintjump(1)`,

    likewise, `sj45(5)` is equivalent to `sj(1) sa45(4)`
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sprinting', True)
    
    def update():
        ctx.args.setdefault('strafe', f32(1))
        ctx.args['function_offset'] = f32(45)
    
    jump(ctx, after_jump_tick = update)

@command(aliases=['lsj45'])
def lsprintjump45(ctx, duration = 1, rotation: f32 = None):
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('sprinting', True)
    
    ctx.args['function_offset'] = f32(45)
    
    jump(ctx)

@command(aliases=['rsj45'])
def rsprintjump45(ctx, duration = 1, rotation: f32 = None):
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(-1))
    ctx.args.setdefault('sprinting', True)
    
    ctx.args['function_offset'] = f32(-45)
    
    jump(ctx)

@command(aliases=['snp'])
def sneakpessi(ctx, duration = 1, delay = 1, rotation: f32 = None):

    ctx.args['duration'] = delay
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['wp'])
def walkpessi(ctx, duration = 1, delay = 1, rotation: f32 = None):

    ctx.args['duration'] = delay
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['sp'])
def sprintpessi(ctx, duration = 1, delay = 1, rotation: f32 = None):

    ctx.args['duration'] = delay
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('airborne', True)
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['snp45'])
def sneakpessi45(ctx, duration = 1, delay = 1, rotation: f32 = None):

    ctx.args['duration'] = delay
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('sneaking', True)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['wp45'])
def walkpessi45(ctx, duration = 1, delay = 1, rotation: f32 = None):

    ctx.args['duration'] = delay
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['sp45'])
def sprintpessi45(ctx, duration = 1, delay = 1, rotation: f32 = None):

    ctx.args['duration'] = delay
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    ctx.args.setdefault('airborne', True)
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['forcemomentum', 'fmm'])
def force_momentum(ctx, duration = 1, delay = 1, rotation: f32 = None):
    """
    Jump without sprint, then activate sprint midair.

    fmm(x,y) = walkjump(y) sprintair(x-y)

    Be aware of sprint air delay in versions 1.8-1.19.
    """
    ctx.args['duration'] = delay
    ctx.args.setdefault('forward', f32(1))
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('airborne', True)
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['forcemomentum45', 'fmm45'])
def force_momentum45(ctx, duration = 1, delay = 1, rotation: f32 = None):
    """
    While 45 strafing, jump without sprint, then activate sprint midair.

    fmm45(x,y) = walkjump45(y) sprintair45(x-y)

    Be aware of sprint air delay in versions 1.8-1.19.
    """
    ctx.args['duration'] = delay
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(45)
    jump(ctx)

    ctx.args['duration'] = duration - delay
    ctx.args.setdefault('airborne', True)
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['st'])
def stop(ctx, duration = 1):
    "Inputless ticks while on the ground"
    move(ctx)

@command(aliases=['sta'])
def stopair(ctx, duration = 1):
    "Inputless ticks while airborne"
    ctx.args.setdefault('airborne', True)
    move(ctx)

@command(aliases=['stj'])
def stopjump(ctx, duration = 1):
    "Inputless jump, `stj(x)` being equivalent to `st sta(x-1)`"
    jump(ctx)

@command(aliases=['stfj'])
def sprintstrafejump(ctx, duration = 1, rotation: f32 = None):
    """
    It is NOT called "Shut The Fuck Jump".

    Strafejump with sprint at the optimal angle for distance. This is weaker than normal sprint jumping.
    """
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(17.4786857811690446)

    def update():
        ctx.args['strafe'] = f32(0)
        ctx.args['function_offset'] = f32(0)
    
    jump(ctx, after_jump_tick = update)

@command(aliases=['stfj45'])
def sprintstrafejump45(ctx, duration = 1, rotation: f32 = None):
    """
    It is NOT called "Shut The Fuck Jump 45".

    Strafejump with sprint at the optimal angle for distance. This is weaker than normal sprint jumping.
    """
    ctx.args.setdefault('sprinting', True)
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args['function_offset'] = f32(17.4786857811690446)

    def update():
        ctx.args['function_offset'] = f32(45)
    
    jump(ctx, after_jump_tick = update)

##### New water stuff ##### If anything goes wrong blame physiq not me :D
@command(aliases=['wwt', 'wt', 'water'])
def walkwater(ctx, duration = 1, rotation: f32 = None):
    """
    `walkwater` and `sprintwater` are equivalent while in water, but beware of sprint air delay when exiting water.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('water', True)
    move(ctx)

@command(aliases=['swt'])
def sprintwater(ctx, duration = 1, rotation: f32 = None):
    """
    `walkwater` and `sprintwater` are equivalent while in water, but beware of sprint air delay when exiting water.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('water', True)
    ctx.args.setdefault('sprinting', True)
    move(ctx)

@command(aliases=['stwt'])
def stopwater(ctx, duration = 1):
    "Inputless tick while in water"
    ctx.args.setdefault('water', True)
    move(ctx)

@command(aliases=['wwt45', 'water45', 'wt45'])
def walkwater45(ctx, duration = 1, rotation: f32 = None):
    """
    `walkwater45` and `sprintwater45` are equivalent while in water, but beware of sprint air delay when exiting water.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('water', True)
    ctx.args['function_offset'] = f32(45)

@command(aliases=['swt45'])
def sprintwater45(ctx, duration = 1, rotation: f32 = None):
    """
    `waterwalk45` and `watersprint45` are equivalent while in water, but beware of sprint air delay when exiting water.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('water', True)
    ctx.args.setdefault('sprinting', True)
    ctx.args['function_offset'] = f32(45)
    move(ctx)

@command(aliases=['snwt'])
def sneakwater(ctx, duration = 1, rotation: f32 = None):
    "Sneak while in water"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('water', True)
    ctx.argd.setdefault('sneaking', True)
    move(ctx)

@command(aliases=['snwt45'])
def sneakwater45(ctx, duration = 1, rotation: f32 = None):
    "Sneak and 45 while in water"
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('water', True)
    ctx.args['function_offset'] = f32(45)
    ctx.argd.setdefault('sneaking', True)
    move(ctx)

@command(aliases=['snswt'])
def sneaksprintwater(ctx, duration = 1, rotation: f32 = None):
    """
    Sneak and sprint while in water

    Only works for versions 1.14+. The player can only sneak sprint if the tick before was sprinted. 
    
    That also means you must be outside of water in order to be able to snesk sprint in water.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('water', True)
    ctx.args.setdefault('sprinting', True)
    ctx.argd.setdefault('sneaking', True)
    move(ctx)

@command(aliases=['snswt45'])
def sneaksprintwater45(ctx, duration = 1, rotation: f32 = None):
    """
    Sneak, sprint, and 45 strafe while in water

    Only works for versions 1.14+. The player can only sneak sprint if the tick before was sprinted. 
    
    That also means you must be outside of water in order to be able to snesk sprint in water.
    """
    ctx.args.setdefault('forward', f32(1))
    ctx.args.setdefault('strafe', f32(1))
    ctx.args.setdefault('water', True)
    ctx.args.setdefault('sprinting', True)
    ctx.args['function_offset'] = f32(45)
    ctx.argd.setdefault('sneaking', True)
    move(ctx)
##### End of new water stuff ######

@command(name='|')
def reset_position(ctx):
    """
    Alias of `setposx(0) setposz(0)`

    Resets the player's position to (0,0)
    """
    ctx.player.x = 0
    ctx.player.modx = 0
    ctx.player.z = 0
    ctx.player.modz = 0

@command(name='b')
def output_blocks(ctx):
    """
    Outputs the players position in terms of blocks
    """
    ctx.player.modx += f32(copysign(0.6, ctx.player.x))
    ctx.player.modz += f32(copysign(0.6, ctx.player.z))

@command(name='mm')
def output_mm(ctx):
    """
    Outputs the players position in terms of momentum
    """
    ctx.player.modx -= f32(copysign(0.6, ctx.player.x))
    ctx.player.modz -= f32(copysign(0.6, ctx.player.z))

@command(aliases=['$'])
def zero(ctx):
    ctx.player.modx -= ctx.player.x
    ctx.player.modz -= ctx.player.z

@command()
def zerox(ctx):
    ctx.player.modx -= ctx.player.x

@command()
def zeroz(ctx):
    ctx.player.modz -= ctx.player.z

@command(aliases = ['v'])
def setv(ctx, vx = 0.0, vz = 0.0):
    "Sets the player's velocity"
    ctx.player.vx = vx
    ctx.player.vz = vz

@command(aliases = ['vx'])
def setvx(ctx, vx = 0.0):
    "Sets the player's x velocity"
    ctx.player.vx = vx

@command(aliases = ['vz'])
def setvz(ctx, vz = 0.0):
    "Sets the player's z velocity"
    ctx.player.vz = vz

@command(aliases = ['pos', 'xz'])
def setpos(ctx, x = 0.0, z = 0.0):
    "Sets the player's position"
    ctx.player.x = x
    ctx.player.z = z

@command(aliases = ['posx', 'x'])
def setposx(ctx, x = 0.0):
    "Sets the player's x position"
    ctx.player.x = x

@command(aliases = ['posz', 'z'])
def setposz(ctx, z = 0.0):
    "Sets the player's z position"
    ctx.player.z = z

@command()
def setvec(ctx, speed = 0.0, angle = 0.0):
    "Sets the players speed and angle. A negative speed will flip the angle 180 degrees"
    ctx.player.vx = -speed * sin(radians(angle))
    ctx.player.vz = speed * cos(radians(angle))

@command()
def speed(ctx, speed = 0):
    "Sets the player's speed potion amplifier (range 0 to 256)"
    ctx.player.speed = speed

@command(aliases = ['slow'])
def slowness(ctx, slowness = 0):
    "Sets the player's slow potion amplifier (range 0 to 256). Slow 7 and beyond are equivalent and result in a speed multiplier of 0 regardless of speed (affects ground movement)."
    ctx.player.slowness = slowness

@command(aliases = ['slip'])
def setslip(ctx, slip = f32(0)):
    "Sets the player's default ground slipperiness"
    ctx.player.ground_slip = slip

@command(aliases = ['a'])
def angles(ctx, angles = -1):
    """
    Approximates how the game would behave if Minecraft had `angles` significant angles.
    
    Vanilla: 65536
    Optifine: 4096
    """
    ctx.player.angles = angles

@command()
def fastmath(ctx):
    """Changes the simulation to use old optifine fast math. An alias of `angles(4096)`."""
    ctx.player.angles = 4096

@command()
def inertia(ctx, inertia = 0.005):
    """
    Sets the inertia threshold.
    
    1.8- : 0.005
    1.9+ : 0.003
    """
    ctx.player.inertia_threshold = inertia

@command(aliases = ['pre'])
def precision(ctx, precision = 6):
    "Sets the number of digits to truncate the output"
    ctx.print_precision = precision

@command(aliases = ['facing', 'face', 'f'])
def rotation(ctx, angle = f32(0)):
    "Sets the player's default facing to `angle`"
    ctx.player.default_rotation = angle

@command(aliases = ['offrotation', 'or', 'offsetfacing', 'of'])
def offsetrotation(ctx, angle = f32(0)):
    "Sets the player's rotation offset to `angle`. This will add `angle` to its default rotation for each tick, but it will not set the new facing to be the default rotation."
    ctx.player.rotation_offset = angle

@command(aliases = ['turn'])
def turn(ctx, angle = f32(0)):
    "Turn the player `angle` degrees AND set that new rotation to be default"
    ctx.player.default_rotation += angle

@command(aliases = ['ssand', 'ss'])
def soulsand(ctx, soulsand = 1):
    ctx.player.soulsand = soulsand

@command(aliases = ['aq', 'qa'])
def anglequeue(ctx):
    "Queues angles, each subsequent tick, the player sets the next angle in queue to be the default angle it faces."
    def to_f32(val):
        try:
            return f32(val)
        except:
            raise SimError(f'Error in `anglequeue` converting `{val}` to type `rotation:float32`')
    ctx.player.rotation_queue.extend(map(to_f32, ctx.pos_args))

@command(aliases = ['tq', 'qt'])
def turnqueue(ctx):
    "Queues angles, each subsequent tick, the player adds the next angle in queue to its default rotation AND sets it to be the default rotation."
    def to_f32(val):
        try:
            return f32(val)
        except:
            raise SimError(f'Error in `turnqueue` converting `{val}` to type `rotation:float32`')
    ctx.player.turn_queue.extend(map(to_f32, ctx.pos_args))

@command()
def macro(ctx, name = 'macro'):
    "Makes an mpk (not cyv) macro file named `name.csv`"
    ctx.macro = name

def zeroed_formatter(ctx, num, zero):
    if zero is None:
        return ctx.format(num)
    
    formatted_offset = ctx.format(num - zero, sign=True)
    if any([formatted_offset.startswith(s) for s in ('+', '-')]):
        formatted_offset = f'{formatted_offset[0:1]} {formatted_offset[1:]}'
    else:
        formatted_offset = f'? {formatted_offset}'
    
    return f'{ctx.format(zero)} {formatted_offset}'

@command()
def outx(ctx, zero: f64 = None, label: str = "X"):
    """
    Outputs the player's x displacement.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `outx` outputs `X: 0.9311`, then `outx(1)` outputs `X: 1 - 0.0689`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, ctx.player.x, zero)}\n'
@command()
def outz(ctx, zero: f64 = None, label: str = "Z"):
    """
    Outputs the player's z displacement.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `outz` outputs `Z: 0.9311`, then `outz(1)` outputs `Z: 1 - 0.0689`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, ctx.player.z, zero)}\n'

@command()
def outvx(ctx, zero: f64 = None, label: str = "Vx"):
    """
    Outputs the player's x velocity.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `outvx` outputs `Vx: -0.072`, then `outvx(-0.0615)` outputs `Vx: -0.0615 - 0.0105`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, ctx.player.vx, zero)}\n'
@command()
def outvz(ctx, zero: f64 = None, label: str = "Vz"):
    """
    Outputs the player's z velocity.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `outvz` outputs `Vz: 0.252`, then `outvz(0.25)` outputs `Vz: 0.25 + 0.002`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, ctx.player.vz, zero)}\n'

@command(name='outxmm', aliases=['xmm'])
def x_mm(ctx, zero: f64 = None, label: str = "X mm"):
    """
    Outputs the player's x position in terms of momentum.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `xmm` outputs `Xmm: 0.9992`, then `xmm(1)` outputs `Xmm: 1 - 0.0008`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, dist_to_mm(ctx.player.x), zero)}\n'
@command(name='outzmm', aliases=['zmm'])
def z_mm(ctx, zero: f64 = None, label: str = "Z mm"):
    """
    Outputs the player's z position in terms of momentum.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `zmm` outputs `Zmm: 1.976`, then `zmm(2)` outputs `Zmm: 2 - 0.024`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, dist_to_mm(ctx.player.z), zero)}\n'

@command(name='outxb', aliases=['xb'])
def x_b(ctx, zero: f64 = None, label: str = "X b"):
    """
    Outputs the player's x position in terms of blocks.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `xb` outputs `Xb: -4.133`, then `xb(-4.125)` outputs `Xb: -4.125 - 0.008`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, dist_to_b(ctx.player.x), zero)}\n'
@command(name='outzb', aliases=['zb'])
def z_b(ctx, zero: f64 = None, label: str = "Z b"):
    """
    Outputs the player's z position in terms of blocks.

    If `zero` is a nonzero number, the output will be expressed as an expression centered at `zero`.

    Example: If `zb` outputs `Zb: 5.000003`, then `zb(5)` outputs `Zb: 5 + 0.000003`

    `zero` will also be truncated by the current decimal precision.
    """
    ctx.out += f'{label.strip()}: {zeroed_formatter(ctx, dist_to_b(ctx.player.z), zero)}\n'
    
@command(aliases = ['speedvec', 'vector', 'vec'])
def speedvector(ctx):
    """Displays the magnitude and direction of the player's speed vector."""
    speed = sqrt(ctx.player.vx**2 + ctx.player.vz**2)
    angle = degrees(atan2(-ctx.player.vx, ctx.player.vz))
    ctx.out += f'Speed: {ctx.format(speed)}\n'
    ctx.out += f'Angle: {ctx.format(angle)}\n'

@command(aliases = ['sprintdelay', 'sdel'])
def air_sprint_delay(ctx, sprint_delay = True):
    """
    Change the air sprint delay, which is present in 1.19.3-
    
    If air sprint delay is toggled on, activating and deactivating sprint in midair is 1 tick delayed.
    """
    ctx.player.air_sprint_delay = sprint_delay

@command(aliases = ['poss', 'zposs'])
def possibilities(ctx, inputs = 'sj45(100)', mindistance: float = 0.01, offset:f32 = f32(0.6), miss: float = None):
    """
    Performs `inputs` and displays ticks where z is within `mindistance` above a pixel.

    Offsets:
    Blocks = 0.6 
    Water/Web = 0.599
    Slime/Ladder = 0.3
    Avoid = 0.0
    Neo = -0.6

    The `mindistance` must be less than a pixel (0.0625).

    If `miss` is a nonzero number, displays ticks where x is within `miss` below a pixel.
    """
    mindistance = abs(mindistance) # only dealing with positive offsets
    if mindistance >= 0.0625:
        raise SimError(f"Minimum distance must be less than 0.0625, got {mindistance} instead")
    
    old_move = ctx.player.move

    tick = 1
    def move(self, ctx):
        nonlocal tick, old_move

        old_move(ctx)

        player_blocks = self.z + offset
        jump_pixels = int(abs(player_blocks) / 0.0625)
        jump_blocks = jump_pixels * 0.0625 * copysign(1, self.z)
        poss_by = (abs(player_blocks) - abs(jump_blocks)) * copysign(1, self.z)

        if abs(poss_by) < mindistance:
            ctx.out += f'Tick {tick}: {ctx.format(poss_by)} ({ctx.format(jump_blocks)}b)\n'
        elif miss:
            jump_blocks += 0.0625 * copysign(1, jump_blocks)
            miss_by = (abs(player_blocks) - abs(jump_blocks)) * copysign(1, self.z)
            if abs(miss_by) < miss:
                ctx.out += f'Tick {tick}: {ctx.format(miss_by)} miss from {ctx.format(jump_blocks)}b\n'
        
        tick += 1
    
    ctx.player.move = MethodType(move, ctx.player)
    ctx.out += '```'
    
    commands_args = parsers.string_to_args(inputs)
    for command, cmd_args in commands_args:
        parsers.execute_command(ctx, command, cmd_args)
    
    ctx.out += '```'
    ctx.player.move = old_move

@command(aliases = ['xposs'])
def xpossibilities(ctx, inputs = 'sj45(100)', mindistance: float = 0.01, offset:f32 = f32(0.6), miss: float = None):
    """
    Performs `inputs` and displays ticks where x is within `mindistance` above a pixel.

    Offsets:
    Blocks = 0.6 
    Water/Web = 0.599
    Slime/Ladder = 0.3
    Avoid = 0.0
    Neo = -0.6

    The `mindistance` must be less than a pixel (0.0625).

    If `miss` is a nonzero number, displays ticks where x is within `miss` below a pixel.
    """
    mindistance = abs(mindistance) # only dealing with positive offsets
    if mindistance >= 0.0625:
        raise SimError(f"Minimum distance must be less than 0.0625, got {mindistance} instead")
    
    old_move = ctx.player.move

    tick = 1
    def move(self, ctx):
        nonlocal tick, old_move

        old_move(ctx)

        player_blocks = self.x + offset
        jump_pixels = int(abs(player_blocks) / 0.0625)
        jump_blocks = jump_pixels * 0.0625 * copysign(1, self.z)
        poss_by = (abs(player_blocks) - abs(jump_blocks)) * copysign(1, self.z)

        if abs(poss_by) < mindistance:
            ctx.out += f'Tick {tick}: {ctx.format(poss_by)} ({ctx.format(jump_blocks)}b)\n'
        elif miss:
            jump_blocks += 0.0625 * copysign(1, jump_blocks)
            miss_by = (abs(player_blocks) - abs(jump_blocks)) * copysign(1, self.z)
            if abs(miss_by) < miss:
                ctx.out += f'Tick {tick}: {ctx.format(miss_by)} miss from {ctx.format(jump_blocks)}b\n'
        
        tick += 1
    
    ctx.player.move = MethodType(move, ctx.player)
    ctx.out += '```'
    
    commands_args = parsers.string_to_args(inputs)
    for command, cmd_args in commands_args:
        parsers.execute_command(ctx, command, cmd_args)
    
    ctx.out += '```'
    ctx.player.move = old_move
    
@command(aliases=['ji'])
def jumpinfo(ctx, z = 0.0, x = 0.0):
    """
    Displays the dimensions, real and block distance, and angle of the shortest distance for a distance jump.
    """

    if abs(z) < 0.6:
        dz = 0.0
    else:
        dz = b_to_dist(z)
    if abs(x) < 0.6:
        dx = 0.0
    else:
        dx = b_to_dist(x)
    
    if dz == 0.0 and dx == 0.0:
        ctx.out += 'That\'s not a jump!'
        return
    elif dz == 0.0 or dx == 0.0:
        ctx.out +=  f'**{ctx.format(max(x, z))}b** jump -> **{ctx.format(max(dx, dz))}** distance'
        return

    distance = sqrt(dx**2 + dz**2)
    angle = degrees(atan(dx/dz))

    lines = [
        f'A **{ctx.format(z)}b** by **{ctx.format(x)}b** block jump:',
        f'Dimensions: **{ctx.format(dz)}** by **{ctx.format(dx)}**',
        f'Distance: **{ctx.format(distance)}** distance -> **{ctx.format(distance+0.6)}b** jump',
        f'Optimal Angle: **{angle:.3f}°**'
    ]

    ctx.out += '\n'.join(lines) + '\n'

@command()
def duration(ctx, floor = 0.0, ceiling = 0.0, inertia = 0.005, jump_boost = 0):
    """
    Displays the duration of a `floor` jump.
    """

    vy = 0.42 + 0.1 * jump_boost
    y = 0
    ticks = 0

    while y > floor or vy > 0:
        y = y + vy
        if ceiling != 0.0 and y > ceiling - 1.8:
            y = ceiling - 1.8
            vy = 0
        vy = (vy - 0.08) * 0.98
        if abs(vy) < inertia:
            vy = 0
        ticks += 1

        if ticks > 5000:
            ctx.out += 'Simulation limit reached.'
            return

    if vy >= 0:
        ctx.out += 'Impossible jump height. Too high.'
        return

    ceiling = f' {ceiling}bc' if ceiling != 0.0 else ''
    ctx.out += f'Duration of a {floor}b{ceiling} jump:\n**{ticks} ticks**\n'

@command()
def height(ctx, duration = 12, ceiling = 0.0, inertia = 0.005, jump_boost = 0):
    """
    Displays the player's height `duration` ticks after jumping.
    """

    vy = 0.42 + jump_boost * 0.1
    y = 0

    for i in range(duration):
        y = y + vy
        if ceiling != 0.0 and y > ceiling - 1.8:
            y = ceiling - 1.8
            vy = 0
        vy = (vy - 0.08) * 0.98
        if abs(vy) < inertia:
            vy = 0

        if i > 5000:
            ctx.out += ('Simulation limit reached.')
            return
    
    ceiling = f' with a {ceiling}bc' if ceiling != 0.0 else ''
    ctx.out += (f'Height after {duration} ticks{ceiling}:\n**{round(y, 6)}**\n')

@command()
def blip(ctx, blips = 1, blip_height = 0.0625, init_height: f64 = None, init_vy: f64 = None, inertia = 0.005, jump_boost = 0):
    """
    Calculates the heights of each blip while blipping.

    Shows `Fail` when trying to blip again would fail.
    """

    if init_height is None:
        init_height = blip_height
    if init_vy is None:
        init_vy = 0.42 + 0.1 * jump_boost    
    
    blips_done = 0
    vy = init_vy
    y = init_height
    jump_ys = [init_height]
    max_heights = []
    vy_prev = 0
    i = 0

    while blips_done < blips or vy > 0:

        y += vy
        vy = (vy - 0.08) * 0.98

        if y + vy < blip_height:

            if y + vy > 0:
                max_heights.append('Fail')
                jump_ys.append(y + vy)
                break
            
            jump_ys.append(y)
            vy = 0.42
            blips_done += 1
        
        if abs(vy) < inertia:
            vy = 0

        if vy_prev > 0 and vy <= 0:
            max_heights.append(y)

        if i > 5000:
            ctx.out += 'Simulation limit reached.'
            return

        vy_prev = vy
        i += 1

    out = '\n'.join([
        f'Blips: {blips_done}',
        f'Blip height: {round(blip_height, 6)}',
        f'Initial y: {round(init_height, 6)}',
        f'Initial vy: {round(init_vy, 6)}',
        f'```Blip | Jumped From | Max Height'
    ])

    num_col_width = len(str(blips))
    for i in range(0, len(jump_ys)):
        num = f'{i:0{num_col_width}}'.ljust(4)
        jumped_from = f'{jump_ys[i]:<11.6f}'
        max_height = f'{max_heights[i]:<10.6f}' if type(max_heights[i]) == f64 else max_heights[i]
        out += (f'\n{num} | {jumped_from} | {max_height}')
    out += '```\n'
    
    ctx.out += out

def inv_helper(ctx, transform, goal_x, goal_z, strat):

    # Perform the first simulation
    ctx1 = ctx.child()
    ctx1.player.inertia_threshold = 0.0
    ctx1.player.vx = 0.0
    ctx1.player.vz = 0.0
    parsers.execute_string(ctx1, strat)

    # Perform the second simulation
    ctx2 = ctx.child()
    ctx2.player.inertia_threshold = 0.0
    ctx2.player.vx = 1.0
    ctx2.player.vz = 1.0
    parsers.execute_string(ctx2, strat)

    # Use the info to calculate the ideal vx/vz, if required
    vx = None
    vz = None
    if goal_x is not None:
        vx = (ctx1.player.x - transform(goal_x)) / (ctx1.player.x - ctx2.player.x)
        ctx.player.vx = vx
    if goal_z is not None:
        vz = (ctx1.player.z - transform(goal_z)) / (ctx1.player.z - ctx2.player.z)
        ctx.player.vz = vz
    
    parsers.execute_string(ctx, strat)

    return vx, vz

@command(aliases=['zbwmm', 'bwmm'])
def z_bwmm(ctx, mm = 1.0, strat = 'sj45(12)'):
    """
    Performs `strat` with an initial speed such that `mm`bm is covered while performing it.

    If the strat runs into inertia while being performed with the optimal speed, then the distance will be incorrect.

    By default, it assumes the player starts on the ground. Prefix it with `sta` to indicate starting while midair, or `stwt` to indicate starting in water. 
    
    Example: `stopair zbwmm(1, sprintjump(6))`
    """

    vx, vz = inv_helper(ctx, mm_to_dist, None, mm, strat)

    ctx.pre_out += f'Speed: {ctx.format(vz)}\n'
    ctx.pre_out += f'MM: {ctx.format(dist_to_mm(ctx.player.z))}\n'

@command(aliases=['zinv', 'inv'])
def z_inv(ctx, goal = 1.6, strat = 'sj45(12)'):
    """
    Performs `strat` with an initial speed such that `goal` is covered while performing it.

    If the strat runs into inertia while being performed with the optimal speed, then the distance will be incorrect.

    By default, it assumes the player starts on the ground. Prefix it with `sta` to indicate starting while midair, or `stwt` to indicate starting in water. 
    
    Example: `zinv(1, fmm45(12) sprint45)`
    """

    vx, vz = inv_helper(ctx, dist_to_dist, None, goal, strat)
    
    ctx.pre_out += f'Speed: {ctx.format(vz)}\n'
    ctx.pre_out += f'Dist: {ctx.format(ctx.player.z)}\n'

@command(aliases=['zspeedreq', 'speedreq'])
def z_speedreq(ctx, blocks = 5.0, strat = 'sj45(12)'):
    """
    Performs `strat` with an initial speed such that `blocks`b is covered while performing it.

    If the strat runs into inertia while being performed with the optimal speed, then the distance will be incorrect.

    By default, it assumes the player starts on the ground. Prefix it with `sta` to indicate starting while midair, or `stwt` to indicate starting in water. 
    
    Example: `stopair zspeedreq(5, sprintjump45(14))`
    """

    vx, vz = inv_helper(ctx, b_to_dist, None, blocks, strat)

    ctx.pre_out += f'Speed: {ctx.format(vz)}\n'
    ctx.pre_out += f'Blocks: {ctx.format(dist_to_b(ctx.player.z))}\n'

@command(aliases=['xbwmm'])
def x_bwmm(ctx, mm = 1.0, strat = 'sj45(12)'):
    """A version of bwmm that optimizes x instead of z."""

    vx, vz = inv_helper(ctx, mm_to_dist, mm, None, strat)

    ctx.pre_out += f'Speed: {ctx.format(vx)}\n'
    ctx.pre_out += f'MM: {ctx.format(dist_to_mm(ctx.player.x))}\n'

@command(aliases=['xinv'])
def x_inv(ctx, goal = 1.6, strat = 'sj45(12)'):
    """A version of inv that optimizes x instead of z."""

    vx, vz = inv_helper(ctx, dist_to_dist, goal, None, strat)
    
    ctx.pre_out += f'Speed: {ctx.format(vx)}\n'
    ctx.pre_out += f'Dist: {ctx.format(ctx.player.x)}\n'

@command(aliases=['xspeedreq'])
def x_speedreq(ctx, blocks = 5.0, strat = 'sj45(12)'):
    """A version of speedreq that optimizes x instead of z."""

    vx, vz = inv_helper(ctx, b_to_dist, blocks, None, strat)

    ctx.pre_out += f'Speed: {ctx.format(vx)}\n'
    ctx.pre_out += f'Blocks: {ctx.format(dist_to_b(ctx.player.x))}\n'

@command(aliases=['xzbwmm'])
def xz_bwmm(ctx, x_mm = 1.0, z_mm = 1.0, strat = 'sj45(12)'):
    """A version of bwmm that optimizes both x and z."""

    vx, vz = inv_helper(ctx, mm_to_dist, x_mm, z_mm, strat)

    ctx.pre_out += f'Speed: {ctx.format(vx)}/{ctx.format(vz)}\n'
    ctx.pre_out += f'MM: {ctx.format(dist_to_mm(ctx.player.x))}/{ctx.format(dist_to_mm(ctx.player.z))}\n'

@command(aliases=['xzinv'])
def xz_inv(ctx, x_goal = 1.6, z_goal = 1.6, strat = 'sj45(12)'):
    """A version of inv that optimizes both x and z."""

    vx, vz = inv_helper(ctx, dist_to_dist, x_goal, z_goal, strat)
    
    ctx.pre_out += f'Speed: {ctx.format(vx)}/{ctx.format(vz)}\n'
    ctx.pre_out += f'Dist: {ctx.format(ctx.player.x)}/{ctx.format(ctx.player.z)}\n'

@command(aliases=['xzspeedreq'])
def xz_speedreq(ctx, x_blocks = 3.0, z_blocks = 4.0, strat = 'sj45(12)'):
    """A version of speedreq that optimizes both x and z."""

    vx, vz = inv_helper(ctx, b_to_dist, x_blocks, z_blocks, strat)

    ctx.pre_out += f'Speed: {ctx.format(vx)}/{ctx.format(vz)}\n'
    ctx.pre_out += f'Blocks: {ctx.format(dist_to_b(ctx.player.x))}/{ctx.format(dist_to_b(ctx.player.z))}\n'

@command(aliases=['angle', 'ai'])
def angleinfo(ctx, angle = f32(0.0), mode = 'vanilla'):
    """
    Get the trig value, significant angle, sin table index, and normal of some angle.
    Mode can be: ['vanilla', 'optifine']
    """

    angle_rad = angle * f32(PI) / f32(180)

    mode = mode.lower()
    if mode == 'vanilla':
        sin_index = u64(i32(angle_rad * f32(10430.378)) & 65535)
        cos_index = u64(i32(angle_rad * f32(10430.378) + f32(16384.0)) & 65535)
        sin_value = sin(sin_index * PI * 2.0 / 65536)
        cos_value = sin(cos_index * PI * 2.0 / 65536)
        cos_index_adj = (int(cos_index) - 16384) % 65536
    elif mode == 'optifine':
        sin_index = u64(i32(angle_rad * f32(651.8986)) & 4095)
        cos_index = u64(i32((angle_rad + f32(1.5707964)) * f32(651.8986)) & 4095)
        sin_value = fastmath_sin_table[sin_index]
        cos_value = fastmath_sin_table[cos_index]
        cos_index_adj = (int(cos_index) - 1024) % 4096
    else:
        raise SimError(f'Unkown mode {mode}. Options are `vanilla`, `optifine`.')
    
    sin_angle = degrees(asin(sin_value))
    cos_angle = degrees(acos(cos_value))
    normal = sqrt(sin_value**2.0 + cos_value**2.0)

    format = ctx.format
    output = [
        [f'{format(angle)}°', 'Sin', 'Cos', 'Normal'],
        ['Value', format(sin_value), format(cos_value), format(normal)],
        ['Angle', format(sin_angle), format(cos_angle), ''],
        ['Index', format(sin_index), f'{format(cos_index_adj)} ({format(cos_index)})', '']
    ]

    for col in output:
        col_width = max(map(len, col)) + 2
        for i in range(len(col)):
            col[i] = col[i].ljust(col_width)

    ctx.out += '```'
    for i in range(4):
        for j in range(4):
            ctx.out += output[j][i]
        ctx.out += '\n'
    ctx.out += '```'

@command()
def help(ctx, cmd_name = 'help'):
    """
    Get help with a function by displaying it's name, aliases, arguments, and defaults.
    arg_name: data_type = default_value

    Example: help(help) help(s) help(bwmm)
    """

    if cmd_name not in commands_by_name:
        ctx.out += f'Command `{cmd_name}` not found\n'
        return

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

    ctx.out += f'Help with {cmd_name}:'
    ctx.out += '' if cmd.__doc__ is None else f'\n```{cleandoc(cmd.__doc__)}```'
    ctx.out += f'```\nAliases:\n{newln.join(map(lambda x: "  "+x, cmd._aliases))}'
    ctx.out += f'\nArgs:\n{newln.join(params)}```\n'

@command(aliases=['print'])
def println(ctx, *strings: str = ('\n')):
    "Print any basic text to your heart's desire"
    ctx.out += ",".join(strings) + '\n'
    # if it doesn't work: ctx.out += strings
