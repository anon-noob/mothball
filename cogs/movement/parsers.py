from re import match, search
import cogs.movement.functions as functions
import cogs.movement.functionsY as functionsY
from cogs.movement.utils import SimError
from numpy import float32 as fl
from collections import Counter
from evalidate import Expr, base_eval_model
import re
import random
from cogs.movement.context import Context # For type hinting

if 'USub' not in base_eval_model.nodes:
    base_eval_model.nodes.append('USub')
    base_eval_model.nodes.append('UAdd')
    base_eval_model.nodes.append('Mult')
    base_eval_model.nodes.append('FloorDiv')
    base_eval_model.nodes.append('Pow')

# This function is purely for error handling scenarios
def get_suggestions(context: Context, string: str):
    """
    Given `string`, return a list of suggestions from all possible mothball commands that best matches `string`.

    For example, if `wtrsprint` was inputted, a possible suggestion is `sprintwater`.
    """
    
    matches_start = []
    matches_part = [] # If string in word
    matches_char_count = {}

    envs = {}
    for env in context.envs:
        envs.update(env)
    
    if context.simulation_axis == "xz":
        envs = {a:envs[a] for a in envs if type(envs[a]) == functions.Function}
        all_cmds = envs | commands_by_name
    elif context.simulation_axis == "y":
        envs = {a:envs[a] for a in envs if type(envs[a]) == functionsY.Function}
        all_cmds = envs | y_commands_by_name


    for command in list(all_cmds.keys()):
        # 1. Matches start
        if command.startswith(string):
            matches_start.append(command)
        # 2. Matches part
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
                except KeyError: # character not found in the command 
                    off_by += 1
            off_by += abs(len(command) - len(string))
            if off_by < len(command): matches_char_count[command] = off_by

    matches_char_count = sorted(matches_char_count, key=lambda e: matches_char_count[e])

    return matches_start + matches_part + matches_char_count

def execute_string(context, text):

    try:
        commands_args = string_to_args(text)
    except SimError:
        raise
    except Exception as e:
        if context.is_dev:
            raise
        print(e)
        raise SimError('Something went wrong while parsing.')

    for command, mods, args in commands_args:
        try:
            execute_command(context, command, mods, args)
        except SimError:
            raise
        except Exception as e:
            if context.is_dev:
                raise
            raise SimError(f'Something went wrong while executing `{command}`.\nDetails: {e}')
    
def string_to_args(text):
    commands_str_list = separate_commands(text)
    commands_args = [argumentatize_command(command) for command in commands_str_list]
    return commands_args

def execute_command(context: Context, command, mods, args):
    # print("EXECUTE CMD recieved args:", args)
    if context.simulation_axis == "xz":
        cmds = commands_by_name
    elif context.simulation_axis == "y":
        cmds = y_commands_by_name

    if context.simulation_axis == "xz":
        # Handle command modifiers
        modifiers = {}
        if command.startswith('-'):
            command = command[1:]
            modifiers['reverse'] = True
        
        if command.endswith('.land'):
            command = command[:-5]
            modifiers['prev_slip'] = fl(1.0)
        
        key_modifier = search(r'\.([ws]?[ad]?){1,2}(\.|$)', command)

        for m in mods:
            n = alias_to_modifier.get(m)
            if n is None:
                raise SimError(f"Invalid modifier {m}\nValid modifiers: `water`, `lava`, `blocking`, `web`, `ladder`")
            modifiers.setdefault(n, True)
                
            

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
    
    if command in cmds: # Normal execution
        command_function = cmds[command]

        context.args, context.pos_args = dictize_args(context.envs, command_function, args, axis=context.simulation_axis)
        if context.simulation_axis == "xz":
            context.args.update(modifiers)

        command_function(context)

    else: # CommandNotFound or user-defined function
        user_func = fetch(context.envs, command)
        
        if user_func is None:
            suggestions = get_suggestions(context, command)

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
                error_msg += f"I couldn't guess what command you wanted..."
            raise SimError(error_msg)
        
        new_env = dict([(var, val) for var, val in zip(user_func.arg_names, args)])

        for command, args in user_func.args:
            context.envs.append(new_env)
            execute_command(context, command, args)
            context.envs.pop()

def matches_parenthesis_stack(stack, parenthesis_char):
    a = stack[-1]
    return (parenthesis_char == ")" and a == "(") or (parenthesis_char == "]" and a == "[")

def remove_comments(string: str):
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
def separate_commands(string: str, splitters: tuple = ("\n", " ", "\r", "\t")) -> list: 


        result = []
        token = ""
        stack = []
        
        matches_next_element = lambda e: ((e == ")" and stack[-1] == "(") or (e == "]" and stack[-1] == "["))

        follows_slash = False

        # Delete comments
        string = remove_comments(string)

        # Regex to change '|' into 'x(0) z(0)'
        replace_bar_regex = r"(\|)"
        string = re.sub(replace_bar_regex, "x(0) z(0)", string)
        
        for char in string + splitters[0]:

            if char == "\\":
                follows_slash = True
                token += char
                continue

            elif (char == "(" or char == "[") and not follows_slash:
                stack.append(char)
            elif (char == ")" or char == "]") and not follows_slash:
                if not stack:
                    raise SyntaxError("Unopened brackets")
                if not matches_next_element(char):
                    raise SyntaxError("Unmatched brackets")
                stack.pop()

            
            if char in splitters and not stack and not follows_slash:
                token = token.strip()
                result.append(token) if token else None
                token = ""

            else:
                token += char

            follows_slash = False
        
        if stack:
            raise SyntaxError("Unclosed open parethesis")

        # print(f"{string=} gave {result=}")
        # print("SEPARATED CMDS:", result)
        return result


def argumentatize_command(command):

    e1 = r"(\W)?"
    func = r"([^.\[\(\-\)\]]+)"
    inputs = r"(?:\.([wasdWASD]+))?"
    modifiers = r"(?:\[(.*)\])?"
    args = r"(?:\((.*)\))?"
    e2 = r"(.+)?"

    tokenize_regex = e1 + func + inputs + modifiers + args + e2 

    error1, func_name, inputs, modifiers, args, error2 = re.findall(tokenize_regex, command, flags=re.DOTALL)[0]
    if error1 and error1 != "-":
        
        raise SyntaxError(f"Unknown item {error1} in {command}")
    elif error2:
        raise SyntaxError(f"Unknown item {error2} in {command}")

    # print("MODIFIERS:", modifiers)
    # print("ARGS:", args)
    if not modifiers or modifiers.isspace():
        modifiers = []
    else:
        modifiers = [x.strip() for x in modifiers.split(",")]
    # print("regex args:", args)
    if not args or args.isspace():
        args_list = []
    else: # PARSE
        arg = ""
        args_list = []
        depth = 0
        for char in args:
            if char in "[(":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "," and depth == 0:
                args_list.append(arg.strip()) if arg else None 
                arg = ''
                continue
            arg += char
        else:
            args_list.append(arg.strip()) if arg else None
        # print("LOOP:", args_list)

    if not inputs:
        cmd = func_name.lower()
    else:
        cmd = (func_name + "." + inputs).lower()
    
    # print("Command:", command)
    # print("Bundled:", (cmd, modifiers, args_list), "\n")
    return (cmd, modifiers, args_list)

def dictize_args(envs, command, str_args, axis = "xz"):
    # print("Dictize recieved args:", str_args)
    args = {}
    pos_args = []
    if axis == "xz":
        cmds = types_by_command
    elif axis == "y":
        cmds = y_types_by_command


    command_types = list(cmds[command].keys())

    positional_index = 0
    for arg in str_args:
        if match(r'^[\w_\|]* ?=', arg): # if keyworded arg
            divider = arg.index('=')
            arg_name = arg[:divider].strip()
            arg_name = dealias_arg_name(arg_name, axis=axis)

            arg_val = convert(envs, command, arg_name, arg[divider + 1:].strip(), axis=axis)
            args[arg_name] = arg_val

        elif positional_index < len(command_types): # if positional arg
            arg_name = command_types[positional_index]
            arg_val = convert(envs, command, arg_name, arg, axis=axis)
            positional_index += 1
            args[arg_name] = arg_val
        
        pos_args.append(arg)
    
    return args, pos_args

def dealias_arg_name(arg_name, axis = "xz"):
    arg_name = arg_name.lower()
    if axis == "xz":
        return aliases.get(arg_name, arg_name)
    elif axis == "y":
        return y_aliases.get(arg_name, arg_name)

def convert(envs, command, arg_name, val, axis = "xz"):
    if axis == "xz":
        types_by_cmd = types_by_command
        types_arg = types_by_arg
    elif axis == "y":
        types_by_cmd = y_types_by_command
        types_arg = y_types_by_arg

    if arg_name in types_by_cmd[command]: # if positionial arg
        type = types_by_cmd[command][arg_name]
    elif arg_name in types_arg: # if keyworded arg
        type = types_arg[arg_name]
    else:
        raise SimError(f'Unknown argument `{arg_name}`')
    try:
        return cast(envs, command, type, val) # if normal value
    except Exception as e:
        if "Node type 'Call'" in str(e): # Expected int or float, got function call instead
            e = f"Argument type should be `{type.__name__}`, not a function call."
        elif "Node type 'Pow'" in str(e): # Exponents are not allowed
            e = f"Exponents are not allowed."
        elif "invalid syntax" in str(e): # Wrong syntax in expression 
            e = f"Expression contains invalid syntax."
        
        raise SimError(f'Error in `{command.__name__}` converting `{val}` to type `{arg_name}:{type.__name__}`.\nDetails: {e}')

def cast(envs, command, type, val):

    if type == bool:
        return val.lower() not in ('f', 'false', 'no', 'n', '0')
    if val.lower() in ('none', 'null'):
        return None
    
    local_env = {'px':0.0625}
    for env in envs:
        local_env.update(env)

    if type in (int, float, fl):
        for k, v in local_env.items():
            try:
                local_env[k] = type(v)
            except:
                continue
        return type(safe_eval(val, local_env))
    
    # Do not format the string immediately if it is inside these functions
    elif type == str and command.__name__ not in ('define', 'repeat', 'z_bwmm', 'x_bwmm', 'xz_bwmm', 'z_inv','x_inv', 'xz_inv', 'z_speedreq', 'x_speedreq', 'xz_speedreq', 'possibilities', 'xpossibilities'):
        try:
            val = formatted(local_env, val)
            link_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
            result = re.findall(link_regex, val)
            if result and result[0]:
                raise SimError(f"Looks like you're trying to print some links. For safety reasons (and for the convenience of {random.randint(100,1000000)} electrons), I cannot print this.")
            return val
        except Exception as e:
            raise SimError(e)
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
                try: x = str(safe_eval(item_to_eval, env)) if item_to_eval else item_to_eval
                except Exception as e: raise ValueError(f"Attempted to evaluate `{item_to_eval}` but {e}.")

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
    # base_eval_model.nodes.append("Pow")
    
    result = Expr(val, model=eval_model).eval(env)
    return result

aliases = functions.aliases
commands_by_name = functions.commands_by_name
types_by_command = functions.types_by_command
types_by_arg = functions.types_by_arg


y_aliases = functionsY.aliases
y_commands_by_name = functionsY.commands_by_name
y_types_by_command = functionsY.types_by_command
y_types_by_arg = functionsY.types_by_arg

alias_to_modifier = {
    'water': 'water',
    'wt': 'water',
    'lava': 'lava',
    'lv': 'lava',
    'web': 'web',
    'block': 'blocking',
    'bl': 'blocking',
    'blocking': 'blocking',
    'ladder': 'ladder',
    'ld': 'ladder',
    'vine': 'vine'
}
