from dataclasses import dataclass
from enum import IntEnum

WIDTH = 3
HEIGHT = 3
STATES = 2
WRAP = False
DIAGONAL = False
INDEX_CACHE: dict[int, list[int, None]] = {}

State = IntEnum('States', dict((str(i), i) for i in range(STATES)))


@dataclass
class RuleCondition:
    appearances: int
    state: State


@dataclass
class Rule:
    state: State
    conditions: list[RuleCondition]


class Grid:
    rules: list[Rule]
    data: list[State]
    states: int
    width: int
    height: int
    wrap: bool
    diagonal: bool

    def __init__(
            self,
            rules: list[Rule],
            signature: int,
            states: int,
            width: int,
            height: int,
            wrap: bool = True,
            diagonal: bool = True
    ):
        if len(rules) == 0:
            self.rules = [
                Rule(
                    State['0'],
                    [
                        RuleCondition(neighbor, State[str(state)])
                        for state in range(states)
                        for neighbor in range(8)
                    ]
                )
            ]
        else:
            self.rules = rules
        self.states = states
        self.width = width
        self.height = height
        self.wrap = wrap
        self.diagonal = diagonal
        self.data = convert_base(signature, states)
        for _ in range((width * height) - len(self.data)):
            self.data.insert(0, State['0'])

    def signature(self) -> int:
        return int(''.join(map(lambda i: str(i.value), self.data)), self.states)

    def calculate_non_wrapping_non_diagonal(self, index: int) -> list[int]:
        cached = None
        if index in INDEX_CACHE:
            cached = INDEX_CACHE[index]
        if cached is not None:
            return [item for item in [cached[1], cached[3], cached[5], cached[7]] if item is not None]
        neighbors = []
        cache: list[int | None] = [None]
        if (index - 1) >= 0:
            neighbors.append(index - 1)
            cache.append(index - 1)
        else:
            cache.append(None)
        cache.append(None)
        if (index + 1) < len(self.data):
            neighbors.append(index + 1)
            cache.append(index + 1)
        else:
            cache.append(None)
        cache.append(None)
        if (index - self.width) >= 0:
            neighbors.append(index - self.width)
            cache.append(index - self.width)
        else:
            cache.append(None)
        if (index + self.width) < len(self.data):
            neighbors.append(index + self.width)
            cache.append(index + self.width)
        else:
            cache.append(None)
        cache.append(None)
        INDEX_CACHE[index] = cache
        return neighbors

    def calculate_wrapping_non_diagonal(self, index: int) -> list[int]:
        # TODO: add caching
        neighbors = []
        if (index - 1) >= 0:
            neighbors.append(index - 1)
        else:
            neighbors.append(index - 1 + self.width)
        if (index + 1) < len(self.data):
            neighbors.append(index + 1)
        else:
            neighbors.append(index + 1 - self.width)
        if (index - self.width) >= 0:
            neighbors.append(index - self.width)
        else:
            neighbors.append(index - self.width + (self.height * self.width))
        if (index + self.width) < len(self.data):
            neighbors.append(index + self.width)
        else:
            neighbors.append(index + self.width - (self.height * self.width))
        return neighbors

    def calculate_non_wrapping_diagonal(self, index: int) -> list[int]:
        # TODO:
        #  add caching
        #  be careful, we might have already used cache for the non diagonal ones, we need to take that into account
        #  cache might need to be updated
        neighbors = self.calculate_non_wrapping_non_diagonal(index)
        if (index - self.width - 1) >= 0:
            neighbors.append(index - self.width - 1)
        if (index - self.width + 1) >= 0:
            neighbors.append(index - self.width + 1)
        if (index + self.width - 1) < len(self.data):
            neighbors.append(index + self.width - 1)
        if (index + self.width + 1) < len(self.data):
            neighbors.append(index + self.width + 1)
        return neighbors

    def calculate_wrapping_diagonal(self, index: int) -> list[int]:
        # TODO:
        #  add caching
        #  be careful, we might have already used cache for the non diagonal ones, we need to take that into account
        #  cache might need to be updated
        neighbors = self.calculate_wrapping_non_diagonal(index)
        if (index - self.width - 1) >= 0:
            neighbors.append(index - self.width - 1)
        else:
            neighbors.append(index - self.width - 1 + (self.height * self.width))
        if (index - self.width + 1) >= 0:
            neighbors.append(index - self.width + 1)
        else:
            neighbors.append(index - self.width + 1 + (self.height * self.width))
        if (index + self.width - 1) < len(self.data):
            neighbors.append(index + self.width - 1)
        else:
            neighbors.append(index + self.width - 1 - (self.height * self.width))
        if (index + self.width + 1) < len(self.data):
            neighbors.append(index + self.width + 1)
        else:
            neighbors.append(index + self.width + 1 - (self.height * self.width))
        return neighbors

    def get_surrounding(self, index: int) -> list[RuleCondition]:
        neighbors = []
        match [self.wrap, self.diagonal]:
            case [False, False]:
                neighbors = self.calculate_non_wrapping_non_diagonal(index)
            case [True, False]:
                neighbors = self.calculate_wrapping_non_diagonal(index)
            case [False, True]:
                neighbors = self.calculate_non_wrapping_diagonal(index)
            case [True, True]:
                neighbors = self.calculate_wrapping_diagonal(index)
        result = []
        for state in range(self.states):
            result.append(RuleCondition(0, State[str(state)]))
        for neighbor in neighbors:
            state = self.data[neighbor]
            result[int(state)].appearances += 1
        return result

    def apply_rules(self, cell: State, neighborhood: list[RuleCondition]) -> State:
        # TODO:
        #  deal with this, unsure which condition should take priority
        #  maybe the first one?
        for rule in self.rules:
            return rule.state

    def generate_next_grid(self) -> 'Grid':
        grid = Grid(self.rules, 0, self.states, self.width, self.height, self.wrap, self.diagonal)
        grid.data = [
            self.apply_rules(cell, self.get_surrounding(index))
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


def convert_base(value: int, base: int) -> list[State]:
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
    print(f'Generated automaton map: \n  {result_map}\n')


if __name__ == '__main__':
    main()
