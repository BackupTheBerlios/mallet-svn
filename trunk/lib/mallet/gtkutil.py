# Copyright (C) 2004 Sridhar Ratna <sridhar@users.berlios.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software 
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""Utility functions, classes for GTK"""

import inspect
import gtk


class ActionControllerMixin:

    def connectActionCallbacks(self, action_group):
        """Connect cb_<action_name> methods to the corresponding Actions"""
        # generate Action names list from callback methods
        methods = [x[0] for x in inspect.getmembers(self) \
                   if inspect.ismethod(x[1])]
        startWith = 'cb_'
        actions_list = [x[len(startWith):] for x in methods \
                        if x.startswith(startWith)]

        # Connect the callback for each action
        for action_name in actions_list:
            action = action_group.get_action(action_name)
            callback = getattr(self, 'cb_%s' % action_name)
            # The "activate" signal is emitted when Action is activated.
            action.connect("activate", callback)
