import enum


class State(enum.Enum):
    WHITE = "."
    BLACK = "#"
    UNKNOWN = "?"


def get_possibilities(constraints: list[int], length: int) -> list[list[State]]:
    """For a single row or column, return all possible solutions."""
    if not constraints:
        return [[State.WHITE] * length]
    
    *init, last = constraints
    return [
        (
            l
            + [State.WHITE] * (n != 0)  # don't add a white cell if at the start
            + [State.BLACK] * last
            + [State.WHITE] * (length - n - last)
        )
        for n in range(0, length - last + 1)
        for l in get_possibilities(init, n - 1)
    ]


def filter_possibilities(
    possibilities: list[list[State]], fact: list[State]
) -> list[list[State]]:
    """Filter out possibilities that are not compatible with the fact."""
    return [
        cs for cs in possibilities
        if all(f == State.UNKNOWN or f == c for c, f in zip(cs, fact))
    ]


def deduce_facts(possibilities: list[list[State]]) -> list[State]:
    """Consolidate the facts from a list of possibilities."""
    return [
        ps[0] if len(set(ps)) == 1 else State.UNKNOWN
        for ps in zip(*possibilities)
    ]


class Picross:
    def __init__(self, rows: list[list[int]], columns: list[list[int]]):
        self.row_constraints = rows
        self.column_constraints = columns
        self.width = len(columns)
        self.height = len(rows)
        self.board = [[State.UNKNOWN for _ in columns] for _ in rows]

        self.row_possibilities = [
            get_possibilities(rc, self.width) for rc in self.row_constraints
        ]
        self.column_possibilities = [
            get_possibilities(cc, self.height) for cc in self.column_constraints
        ]

    def solve(self):
        while not self.is_solved():
            self.solve_step()

    def is_solved(self) -> bool:
        return all(all(cell != State.UNKNOWN for cell in row) for row in self.board)

    def solve_step(self):
        """
        For each row/column, see if we can deduce any facts from the possibilities.
        Then, filter out the possibilities that are not compatible with the new facts.
        """
        for i, row in enumerate(self.row_possibilities):
            self.enrich_row(i, deduce_facts(row))
        for j, column in enumerate(self.column_possibilities):
            self.enrich_column(j, deduce_facts(column))

        for i, row in enumerate(self.row_possibilities):
            self.row_possibilities[i] = filter_possibilities(row, self.row(i))
        for j, column in enumerate(self.column_possibilities):
            self.column_possibilities[j] = filter_possibilities(column, self.column(j))

    def row(self, i: int) -> list[State]:
        return self.board[i]
    
    def column(self, j: int) -> list[State]:
        return [self.board[i][j] for i in range(self.height)]

    def enrich_row(self, i: int, row: list[State]):
        """Write any known facts to one row."""
        for j, cell in enumerate(row):
            if cell != State.UNKNOWN:
                self.board[i][j] = cell

    def enrich_column(self, j: int, column: list[State]):
        """Write any known facts to one column."""
        for i in range(self.height):
            if column[i] != State.UNKNOWN:
                self.board[i][j] = column[i]

    def __str__(self):
        return "\n".join(" ".join(cell.value for cell in row) for row in self.board)


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="The input JSON file")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    picross = Picross(data["rows"], data["columns"])
    picross.solve()
    print(picross)
