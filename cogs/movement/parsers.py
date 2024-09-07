from re import match, search
import cogs.movement.functions as functions
from cogs.movement.utils import SimError
from numpy import float32 as fl
from collections import Counter
from evalidate import Expr, base_eval_model

if 'USub' not in base_eval_model.nodes:
    base_eval_model.nodes.append('USub')
    base_eval_model.nodes.append('UAdd')
    base_eval_model.nodes.append('Mult')
    base_eval_model.nodes.append('FloorDiv')
    base_eval_model.nodes.append('Pow')

def execute_string(context, text):

    try:
        commands_args = string_to_args(text)
    except SimError:
        raise
    except Exception:
        if context.is_dev:
            raise
        raise SimError('Something went wrong while parsing.')

    for command, args in commands_args:

        try:
            execute_command(context, command, args)
        except SimError:
            raise
        except Exception:
            if context.is_dev:
                raise
            raise SimError(f'Something went wrong while executing `{command}`.')
    
def string_to_args(text):
    commands_str_list = separate_commands(text)
    commands_args = [argumentatize_command(command) for command in commands_str_list]
    return commands_args

def execute_command(context, command, args):
    # Handle command modifiers
    modifiers = {}
    if command.startswith('-'):
        command = command[1:]
        modifiers['reverse'] = True
    
    if command.endswith('.land'):
        command = command[:-5]
        modifiers['prev_slip'] = fl(1.0)
    
    key_modifier = search(r'\.([ws]?[ad]?){1,2}(\.|$)', command)
    if key_modifier:
        keys = key_modifier.group(0)[1:]

        if 'w' in keys: modifiers.setdefault('forward', fl(1))
        if 's' in keys: modifiers.setdefault('forward', fl(-1))
        if 'a' in keys: modifiers.setdefault('strafe', fl(1))
        if 'd' in keys: modifiers.setdefault('strafe', fl(-1))

        modifiers.setdefault('forward', fl(0))
        modifiers.setdefault('strafe', fl(0))

        command = command.replace(key_modifier.group(0), '', 1)
    # End handling command modifiers

    # pp(commands_by_name)
    if command in commands_by_name: # Normal execution
        command_function = commands_by_name[command]

        context.args, context.pos_args = dictize_args(context.envs, command_function, args)
        context.args.update(modifiers)

        command_function(context)

    else: # CommandNotFound or user-defined function
        user_func = fetch(context.envs, command)
        
        if user_func is None:
            # Smart feedback here
            suggestions = []
            possible_cmds = list(commands_by_name.keys())
            
            # 1. Matches start of command
            for valid_cmd in possible_cmds:
                if valid_cmd.startswith(command):
                    suggestions.append(valid_cmd)

            # 2. Matches entire string anywhere
            for valid_cmd in possible_cmds:
                if valid_cmd not in suggestions and command in valid_cmd:
                    suggestions.append(valid_cmd)

            # 3. Matches character count
            for valid_cmd in possible_cmds:
                valid_cmd_char_count = Counter(valid_cmd)
                cmd_char_count = Counter(command)
                for char in cmd_char_count:
                    try:
                        if cmd_char_count[char] > valid_cmd_char_count[char]:
                            break
                        
                    except KeyError:
                        break

                else:
                    if valid_cmd not in suggestions:
                        suggestions.append(valid_cmd)
            
            error_msg = f'Command `{command}` not found. '

            suggestion = []
            if suggestions:
                suggestion_count = min(4, len(suggestions))
                for i in range(suggestion_count):
                    suggestion.append(f"`{suggestions[i]}`")
                if suggestion_count > 1:
                    error_msg += f"Did you mean any of the following: {', '.join(suggestion)}?"
                else:
                    error_msg += f"Did you mean {suggestion[0]}?"
            else:
                error_msg += f"I dont know what you're trying to do..."
            raise SimError(error_msg)
        
        new_env = dict([(var, val) for var, val in zip(user_func.arg_names, args)])

        for command, args in user_func.args:
            context.envs.append(new_env)
            execute_command(context, command, args)
            context.envs.pop()


def separate_commands(text):
    
    # States:
    # 0: Looking for a function
    # 1: Scanning for the opening parenthesis or whitespace
    # 2: Scanning for the closing parenthesis
    # 3: In a comment

    state = 0
    comment_state = None
    start = 0
    depth = 0
    player_commands = []

    for i in range(len(text)):
        char = text[i]

        if char == '#':
            if state != 3:
                comment_state = state
                state = 3
            else:
                state = comment_state
            continue

        if state == 0:
            if match(r'[\w_\|\-\.]', char):
                start = i
                state = 1

        elif state == 1:
            if char == '(':
                depth = 1
                state = 2
            elif not match(r'[\w_\|\-\.]', char):
                player_commands.append(text[start:i])
                state = 0

        elif state == 2:
            if char == '(':
                depth += 1
            if  char == ')':
                depth -= 1
                if depth == 0:
                    player_commands.append(text[start:i + 1])
                    state = 0

    # Handle unfinished parsing of argumentless commands
    if state == 1:
        player_commands.append(text[start:])
    elif state == 2:
        raise SimError('Unmatched opening parenthesis')

    return player_commands

def argumentatize_command(command):
    # Handle argumentless commands
    try:
        divider = command.index('(')
    except ValueError:
        return (command.lower(), [])

    args = []
    start = divider + 1
    depth = 0
    after_backslash = False
    for i in range(divider + 1, len(command) - 1):
        char = command[i]
        if char == '\\' and not after_backslash:
            after_backslash = True
            continue
        if depth == 0 and char == ',' and not after_backslash:
            args.append(command[start:i].strip())
            start = i + 1
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1

        after_backslash = False

    command_name = command[:divider].lower()
    final_arg = command[start:-1].strip()
    if len(final_arg) > 0:
        args.append(final_arg)

    return (command_name, args)

def dictize_args(envs, command, str_args):
    args = {}
    pos_args = []

    command_types = list(types_by_command[command].keys())

    positional_index = 0
    for arg in str_args:
        if match(r'^[\w_\|]* ?=', arg): # if keyworded arg
            divider = arg.index('=')
            arg_name = arg[:divider].strip()
            arg_name = dealias_arg_name(arg_name)
            arg_val = convert(envs, command, arg_name, arg[divider + 1:].strip())
            args[arg_name] = arg_val

        elif positional_index < len(command_types): # if positional arg
            arg_name = command_types[positional_index]
            arg_val = convert(envs, command, arg_name, arg)
            positional_index += 1
            args[arg_name] = arg_val
        
        pos_args.append(arg)
    
    return args, pos_args

def dealias_arg_name(arg_name):
    arg_name = arg_name.lower()
    return aliases.get(arg_name, arg_name)

def convert(envs, command, arg_name, val):
    if arg_name in types_by_command[command]: # if positionial arg
        type = types_by_command[command][arg_name]
    elif arg_name in types_by_arg: # if keyworded arg
        type = types_by_arg[arg_name]
    else:
        raise SimError(f'Unknown argument `{arg_name}`')
    try:
        return cast(envs, type, val) # if normal value
    except:
        raise SimError(f'Error in `{command.__name__}` converting `{val}` to type `{arg_name}:{type.__name__}`')

def cast(envs, type, val):
    if type == bool:
        return val.lower() not in ('f', 'false', 'no', 'n', '0')
    if val.lower() in ('none', 'null'):
        return None

    local_env = {}
    for env in envs:
        local_env.update(env)
    
    if type in (int, float, fl):
        for k, v in local_env.items():
            try:
                local_env[k] = type(v)
            except:
                continue
                # local_env[k] = safe_eval(v, local_env)
        return type(safe_eval(val, local_env))
    elif type == str:
        return formatted(local_env, val)
    else:
        return type(val)

def fetch(envs, name):
    for env in envs[::-1]:
        if name in env:
            return env[name]

def formatted(env, string: str):
    "Formats the string just like a python f-string, with expressions inside curly braces {}. Pairs of curly braces {{}} are treated like strings inside, so {{hey}} would print {hey}"
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
                raise SimError("Unmatched Brackets")

            depth -= 1
            if in_expr:
                item_to_eval += char

                item_to_eval = item_to_eval[1:len(item_to_eval) - 1]
                x = str(safe_eval(item_to_eval, env)) if item_to_eval else item_to_eval

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
        raise SimError("Unmatched Brackets")

    return formatted_string

def safe_eval(val, env):
    eval_model = base_eval_model

    # DANGEROUS, use at your own risk
    base_eval_model.nodes.append("Mult")
    base_eval_model.nodes.append("FloorDiv")
    base_eval_model.nodes.append("Pow")
    return Expr(val, model=eval_model).eval(env)


aliases = functions.aliases
commands_by_name = functions.commands_by_name
types_by_command = functions.types_by_command
types_by_arg = functions.types_by_arg
