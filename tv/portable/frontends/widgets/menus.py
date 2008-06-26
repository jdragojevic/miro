# Miro - an RSS based video player application
# Copyright (C) 2005-2008 Participatory Culture Foundation
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

"""Menu handling code."""

from miro import app
from miro import signals

action_handlers = {}
def lookup_handler(action_name):
    """For a given action name from miro.menubar, get a callback to handle it.
    Return None if no callback is found.
    """
    return action_handlers.get(action_name)

def action_handler(name):
    """Decorator for functions that handle menu actions."""
    def decorator(func):
        action_handlers[name] = func
        return func
    return decorator

@action_handler("Quit")
def on_quit():
    app.widgetapp.quit()

# group name -> list of MenuItem labels belonging to group
action_groups = {
        'FeedSelected': [
            'CopyChannelURL',
            'MailChannel',
        ],
        'FeedsSelected' : [
            'UpdateChannels',
        ],
        'PlayableSelected': [
            'PlayPauseVideo',
        ],
}

action_group_map = {}
for group, actions in action_groups.items():
    for action in actions:
        action_group_map[action] = group

def action_group_names():
    return action_groups.keys() + ['AlwaysOn']

def get_action_group_name(action):
    return action_group_map.get(action, 'AlwaysOn')

class MenuManager(signals.SignalEmitter):
    def __init__(self):
        signals.SignalEmitter.__init__(self)
        self.create_signal('enabled-changed')
        self.enabled_groups = set(['AlwaysOn'])

    def handle_feed_selection(self, selected_feeds):
        """Handle the user selecting things in the feed list.  selected_feeds
        is a list of ChannelInfo objects
        """
        self.enabled_groups = set(['AlwaysOn'])
        self.enabled_groups.add('FeedsSelected')
        if len(selected_feeds) == 1:
            self.enabled_groups.add('FeedSelected')
        self.emit('enabled-changed')

    def handle_playlist_selection(self, selected_playlists):
        self.enabled_groups = set(['AlwaysOn'])
        self.emit('enabled-changed')

    def handle_static_tab_selection(self, selected_static_tabs):
        self.enabled_groups = set(['AlwaysOn'])
        self.emit('enabled-changed')

    def handle_item_list_selection(self, selected_items):
        """Handle the user selecting things in the item list.  selected_items
        is a list of ItemInfo objects containing the current selection.
        """
        self.enabled_groups = set(['AlwaysOn'])
        for item in selected_items:
            if item.downloaded:
                self.enabled_groups.add('PlayableSelected')
        self.emit('enabled-changed')
