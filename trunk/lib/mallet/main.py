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

"""Main module"""

import os.path
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

def get_main_wind():
    return MainWindow.instance
    
# First module to be imported from `mallet`
import mallet.context
mallet.context.init_context(get_main_wind)
from mallet.context import ctx

from mallet.editor import EditorBook
from mallet.config import pixmaps_dir
from mallet.gtkutil import ActionControllerMixin


def run():
    """Start the application"""
    gtk.window_set_default_icon(MainWindow.logo)
    w = MainWindow()
    MainWindow.instance = w
    for child in w.get_children():
        w.show_all()
    w.maximize()
    w.show()
    gtk.main()



class MainWindow(gtk.Window, ActionControllerMixin):

    """Main application window"""
    
    instance = None
    
    logo = gdk.pixbuf_new_from_file(os.path.join(pixmaps_dir, 'mallet.png'))

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("GNOME Mallet")
        
        self.uim = uim = gtk.UIManager()
        accelgroup = uim.get_accel_group()
        self.add_accel_group(accelgroup)

        ncb = lambda *args: None

        self.actiongroup = actiongroup = gtk.ActionGroup('MainActionGroup')

        # Create Actions
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, '_Quit', None,
                                  'Quit the Program', ncb),
                                 ('FileMenu', None, '_File'),
                                 ('EditMenu', None, '_Edit'),
                                 ])

        actiongroup.add_actions([('About', None, '_About', None,
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
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        vbox.pack_start(menubar, False)
        vbox.pack_start(toolbar, False)
        vbox.pack_start(e, True)
        vbox.pack_start(gtk.Statusbar(), False)

        self.add(vbox)
        
        self.connectActionCallbacks(actiongroup)
        
        self.connect('delete_event', lambda *args: False)
        self.connect('destroy', self.on_Quit)

    def on_About(self, widget):
        dlg = gtk.AboutDialog()
        dlg.set_name('GNOME Mallet')
        dlg.set_version('0.0')
        dlg.set_comments('GNOME RAD')
        dlg.set_website('http://mallet.berlios.de')
        dlg.set_authors(['Sridhar Ratna'])
        dlg.set_logo(self.logo)
        dlg.set_transient_for(ctx.main_window)
        dlg.run()
        dlg.destroy()

    def on_Quit(self, widget, data=None):
        ctx._cleanup()
        gtk.main_quit()


uidesc = """
  <menubar name="MenuBar">
    <menu action="FileMenu">
      <menuitem action="Quit" position="bot"/>
    </menu>
    <menu action="EditMenu">
    </menu>
    <menu action="HelpMenu">
      <menuitem action="About" position="bot"/>
    </menu>
  </menubar>
"""
