class TkinterPosition:
    def __init__(self, row: int, column: int):
        self.string = f"{row}.{column}"
        self.row = row
        self.column = column
    
    def __add__(self, other):
        if isinstance(other, int):
            return TkinterPosition(self.row, self.column + other)
    
    def __sub__(self, other):
        if isinstance(other, int):
            return TkinterPosition(self.row, max(self.column - other,0))

    def add_row(self, integer: int):
        return TkinterPosition(self.row + integer, self.column)
    
    def subtract_row(self, integer: int):
        return TkinterPosition(max(self.row - integer, 1), self.column)

    def reset_column(self):
        return TkinterPosition(self.row, 0)

    def __repr__(self):
        return f"TkPos({self.row}.{self.column})"
    
    def __str__(self):
        return f"{self.row}.{self.column}"
