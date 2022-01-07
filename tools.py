#! /usr/bin/env python

import re
from typing import Any

renum = re.compile("^\d+$")

def parseIntAuto(context: Any):

    if type(context) is str:

        if renum.match(context):

            return int(context)

    return context