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

"""Editor widget based on GtkSourceView

This could perhaps become the Editor Plugin
"""

import os.path

import gobject
import gtk
import gtksourceview as gsv

from mallet.gtkutil import ActionControllerMixin, FileDialog
from mallet.context import ctx


class Editor(gtk.ScrolledWindow):

    """High-level simple wrapper around GtkSourceView"""

    LM = gsv.SourceLanguagesManager()
    
    editable = property(fget=lambda s: s.view.get_editable(), doc="Is the text editable?")

    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.buffer = gsv.SourceBuffer()
        self.view = gsv.SourceView(self.buffer)
        self.buffer.set_highlight(True)
        language = self.LM.get_language_from_mime_type('text/x-python')
        self.buffer.set_language(language)
        self.add_with_viewport(self.view)
        self.show()
        self.view.show()

    def setText(self, text):
        self.buffer.set_text(text)

    def getText(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end)


class DocumentExists(Exception):

    """Document already exists (opened by user)"""

    def __init__(self, document):
        self.document = document

    def __str__(self):
        return self.__class__.__doc__

class DocumentHasNoFilename(Exception):

    """Document was not given any filename (unnamed)"""


class UniqueNames:

    """Map each filename to unique (human readable) short versions such that no
    two filename in a 'set' has the same short version.
    
    eg:
    /root/a/file.py and /root/a/open.py map to file.py and open.py
    while
    /root/a/file.py and /root/b/file.py map to file.py[a] and file.py[b]
    """
    
    def __init__(self):
        self.basename_map = {} # file.py -> (/root/a/file.py:shortname_changed_callback,/root/b/file.py:s_c_c)
        self.uniquename = {}  # path -> unique
        
    def addPath(self, newpath, shortname_changed_callback):
        """Add newpath to set, notifying any change in shortnames for other paths"""
        basename = os.path.basename(newpath)
        map_value = self.basename_map.get(basename, {})
        map_value[newpath] = shortname_changed_callback
        self.basename_map[basename] = map_value
        self.uniquename[newpath] = None
        self._updateSet(basename)
        
    def removePath(self, path):
        """Remove newpath from set, notifying any change in shortnames for other paths"""
        basename = os.path.basename[path]
        del self.basename_map[basename][path]
        del self.uniquename[path]
        self._updateSet(basename)
        
    # main algorithm
    def _updateSet(self, basename):
        """Update self.basename_map[basename] set"""
        pathmap = self.basename_map[basename]
        shortname = {} # (basename, identity)
                       # identify is nearest parent directory name which is unique
        
        parts = {} # path components
        min_len = None
        for path in pathmap.keys():
            pth = os.path.dirname(path)
            parts[path] = pth.split(os.path.sep)
            parts[path].reverse()
            parts[path].append('') # sentinel
            if not min_len or min_len > len(parts[path]):
                min_len = len(parts[path])
            shortname[path] = [basename, '']
        
        pathmap_copy = pathmap.copy()
        for point in range(min_len):
            if len(pathmap_copy) == 1:
                del pathmap_copy[pathmap_copy.keys()[0]]
                continue
            elif len(pathmap_copy) == 0:
                break
                
            part_map = {} # parts[path][point] -> path
            for path in pathmap_copy.keys():
                part = parts[path][point]
                lst = part_map.get(part, [])
                lst.append(path)
                part_map[part] = lst
            for part, path_lst in part_map.items():
                if len(path_lst) == 1:
                    # unique name found!
                    path = path_lst[0]
                    del pathmap_copy[path]
                    shortname[path][1] = part
                
        assert len(pathmap_copy) == 0
        
        modified = []
        print '-'*30
        for path, shortname in shortname.items():
            if not self.uniquename[path] or self.uniquename[path]  != shortname:
                shortname_changed_callback = pathmap[path]
                self.uniquename[path] = shortname
                print 'Solution:', path, shortname
                shortname_changed_callback(shortname)


class Document(gobject.GObject):

    """Represent the editor and file associated with it. Any *editing* operations
    must be handled by the `editor` instance

    @ivar filename: The file represented by the document
    @ivar shortname: Unique name (shorted than filename) for this document
    @ivar editor: The editor widget contained in document
    """

    # Created (named) documents 'hashed' by the filename
    live_documents = {}
    
    uniquename = UniqueNames()

    __gsignals__ = {
        'shortname-changed': (gobject.SIGNAL_RUN_LAST, None, (str,))
    }

    filename = property(fget=lambda self: self.__filename)
    shortname = property(fget=lambda self: self.__shortname)

    def __init__(self, filename=None):
        if filename and filename in self.live_documents:
            raise DocumentExists, self.live_documents[filename]
        self.__filename = None
        self.__shortname = None
        gobject.GObject.__init__(self)
        self.editor = Editor()
        if filename:
            self.openFile(filename)
            Document.live_documents[filename] = self
        self.editor.show()
        self.editor.set_data('document-instance', self)
        
    def __set_filename(self, value):
        def update_shortname(shortname):
            if shortname[1]:
                sname = '%s [%s]' % (shortname[0], shortname[1])
            else:
                sname = '%s' % shortname[0]
            self.__shortname = sname
            self.emit('shortname-changed', sname)
        oldfilename = self.__filename
        if value == oldfilename:
            return
        self.__filename = value
        if oldfilename:
            self.uniquename.removePath(oldfilename)
        self.uniquename.addPath(value, update_shortname)

    def close(self):
        """Destroy this document"""
        if self.filename:
            del Document.live_documents[self.filename]

    def openFile(self, filename):
        """Open file"""
        self.editor.setText(open(filename).read())
        self.__set_filename(filename)

    def save(self, newFilenameIfAny=None):
        """Save to file. Use `newFilenameIfAny` (if passed) and update 
        the document filename accordingly"""
        text = self.editor.getText()
        if newFilenameIfAny:
            filename = newFilenameIfAny
        else:
            filename = self.filename
        if filename is None:
            raise DocumentHasNoFilename
        open(filename, 'w').write(text)
        self.editor.buffer.set_modified(False)
        self.__set_filename(filename)

    def getModified(self):
        """Return True if the buffer was modified since last saved"""
        return self.editor.buffer.get_modified()


gobject.type_register(Document)

    
class EditorBook(gtk.Notebook, ActionControllerMixin):

    """Documents notebook"""

    def __init__(self):
        gtk.Notebook.__init__(self)

        self.documents = {} # document -> page_num
        
        self.action_group = ag = gtk.ActionGroup('EditorActionGroup')
        ag.add_actions([
            ('New', gtk.STOCK_NEW, '_New', '<Control>n',
             'Open new file'),
            ('Open', gtk.STOCK_OPEN, '_Open ...', '<Control>o',
             'Open existing file'),
            ('Save', gtk.STOCK_SAVE, '_Save', '<Control>s',
             'Save current file'),
            ('SaveAs', None, 'Save _As ...', None,
             'Save current file under different filename'),
            ('Close', gtk.STOCK_CLOSE, '_Close', None,
             'Close current file'),

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

    def _cbFilenameChanged(self, document, prop):
        print 'CC', document.filename

    def addDocument(self, document):
        """Add a document to notebook"""
        title = str(document.shortname)
        label = gtk.Label(title)
        label.show()
        self.documents[document] = self.append_page(document.editor, label)
        document.connect('shortname-changed', self._cbShortnameChanged)
    
    def _cbShortnameChanged(self, document, shortname):
        label = self.get_tab_label(document.editor)
        label.set_text(shortname)

    def removeDocument(self, document):
        """Remove the document from notebook"""
        self.remove_page(self.documents[document])
        del self.documents[document]
        document.close()

    def focusDocument(self, document):
        """Bring the document to focus"""
        nr = self.page_num(document.editor)
        self.set_current_page(nr)

    def currentDocument(self):
        """Return the focused document"""
        nr = self.get_current_page()
        if nr == -1:
            return None # no documents
        editor = self.get_nth_page(nr)
        document = editor.get_data('document-instance')
        assert document
        return document
        
    def saveDocument(self, document):
        """Try to save the document with user interaction, returning
        True if document was saved successfully"""
        try:
            document.save()
        except DocumentHasNoFilename:
            filename = FileDialog().save()
            if filename is None:
                return False
            document.save(filename)
        return True

    # action callbacks
    #

    def on_New(self, widget):
        document = Document()
        self.addDocument(document)
        self.focusDocument(document)

    def on_Open(self, widget):
        filename = FileDialog().open()
        if filename:
            document = None
            try:
                document = Document(filename)
                self.addDocument(document)
            except DocumentExists, e:
                document = e.document
            self.focusDocument(document)

    def on_Save(self, widget):
        document = self.currentDocument()
        self.saveDocument(document)

    def on_Close(self, widget):
        document = self.currentDocument()
        if document.getModified():
            # TODO: set parent
            msg = gtk.MessageDialog(parent=None,
                                    flags=gtk.DIALOG_MODAL,
                                    type=gtk.MESSAGE_WARNING,
                                    message_format="Save %s?"%document.filename or 'Untitled')
            msg.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_YES, gtk.RESPONSE_YES)
            response = msg.run()
            msg.destroy()
            if response == gtk.RESPONSE_YES:
                if self.saveDocument(document) == False:
                    return # don't close as user cancelled
            elif response == gtk.RESPONSE_NO:
                pass # shall be closed
            else:
                return # don't save and close
        # close now
        self.removeDocument(document)


uidesc = """
  <menubar name="MenuBar">
    <menu action="FileMenu">
      <menuitem action="New"/>
      <menuitem action="Open"/>
      <menuitem action="Save"/>
      <menuitem action="SaveAs"/>
      <menuitem action="Close"/>
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
