import json
import random

from maya import cmds as mc
from pymel import core as pm

"""
controls = [str(x) for x in pm.selected()]
with open(mc.workspace(q=True, rd=True)+"data/controls.json", "w") as fp:
	json.dump(controls, fp, indent=2)
"""


skips    = {"bool", "enum"}
numerics = {"short", "float", "double"}


def has_scale_token(attr):
	scale_tokens = ["Mult", "Thickness", "Scale"]
	result = filter(lambda x: x in attr.longName(), scale_tokens)
	return bool(len(result))


def randomize_keys_on_control(control, start=None, end=None, spacing=10):
	start = start or mc.playbackOptions(q=True, ast=True)
	end   = end   or mc.playbackOptions(q=True, aet=True)

	key_frames = range(int(start), int(end+1), 10)

	## using node.attr("name") syntax here because some nodes
	## have function names that match
	translates = control.attr("translate").children()
	rotates    = control.attr("rotate").children()
	scales     = control.attr("scale").children()

	keyables = filter(lambda x: not x.type() in skips, control.listAttr(k=True))

	for attr in keyables:
		if attr in scales or has_scale_token(attr):
			r_start, r_end = 1.0, 1.2
		elif attr in rotates or "Angle" in attr.type():
			r_start, r_end = -10, 10
		else:
			r_start, r_end = -1, 1
		
		r_start, r_end = map(float, [r_start, r_end])
		
		for frame in key_frames:
			value = random.uniform(r_start, r_end)
			pm.mel.eval("setKeyframe -attribute {} -time {} -value {} {}"
						.format(attr.longName(), frame, value, control))


def randomize_keys(controls_list):
	controls = pm.ls(controls_list)
	for control in controls:
		randomize_keys_on_control(control)


## operate just on selection
randomize_keys(pm.selected())



"""
import json
from maya import cmds as mc
import os, sys

path = mc.workspace(q=True, rd=True)
path = os.sep.join([path, "scripts"])

if not path in sys.path:
	sys.path.insert(0, path)

import random_keyer

with open(mc.workspace(q=True, rd=True)+"data/controls.json", "r") as fp:
	controls = json.load(fp)

random_keyer.randomize_keys(controls)

"""
