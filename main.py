WIDTH = 1
HEIGHT = 1
STATES = 3
WRAP = False
DIAGONAL = True


class Grid:
    rules: list[...]
    data: list[int]
    states: int
    width: int
    height: int
    wrap: bool
    diagonal: bool

    def __init__(
            self,
            rules: list[...],
            signature: int,
            states: int,
            width: int,
            height: int,
            wrap: bool = True,
            diagonal: bool = True
    ):
        self.rules = rules
        self.states = states
        self.width = width
        self.height = height
        self.wrap = wrap
        self.diagonal = diagonal
        self.data = convert_base(signature, states)
        for _ in range((width * height) - len(self.data)):
            self.data.insert(0, 0)

    def signature(self) -> int:
        return int(''.join(map(lambda i: str(i), self.data)), self.states)

    def get_surrounding(self, index: int) -> dict[int, int]:
        res = {}
        # TODO: implement surroundings
        match [self.wrap, self.diagonal]:
            case [False, False]:
                ...
            case [False, True]:
                ...
            case [True, False]:
                ...
            case [True, True]:
                ...
        return res

    def apply_rules(self, cell: int, neighborhood: dict[int, int], rules: list[...]) -> int:
        # TODO: implement rules
        match self.rules:
            case _:
                return 0

    def generate_next_grid(self) -> 'Grid':
        grid = Grid(self.rules, 0, self.states, self.width, self.height, self.wrap, self.diagonal)
        grid.data = [
            self.apply_rules(cell, self.get_surrounding(index), self.rules)
            for index, cell in enumerate(self.data)
        ]
        return grid

    def __str__(self) -> str:
        return (
                f'Grid (width={self.width}, height={self.height} [diagonal={self.diagonal}, wrap={self.wrap}]) [\n  ' +
                ',\n  '.join(
                    [
                        ','.join(map(lambda el: str(el), self.data[i:(i + self.width)]))
                        for i in range(0, len(self.data), self.width)
                    ]
                ) + '\n]'
        )


def convert_base(value: int, base: int) -> list[int]:
    result = []
    while value > 0:
        result.insert(0, value % base)
        value = value // base
    return result


def main() -> None:
    print('Generating automaton map..\n')
    result_map: dict[int, int] = {}
    for signature in range(STATES ** (WIDTH * HEIGHT)):
        grid = Grid([], signature, STATES, WIDTH, HEIGHT, WRAP, DIAGONAL)
        next_grid = grid.generate_next_grid()
        result_map[signature] = next_grid.signature()
    print(f'Generated automaton map: \n  {result_map}')


if __name__ == '__main__':
    main()
