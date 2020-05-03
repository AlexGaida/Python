"""
opens the rig builder tool.
"""

# import custom modules
from rig_builder import rig_builder

# reload modules
reload(rig_builder)


def open_ui():
    rig_builder.open_ui()
    return True
