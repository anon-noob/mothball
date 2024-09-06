# Mothball
A Discord bot for simulating Minecraft movement to high accuracy, used for parkour among other minecraft fields of research involving movement.

## Commands
`;[simulate | sim | s]`​`functions` Simulates the provided functions and displays the final result.  
`;[history | h]`​`functions` Simulates the provided functions and displays tick by tick results.  
`;[then | t]`​`functions` Continues simulation from the reply and displays the final result.  
`;[thenh | th]`​`functions` Continues simulation from the reply and displays tick by tick results.

### Non-Simulation Functions

`jumpinfo(z, x=0)`  
`duration(floor=0, ceiling=inf, inertia=0.005, jump_boost=0)`  
`height(ticks=0, ceiling=inf, inertia=0.005, jump_boost=0)`  
`blip(num_blips=1, blip_height=0.0625, init_height=blip_height, init_vy=(0.42+jump_boost), inertia=0.005, jump_boost=0)`

## Function Syntax
Functions must be separated by spaces. They consist of the function name, optionally followed by arguments in parenthesis. Args must be separated by commas.

### Functions
Movement names are generally of the format `[stop, sneak, walk, sprint]`​`[air, jump]`​`[45]`.  
These can be shortened down to `[st, sn, w, s]`​`[a, j]`​`[45]`.

Exceptions include the strafe sprintjump variants, which are prefixed with `[l, r]`.

#### Player Functions:
| Function     | Alias(es) | Arguments | Result                                                     |
|--------------|-----------|-----------|------------------------------------------------------------|
| \|           |           |           | Resets the player's position                               |
| b            |           |           | Modifies the player's x/z positions to be in blocks jumped |
| mm           |           |           | Modifies the player's x/z positions to be in mm used       |
| setv         | v         | vx, vz    | Sets the player's x and z velocities                       |
| setvx        | vx        | vx        | Sets the player's x velocity                               |
| setvz        | vz        | vz        | Sets the player's z velocity                               |
| setpos       | pos       | x, z      | Sets the player's x and z positions                        |
| setposx      | posx, x   | x         | Sets the player's x position                               |
| setposz      | posz, z   | z         | Sets the player's z position                               |
| facing       | face, f   | angle     | Sets the player's default facing                           |
| offsetfacing | oface, of | angle     | Offsets the player's facing once                           |
| turn         | t         | angle     | Turns the player's default facing                          |
#### Simulation Parameter Functions:
| Function     | Alias(es) | Arguments | Result                                                     |
|--------------|-----------|-----------|------------------------------------------------------------|
| precision    | pre       | precision | Sets the number of decimals in the output                  |
| angles       | angle     | angles    | Sets the player's default number of significant angles     |
| inertia      |           | inertia   | Sets the player's inertia threshold                        |
| speed        |           | speed     | Sets the player's speed                                    |
| slowness     | slow      | slowness  | Sets the player's slowness                                 |
| setslip      | slip      | slip      | Sets the player's default ground slipperiness              |
#### Output Functions:
| Function     | Alias(es) | Arguments | Result                                                     |
|--------------|-----------|-----------|------------------------------------------------------------|
| xb           |           | centered  | Outputs the player's x position in blocks jumped           |
| zb           |           | centered  | Outputs the player's z position in blocks jumped           |
| outx         |           | centered  | Outputs the player's x displacement                        |
| outz         |           | centered  | Outputs the player's z displacement                        |
| xmm          |           | centered  | Outputs the player's x position in mm used                 |
| zmm          |           | centered  | Outputs the player's z position in mm used                 |
| speedvector  | vec       | centered  | Outputs the player's speed vector                          |

if `centered` is a nonzero number, the output functions will display the number as an expression in terms of `centered`. For example, running `;s sj outvz` results in `Vz: 0.3274`, and running `;s sj outvz(0.3)` results in `Vz: 0.3 + 0.0274`. Keep in mind that the `centered` number will also be truncated by the simulation's precision.

### Arguments
Arguments affect only the function in which they are present.

Positional arguments are defined by their positions to one another. Keyworded arguments are given by `argument`​`=`​`value`.

Most movement functions have the positonal args `duration, rotation`, which default to 1 and the player's default rotation, respectively. Many functions include default values for arguments like inertia that can be overriden to provide custom behavior.

| Argument  | Alias(es) | Effect                                     |
|-----------|-----------|--------------------------------------------|
| duration  | dur, t    | Duration of the action                     |
| rotation  | rot, r    | The player's rotation                      |
| slip      | s         | Ground slipperiness                        |
| airborne  | air       | Determines whether the player is airborne  |
| sprinting | sprint    | Determines whether the player is sprinting |
| sneaking  | sneak, sn | Determines whether the player is sneaking  |
| jumping   | jump      | Determines whether the player is jumping   |
| speed     | spd       | Determines the player's speed level.       |
| slowness  | slow      | Determines the player's slowness level.    |

Adding arguments to functions clearly not designed for them will produce unpredictable and/or impossible results. It is also good to know a few quirks to this system. In particular, any function that moves the player while airborne or inside water will ignore `slip`, `speed`, and `slowness`. Hence, running `;s sprintair(3, slip=4, slow=2)` is no different than `;s sprintair(3)`.

### The repeat function
The repeat function (or just `r` for short) lets you repeat a function or a series of functions multiple times.  
For example, `repeat(sprintjump(12) outz, 3)` is equivalent to `sj(12) outz sj(12) outz sj(12) outz`.
Simulations will time out if it takes too long to calculate.

### Comments
Anything delimited by `#` will be ignored. Hence, running `wj.s(12) w.s | # hello world sj(3) # sj(12)` is equivalent to running `wj.s(12) w.s | sj(12)`.
Comments are multiline.

## User-Defined Variables and Functions

Custom variables can be defined with the syntax `var(name, val)`.  
For example, you could define t=12 with `var(t, 12)`, then use the variable with `sprintjump(t)`.

Custom functions can be defined with the syntax `def(name, inputs, *args)`.  
For example, you could define `def(angled_3bc, -wj(duration, angle) -w(1, angle) | sj(duration, angle), duration, angle)`.  
You could then call this function with `angled_3bc(11, 0.0054)`

Functions and variables will persist across channels and servers until Mothball restarts.

## Input-based Functions

You may modify a movement function's keypresses with the syntax `function.keys`.  
For example, `sprint.wd(4, 10)` would sprint with WD for 4 ticks facing 10.

Prepending a function with `-` will invert the keypresses.  
For example, `-w(5)` walks backwards with S for 5 ticks, and `-s.wd(2)` will sprint backwarwds with S and A for 2 ticks.
For the sake of clarity and readability, it is recommended to only use the `-` syntax as an alternative to `<func>.s` (unless you're calculating movement resulting from glitches).

## Macros

MPK Mod macros can be made by adding the argumentless macro function anywhere in a command.  
For example, this simulates 1bm 5-1: `wj.sd(12, 35) w.sd(1, 35) sj.wa(1, 35) s45a(11) | sj45(14) b macro`  
You may also provide the macro function a name with macro(name)

Macros will not account for sprinting in air starting a tick late.

Cyv Client macros have a slightly different syntax than MPK Mod macros. As mothball only outputs MPK Mod macros, be sure to double check while converting the macro to Cyv's style.

## Optimization Functions

There are three optimization functions: `bwmm`, `inv`, and `speedreq`.  
They all behave similarly. First, they take a goal arg that they will optimize Z towards. Second, they take a strat to optimize. The function will find the speed required to meet the goal, then perform the strat that speed.

Here are a few examples!  
1bm 4.8175+0.5: `bwmm(1, sj45(12)) | sj45(10) zb`. This is a loop jump.  
2bm backwalled 4.125b with 3bc: `inv(2, sj | sa(11)) | sj45(11) zb`. Note that there's a `|` after the sj forward. This is because you're still moving backward before that tick, so it must be ignored.  
Finding the speed required for a 5 block, no 45: `sta speedreq(5, sj(12)) b`. Note the `sta` before the `speedreq`. This is to make the player start midair, since mothball usually assumes the player starts on the ground.
`speedreq` is also used for momentums with both a front and back wall. For example, a 3bm backwalled triple neo: `speedreq(3, sj | sa(11)) | sj(11) zmm(3)`. Note the `|` after the sj forward. As a bonus, using `zmm` helps check the offset for triple neos as well as any neo where distance is potentially a very important factor.
