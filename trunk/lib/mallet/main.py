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

"""Main module for mallet"""

import pygtk
pygtk.require('2.0')
import gtk

from mallet.editor import EditorBook


def run():
    """Start the application"""
    w = MainWindow()
    w.show_all()
    gtk.main()


class MainWindow(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.uim = uim = gtk.UIManager()
        accelgroup = uim.get_accel_group()
        self.add_accel_group(accelgroup)

        ncb = lambda *args: None

        self.actiongroup = actiongroup = gtk.ActionGroup('DefaultActionGroup')

        # Create actions
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Quit', None,
                                  'Quit the Program', ncb),
                                 ('FileMenu', None, '_File'),
                                 ('EditMenu', None, '_Edit'),
                                 ])

        actiongroup.add_actions([('OnlineHelp', None, 'Online _Help', None,
                                  'Get help on the web', ncb),
                                 ('About', None, '_About', None,
                                  'About this program', ncb),
                                 ('HelpMenu', None, '_Help')])
                      
        uim.insert_action_group(actiongroup, 0)
        merge_id = uim.add_ui_from_string(uidesc)

        e = EditorBook()
        e.show()
        e_ag, e_uidesc = e.getUI()
        uim.insert_action_group(e_ag, 1)
        uim.add_ui_from_string(e_uidesc)

        # packing
        vbox = gtk.VBox()
        menubar = uim.get_widget('/MenuBar')
        toolbar = uim.get_widget('/Toolbar')
        vbox.pack_start(menubar, False)
        vbox.pack_start(toolbar, False)
        vbox.pack_start(e, True)

        self.add(vbox)

class Splash:

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)
        self.window.show()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()


uidesc = """
  <menubar name="MenuBar">
    <menu action="FileMenu">
      <menuitem action="Quit" position="bot"/>
    </menu>
    <menu action="EditMenu">
    </menu>
    <menu action="HelpMenu">
      <menuitem action="OnlineHelp" position="top" />
      <menuitem action="About" position="bot"/>
    </menu>
  </menubar>
"""
