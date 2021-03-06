# Miro - an RSS based video player application
# Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011
# Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""Handle dialog popups.

Simple Choices

For dialogs where you just want to ask the user a question use the
``ChoiceDialog class``.  Pass it a title, description and a the
buttons to display.  Then call ``dialog.run``, passing it a callback.
Here's an example::

    dialog = dialog.ChoiceDialog("Do you like pizza?",
        "Democracy would like to know if you enjoy eating pizza.",
        dialog.BUTTON_YES, dialog.BUTTON_NO)
    def handlePizzaAnswer(dialog):
        if dialog.choice is None:
            # handle the user closing the dialog windows
        elif dialog.choice == dialog.BUTTON_YES:
            # handle yes response
        elif dialog.choice == dialag.BUTTON_NO:
            # handle no respnose
    dialog.run(handlePizzaAnswer)


Advanced usage

For more advanced usage, check out the other ``Dialog`` subclasses.
They will probably have different constructor arguments and may have
attributes other than choice that will be set.  For example, the
``HTTPAuthDialog`` has a ``username`` and ``password`` attribute that
store what the user entered in the textboxes.


Frontend requirements

Frontends should implement the ``runDialog`` method in
``UIBackendDelegate`` class.  It inputs a ``Dialog`` subclass and
displays it to the user.  When the user clicks on a button, or closes
the dialog window, the frontend must call ``dialog.run_callback()``.

As we add new dialog boxes, the frontend may run into ``Dialog``
subclasses that it doesn't recognize.  In that case, call
``dialog.run_callback(None)``.

The frontend can layout the window however it wants, in particular
buttons can be arranged with the default on the right or the left
depending on the platform.  The default button is the 1st button in
the list.  Frontends should try to recognize standard buttons and
display the stock icons for them.
"""

import threading

from miro import eventloop
from miro import signals
from miro import util
from miro.gtcache import gettext_lazy, gettext as _

class DialogButton(object):
    def __init__(self, text):
        self._text = text
    def __eq__(self, other):
        return isinstance(other, DialogButton) and self.text == other.text
    def __str__(self):
        return "DialogButton(%r)" % util.stringify(self.text)
    @property
    def text(self):
        return unicode(self._text)

BUTTON_OK = DialogButton(gettext_lazy("OK"))
BUTTON_APPLY = DialogButton(gettext_lazy("Apply"))
BUTTON_CLOSE = DialogButton(gettext_lazy("Close"))
BUTTON_CANCEL = DialogButton(gettext_lazy("Cancel"))
BUTTON_DONE = DialogButton(gettext_lazy("Done"))
BUTTON_YES = DialogButton(gettext_lazy("Yes"))
BUTTON_NO = DialogButton(gettext_lazy("No"))
BUTTON_QUIT = DialogButton(gettext_lazy("Quit"))
BUTTON_CONTINUE = DialogButton(gettext_lazy("Continue"))
BUTTON_IGNORE = DialogButton(gettext_lazy("Ignore"))
BUTTON_IMPORT_FILES = DialogButton(gettext_lazy("Import Files"))
BUTTON_SUBMIT_REPORT = DialogButton(gettext_lazy("Submit Crash Report"))
BUTTON_MIGRATE = DialogButton(gettext_lazy("Migrate"))
BUTTON_DONT_MIGRATE = DialogButton(gettext_lazy("Don't Migrate"))
BUTTON_DOWNLOAD = DialogButton(gettext_lazy("Download"))
BUTTON_REMOVE_ENTRY = DialogButton(gettext_lazy("Remove Entry"))
BUTTON_DELETE_FILE = DialogButton(gettext_lazy("Delete File"))
BUTTON_DELETE_FILES = DialogButton(gettext_lazy("Delete Files"))
BUTTON_KEEP_VIDEOS = DialogButton(gettext_lazy("Keep Videos"))
BUTTON_DELETE_VIDEOS = DialogButton(gettext_lazy("Delete Videos"))
BUTTON_CREATE = DialogButton(gettext_lazy("Create"))
BUTTON_CREATE_FEED = DialogButton(gettext_lazy("Create Podcast"))
BUTTON_CREATE_FOLDER = DialogButton(gettext_lazy("Create Folder"))
BUTTON_CHOOSE_NEW_FOLDER = DialogButton(gettext_lazy("Choose New Folder"))
BUTTON_ADD_FOLDER = DialogButton(gettext_lazy("Add Folder"))
BUTTON_ADD = DialogButton(gettext_lazy("Add"))
BUTTON_ADD_INTO_NEW_FOLDER = DialogButton(gettext_lazy("Add Into New Folder"))
BUTTON_KEEP = DialogButton(gettext_lazy("Keep"))
BUTTON_DELETE = DialogButton(gettext_lazy("Delete"))
BUTTON_REMOVE = DialogButton(gettext_lazy("Remove"))
BUTTON_NOT_NOW = DialogButton(gettext_lazy("Not Now"))
BUTTON_CLOSE_TO_TRAY = DialogButton(gettext_lazy("Close to Tray"))
BUTTON_LAUNCH_MIRO = DialogButton(gettext_lazy("Launch Miro"))
BUTTON_DOWNLOAD_ANYWAY = DialogButton(gettext_lazy("Download Anyway"))
BUTTON_OPEN_IN_EXTERNAL_BROWSER = DialogButton(gettext_lazy(
                                               "Open in External Browser"))
BUTTON_DONT_INSTALL = DialogButton(gettext_lazy("Don't Install"))
BUTTON_SUBSCRIBE = DialogButton(gettext_lazy("Subscribe"))
BUTTON_STOP_WATCHING = DialogButton(gettext_lazy("Stop Watching"))
BUTTON_RETRY = DialogButton(gettext_lazy("Retry"))
BUTTON_START_FRESH = DialogButton(gettext_lazy("Start Fresh"))
BUTTON_INCLUDE_DATABASE = DialogButton(gettext_lazy("Include Database"))
BUTTON_DONT_INCLUDE_DATABASE = DialogButton(gettext_lazy(
                                            "Don't Include Database"))

class Dialog(object):
    """Abstract base class for dialogs.
    """
    def __init__(self, title, description, buttons):
        self.title = title
        self.description = description
        self.buttons = buttons
        self.event = threading.Event()

    def run(self, callback):
        self.callback = callback
        self.choice = None
        signals.system.new_dialog(self)

    def run_blocking(self):
        """Run the dialog, blocking for a response from the frontend.

        Returns the user's choice.
        """
        self.run(None)
        self.event.wait()
        return self.choice

    def run_callback(self, choice):
        """Run the callback for this dialog.  Choice should be the
        button that the user clicked, or None if the user closed the
        window without makeing a selection.
        """
        self.choice = choice
        self.event.set()
        if self.callback is not None:
            eventloop.add_urgent_call(self.callback,
                                    "%s callback" % self.__class__,
                                    args=(self,))

    def __str__(self):
        button_text = '/'.join(b.text for b in self.buttons)
        return "%s (text: %s, buttons: %s)" % (self.__class__,
                                               self.title,
                                               button_text)

class MessageBoxDialog(Dialog):
    """Show the user some info in a dialog box.  The only button is
    Okay.  The callback is optional for a message box dialog.
    """
    def __init__(self, title, description):
        Dialog.__init__(self, title, description, [BUTTON_OK])

    def run(self, callback=None):
        Dialog.run(self, callback)

class ChoiceDialog(Dialog):
    """Give the user a choice of 2 options (Yes/No, OK/Cancel,
    Migrate/Don't Migrate, etc.)
    """
    def __init__(self, title, description, default_button, other_button):
        super(ChoiceDialog, self).__init__(title, description,
                                           [default_button, other_button])
class DatabaseErrorDialog(ChoiceDialog):
    """ChoiceDialog for that we show when we see a database error.

    Frontends should call app.db_error_handler.run_backend_dialog() instead
    of running the normal code.
    """
    def __init__(self, title, description):
        super(DatabaseErrorDialog, self).__init__(title, description,
                                                  BUTTON_RETRY, BUTTON_QUIT)

class ThreeChoiceDialog(Dialog):
    """Give the user a choice of 3 options (e.g. Remove entry/
    Delete file/Cancel).
    """
    def __init__(self, title, description, default_button, second_button,
                 third_button):
        super(ThreeChoiceDialog, self).__init__(title, description,
                                                [default_button,
                                                 second_button,
                                                 third_button])

class HTTPAuthDialog(Dialog):
    """Ask for a username and password for HTTP authorization.
    Frontends should create a dialog with text entries for a username
    and password.  Use prefill_user and prefill_password for the initial
    values of the entries.

    The buttons are always BUTTON_OK and BUTTON_CANCEL.
    """
    def __init__(self, location, realm, prefill_user=None,
            prefill_password=None):
        desc = _(
            '%(authtype)s %(url)s requires a username and password for '
            '"%(realm)s".',
            {'authtype': location[0], 'url': location[1], 'realm': realm})
        super(HTTPAuthDialog, self).__init__(_("Login Required"), desc,
                                             (BUTTON_OK, BUTTON_CANCEL))
        self.prefill_user = prefill_user
        self.prefill_password = prefill_password

    def run_callback(self, choice, username='', password=''):
        self.username = username
        self.password = password
        super(HTTPAuthDialog, self).run_callback(choice)

class TextEntryDialog(Dialog):
    """Like the ChoiceDialog, but also contains a textbox for the user
    to enter a value into.  This is used for things like the create
    playlist dialog, the rename dialog, etc.
    """
    def __init__(self, title, description, default_button, other_button,
                 prefill_callback=None, fill_with_clipboard_url=False):
        super(TextEntryDialog, self).__init__(title, description,
                                              [default_button, other_button])
        self.prefill_callback = prefill_callback
        self.fill_with_clipboard_url = fill_with_clipboard_url

    def run_callback(self, choice, value=None):
        self.value = value
        super(TextEntryDialog, self).run_callback(choice)

class CheckboxDialog(Dialog):
    """Like the ChoiceDialog, but also contains a checkbox for the
    user to enter a value into.  This is used for things like asking
    whether to show the dialog again.  There's also a mesage for the
    checkbox and an initial value.
    """
    def __init__(self, title, description, checkbox_text, checkbox_value,
                 default_button, other_button):
        super(CheckboxDialog, self).__init__(title, description,
                                             [default_button, other_button])
        self.checkbox_text = checkbox_text
        self.checkbox_value = checkbox_value

    def run_callback(self, choice, checkbox_value=False):
        self.checkbox_value = checkbox_value
        super(CheckboxDialog, self).run_callback(choice)

class CheckboxTextboxDialog(CheckboxDialog):
    """Like ``CheckboxDialog`` but also with a text area. Used for
    capturing bug report data.
    """
    def __init__(self, title, description, checkbox_text,
                 checkbox_value, textbox_value, default_button, other_button):
        super(CheckboxTextboxDialog, self).__init__(title, description,
                                                    checkbox_text,
                                                    checkbox_value,
                                                    default_button,
                                                    other_button)
        self.textbox_value = textbox_value

    def run_callback(self, choice, checkbox_value=False, textbox_value=""):
        self.textbox_value = textbox_value
        super(CheckboxTextboxDialog, self).run_callback(choice, checkbox_value)
