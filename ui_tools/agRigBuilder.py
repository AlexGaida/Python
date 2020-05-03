"""
opens the rig builder tool.
"""

# import custom modules
from rig_builder import rig_builder

# reload modules
reload(rig_builder)

# define global variables
BUILD_WIN = None

def main():
    global BUILD_WIN
    if BUILD_WIN:
        BUILD_WIN.close_ui()

    if not BUILD_WIN:
        BUILD_WIN = rig_builder.open_ui()
    