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

"""Editor widget based on GtkSourceView"""

import gtk
import gtksourceview as gsv

from mallet.gtkutil import ActionControllerMixin


class Editor:

    """High-level simple wrapper around GtkSourceView"""

    def __init__(self):
        self.lm = gsv.SourceLanguagesManager()
        self.buffer = gsv.SourceBuffer()
        self.buffer.set_data('languages-manager', self.lm)
        self.view = gsv.SourceView(self.buffer)
    
    
class EditorBook(ActionControllerMixin):

    """Set of Editor widgets"""

    def __init__(self):
        self.action_group = ag = gtk.ActionGroup('EditorActions')
        ag.add_actions([
            ('New', gtk.STOCK_NEW, '_New', '<Control>n',
             'Open new file'),
            ('Open', gtk.STOCK_OPEN, '_Open ...', '<Control>o',
             'Open existing file'),
            ('Save', gtk.STOCK_SAVE, '_Save', '<Control>s',
             'Save current file'),
            ('SaveAs', None, 'Save _As ...', None,
             'Save current file under different filename'),

            ('Undo', gtk.STOCK_UNDO, '_Undo', '<Control>z',
             'Undo last change'),
            ('Redo', gtk.STOCK_REDO, '_Redo', '<Control><Shitf>z',
             'Redo'),
            ('Cut', gtk.STOCK_CUT, 'C_ut', '<Control>x',
             'Cut selected text to clipboard'),
            ('Copy', gtk.STOCK_COPY, '_Copy', '<Control>c',
             'Copy selected text to clipboard'),
            ('Paste', gtk.STOCK_PASTE, '_Paste', '<Control>p',
             'Paste text from clipboard'),
            ])

        self.connectActionCallbacks(ag)

    def getUI(self):
        # TODO: standardize this as plugin method
        return self.action_group, uidesc

    # action callbacks
    #

    def cb_New(self, widget):
        print 'New!'



uidesc = """
  <menubar name="MenuBar">
    <menu action="FileMenu">
      <menuitem action="New"/>
      <menuitem action="Open"/>
      <menuitem action="Save"/>
      <menuitem action="SaveAs"/>
    </menu>
    <menu action="EditMenu">
      <menuitem action="Undo"/>
      <menuitem action="Redo"/>
      <menuitem action="Cut"/>
      <menuitem action="Copy"/>
      <menuitem action="Paste"/>
    </menu>
  </menubar>
  <toolbar name="Toolbar">
      <toolitem action="New"/>
    <separator/>
      <toolitem action="Open"/>
    <separator name="sep1"/>
      <toolitem action="Cut"/>
      <toolitem action="Copy"/>
      <toolitem action="Paste"/>
  </toolbar>
"""
