#!/usr/bin/env python3

from log import get_logger
from effects import (
    Filter,
    RenderedFilter,
    get_barycenter,
    needs_more_face_points,
    get_face_dimension,
    needs_more_dank,
)
from config import (
    EFFECTS,
)
from cli import (
    cli,
)

if __name__ == "__main__":
    cli()