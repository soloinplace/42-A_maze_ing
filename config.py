class Config():
    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None
    
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exit_: tuple[int, int],
            output_file: str,
            perfect: bool,
            seed: int | None = None):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.output_file = output_file
        self.perfect = perfect
        self.seed = None
        if seed:
            self.seed = seed


    def __str__(self):
        return f"Width = {self.width}, " \
        f"Height = {self.height}, " \
        f"Entry = {self.entry}, " \
        f"Exit = {self.exit_}, " \
        f"Output file = {self.output_file}, " \
        f"Perfect = {self.perfect}, " \
        f"Seed = {self.seed}"