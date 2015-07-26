__author__ = 'alexgoretoy'

import os
import sys
project_name = os.path.dirname(__file__).split('/').pop()
if "".join(sys.path[0]).endswith(project_name):
    project = os.path.dirname("".join(sys.path[0]))
    if project not in sys.path:
        os.sys.path.insert(0, project)
    del project
elif "".join(sys.path[-1:]).endswith(project_name):
    project = os.path.dirname("".join(sys.path[-1:]))
    if project not in sys.path:
        os.sys.path.insert(0, project)
    del project