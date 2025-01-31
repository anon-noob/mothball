import inspect

class FunctionSignature:
    def __init__(self, func_or_funcname):
        self.posititonal_only: list[inspect.Parameter] = []
        self.posititonal_or_keyword: list[inspect.Parameter] = []
        self.keyword_only: list[inspect.Parameter] = []
        self.var_positional: list[inspect.Parameter] = []
        self.var_keyword: list[inspect.Parameter] = []

        self.after_keyword = False

        if isinstance(func_or_funcname, str):
            self.name = func_or_funcname
        else:
            params = inspect.signature(func_or_funcname).parameters

            self.name = func_or_funcname.__name__



            for p in params.values():
                match p.kind:
                    case inspect.Parameter.POSITIONAL_ONLY:
                        self.posititonal_only.append(p)
                    case inspect.Parameter.POSITIONAL_OR_KEYWORD:
                        self.posititonal_or_keyword.append(p)
                    case inspect.Parameter.KEYWORD_ONLY:
                        self.keyword_only.append(p)
                    case inspect.Parameter.VAR_POSITIONAL:
                        self.var_positional.append(p)
                    case inspect.Parameter.VAR_KEYWORD:
                        self.var_keyword.append(p)

        # Remove the self parameter
        if self.posititonal_only and self.posititonal_only[0].name == 'self':
            self.posititonal_only = self.posititonal_only[1:]
        elif self.posititonal_or_keyword and self.posititonal_or_keyword[0].name == 'self':
            self.posititonal_or_keyword = self.posititonal_or_keyword[1:]

        self.posititonals = self.posititonal_only + self.posititonal_or_keyword
        self.keywords = self.posititonal_or_keyword + self.keyword_only
        
        self.current_parameter: inspect.Parameter = None
        if self.posititonals:
            self.current_parameter = self.posititonals[0]
        elif self.var_positional:
            self.current_parameter = self.var_positional[0]
        elif self.keywords:
            self.current_parameter = self.keywords[0]
        elif self.var_keyword:
            self.current_parameter = self.var_keyword[0]

    
    def __repr__(self):
        return f"""Function {self.name}
positional_only: {self.posititonal_only}
positional_or_keyword: {self.posititonal_or_keyword}
keyword_only: {self.keyword_only}
var_positional: {self.var_positional}
var_keyword: {self.var_keyword}"""
    
    def next_positional_parameter(self):
        if self.after_keyword:
            print("DONE")
            self.current_parameter = None
        elif self.posititonals:
            self.posititonals.remove(self.current_parameter)
            if self.current_parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                self.keywords.remove(self.current_parameter)
            try:
                self.current_parameter = self.posititonals[0]
            except:
                if self.var_positional:
                    self.current_parameter = self.var_positional[0]
                else:
                    self.current_parameter = "All positional arguments expended"
                    self.after_keyword = True
    
    def remove_keyword_parameter(self, param_name: str):
        keyword_to_remove = [x for x in self.keywords if x.name == param_name]
        if keyword_to_remove:
            keyword_to_remove = keyword_to_remove[0]
            self.keywords = [x for x in self.keywords if x.name != param_name]
            self.after_keyword = True
            self.current_parameter = keyword_to_remove
    
    def get_current_parameter(self):
        return self.current_parameter
    
    def get_current_parameter_type(self):
        try: return self.current_parameter.annotation
        except AttributeError: return None

    def get_current_parameter_kind(self):
        return self.current_parameter.kind
    
    def remaining_keywords(self, return_as: str = "name"):
        if return_as == "parameter":
            return self.keywords
        elif return_as == "name":
            return [x.name for x in self.keywords]
    
    def get_keyword_type(self, name: str):
        # print(f"{name=}")
        a = {x.name:x for x in self.keywords}
        # print(a)
        b = a.get(name)
        if b is not None:
            return b.annotation

    
class ParenthesisStack:
    def __init__(self):
        self.stack: list[tuple[tuple[str,str],str]] = []
    
    def peek(self):
        if not self.is_empty():
            return self.stack[-1]

    def push(self, position: str, parenthesis: str):
        "Position is of the form `row.column`"
        a,b = position.split(".")

        self.stack.append(((position,f"{a}.{int(b)+1}"), parenthesis))
    
    def pop(self):
        if not self.is_empty():
            return self.stack.pop()

    def matches_parenthesis_stack(self, parenthesis: str):
        if self.is_empty():
            return False
        
        left_parenthesis = self.peek()[1]
        if (left_parenthesis == "(" and parenthesis == ")") or (left_parenthesis == "{" and parenthesis == "}"):
            return True
        return False

    def is_empty(self):
        return len(self.stack) == 0
    


class FunctionStack:
    def __init__(self):
        self.stack: list[FunctionSignature] = []
    
    def push(self, function):
        "to push"
        self.stack.append(FunctionSignature(function))
    
    def peek(self):
        if not self.is_empty():
            return self.stack[-1]
    
    def peek_current_parameter_annotation(self):
        return self.peek().get_current_parameter_type()
    
    def peek_after_keyword(self):
        return self.peek().after_keyword
    
    def peek_next_positional_parameter(self):
        self.peek().next_positional_parameter()

    def peek_remaining_keywords(self, mode: str = "name"):
        return self.peek().remaining_keywords(mode)
    
    def peek_remove_keyword(self, name: str):
        return self.peek().remove_keyword_parameter(name)

    def peek_get_keyword_type(self, name: str):
        return self.peek().get_keyword_type(name)
    
    def peek_function_name(self):
        return self.peek().name
        
    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
    
    def is_empty(self):
        return len(self.stack) == 0
