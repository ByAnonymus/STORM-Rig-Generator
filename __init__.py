# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Storm_rig",
    "author": "ByAnon",
    "description": "",
    "blender": (3, 4, 0),
    "version": (1, 3, 0),
    "location": "",
    "warning": "",
    "category": "Generic",
}

from . import rig_adapt, Panels


def register():
    rig_adapt.register()
    Panels.register()

def unregister():
    rig_adapt.unregister()
    Panels.unregister()