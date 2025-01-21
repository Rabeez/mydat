from dataclasses import dataclass
from enum import StrEnum, auto, unique
from functools import reduce
from typing import Any, Self

import polars as pl


class KindAnalysis(StrEnum):
    FILTER = auto()
    CALCULATE = auto()
    AGGREGATE = auto()
    JOIN = auto()


@dataclass
class TableCol:
    selected: str
    options: list[str]

    @classmethod
    def from_list(cls, l: list[str]) -> Self:
        return cls(l[0], l)

    def current(self) -> str | None:
        return self.selected if self.selected != "" else None


@unique
class FilterOperation(StrEnum):
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "=="
    NE = "!="

    @classmethod
    def from_string(cls, value: str) -> Self:
        for label in cls:
            if label.value == value:
                return label
        raise ValueError(f"Could not convert '{value}' to instance of `{Self}`")


@dataclass
class FilterPredicate:
    col: TableCol
    op: FilterOperation
    value: Any


@dataclass
class AnalysisFilter:
    """Basic filter operation on table with multiple predicates."""

    predicates: list[FilterPredicate]

    def apply(self, src_df: pl.DataFrame) -> pl.DataFrame:
        exprs = []
        for pred in self.predicates:
            match pred.op:
                case FilterOperation.LT:
                    expr = pl.col(pred.col.selected).lt(pred.value)
                case FilterOperation.LE:
                    expr = pl.col(pred.col.selected).le(pred.value)
                case FilterOperation.GT:
                    expr = pl.col(pred.col.selected).gt(pred.value)
                case FilterOperation.GE:
                    expr = pl.col(pred.col.selected).ge(pred.value)
                case FilterOperation.EQ:
                    expr = pl.col(pred.col.selected).eq(pred.value)
                case FilterOperation.NE:
                    expr = pl.col(pred.col.selected).ne(pred.value)
            exprs.append(expr)
        full_expr = reduce(lambda a, b: a & b, exprs)
        # TODO: if this causes error then send alert to user with "failed operation"
        result = src_df.filter(full_expr)
        return result


@dataclass
class AnalysisCalculate:
    """Basic 'mutate' operation to add a calculated column in a table."""

    col: TableCol
    formula: str  # Used via getattr(polars, formula)(col.selected)

    def apply(self, src_df: pl.DataFrame) -> pl.DataFrame:
        raise NotImplementedError


DataAnalysis = AnalysisFilter | AnalysisCalculate


def get_available_analysis_kinds() -> list[dict[str, Any]]:
    analysis_specifications = [
        {
            "name": e.__name__.replace("Analysis", ""),
            "description": e.__doc__,
            # "dimensions": [
            #     {
            #         "name": n,
            #         "is_optional": False,
            #     }
            #     for n, _ in e.__annotations__.items()
            # ],
        }
        for e in DataAnalysis.__args__
    ]
    # NOTE: Alphabetical order
    analysis_specifications = sorted(analysis_specifications, key=lambda x: x["name"])
    return analysis_specifications
