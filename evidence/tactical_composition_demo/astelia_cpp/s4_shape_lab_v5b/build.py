"""Read-only admission of v5's exact binary. v5b never rebuilds it."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
BINARY = CPP / 's4_shape_lab_v5/build/tactics_react_host_v5'
sys.path.insert(0, str(CPP))
from build_admission import admit, sha
