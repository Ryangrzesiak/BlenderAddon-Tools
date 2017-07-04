### Ryan's Blender Scripts
#Test

# Addon info
bl_info = {
    'name': 'Ryan Tools',
    'author': 'Ryan Grzesiak',
    'version': (1, 0, 0),
    'blender': (2, 74),
    'location': 'View3D > UI panel > Add Tools',
    'description': 'To use Blender more efficently',
    'category': '3D View'
}

import sys

# Import files
#from ryan_tools import edit_groups
#from ryan_tools import material_creator

from ryan_tools.edit_groups import (
    edit_groups,
    )

## Create Material from Textures

from ryan_tools.material_creator import (
    material_creator,
    )
    
from ryan_tools.action_editor import (
    action_editor,
    )


'''
## FBX Exporter Tool
from ryan_tools.fbx_export import (
    exporter_panel,
    )
'''


## Tools for quick use
from ryan_tools.quick_tools import (
    tool_panel,
    )

# Register the Addon
def _call_globals(attr_name):
    for m in globals().values():
        if hasattr(m, attr_name):
            getattr(m, attr_name)()

def _flush_modules(pkg_name):
    pkg_name = pkg_name.lower()
    for k in tuple(sys.modules.keys()):
        if k.lower().startswith(pkg_name):
            del sys.modules[k]

def register():
    _call_globals("register")
	
def unregister():
    _call_globals("unregister")
    _flush_modules("ryan_tools")  # reload ryan_tools

if __name__ == "__main__" :
    register()
