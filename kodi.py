"""
Kodi plugin for errbot
"""
# pylint: disable=unused-argument,too-many-public-methods,no-self-use
from itertools import chain
from functools import wraps
import re

from errbot import BotPlugin, botcmd
from xbmcjson import XBMC, PLAYER_VIDEO


KODI_CONFIG = {
    'HOST': 'http://localhost/jsonrpc',
    'LOGIN': 'kodi',
    'PASSWORD': 'kodi',
}

def result(func):
    """
    Return the result value of a json/dict, if its present in the returned object.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Return the response text, if it exists.
        """
        response = func(*args, **kwargs)
        if isinstance(response, dict):
            if 'result' in response.keys():
                return response['result']
        else:
            return response
    return wrapper

def format_youtube(url):
    """Strip youtube video id and format it for kodi playing."""
    match = re.match(r'.*youtube.com/watch\?v=(.{11})', url)
    if match is None:
        raise ValueError('No youtube video found: %s' % url)
    video_id = match.group(1)
    prefix = "plugin://plugin.video.youtube/?action=play_video&videoid="
    return prefix + video_id

class Kodi(BotPlugin):
    """
    Interact with a networked XBMC or Kodi installation via errbot.
    """
    def configure(self, configuration):
        """Set the configuration for the kodi plugin."""
        if configuration is not None and configuration != {}:
            config = dict(chain(KODI_CONFIG.items(),
                                configuration.items()))
        else:
            config = KODI_CONFIG

        super(Kodi, self).configure(config)

    def load_config(self):
        """Create the .xbmc client."""
        self.xbmc = XBMC(
            self.config['HOST'], self.config['LOGIN'], self.config['PASSWORD']
        )

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return KODI_CONFIG

    @result
    @botcmd
    def kodi_message(self, message, args):
        """
        Send a message to be displayed on screen.
        """
        self.load_config()
        title = "%s says:" % message.frm
        return self.xbmc.GUI.ShowNotification(title=title, message=args)

    @result
    @botcmd
    def kodi_url(self, message, args):
        """
        Play a given url on kodi.
        """
        self.load_config()
        if 'youtube' in args:
            args = format_youtube(args)
        return self.xbmc.Player.Open(item={'file': args})

    @result
    @botcmd
    def kodi_volume(self, message, args):
        """Set the volume to a value from 0-100"""
        self.load_config()
        try:
            return self.xbmc.Application.SetVolume(volume=int(args))
        except TypeError:
            return "Volume must be set to an integer."""

    @result
    @botcmd
    def kodi(self, message, args):
        """
        Run commands on the configured kodi/xbmc instance:

        * ping
        * home
        * weather
        * scan
        * clean
        * mute
        * pause
        * play
        * stop
        * left
        * right
        * up
        * down
        * back
        * info
        * select

        """
        self.load_config()

        if args in dir(self):
            method = getattr(self, args)
            return method()
        else:
            return "Command %s unrecognized. %s" % (message, args)

    @botcmd
    def htpc(self, message, args):
        """Just a symlink for kodi."""
        return self.kodi(message, args)

    def home(self):
        """Navigate to the home screen."""
        return self.xbmc.GUI.ActivateWindow(window='home')

    def weather(self):
        """Navigate to the weather screen."""
        return self.xbmc.GUI.ActivateWindow(window='weather')

    def scan(self):
        """Scan the video library."""
        return self.xbmc.VideoLibrary.Scan()

    def clean(self):
        """Clean the video library."""
        return self.xbmc.VideoLibrary.Clean()

    def mute(self):
        """Mute the audio."""
        return self.xbmc.Application.SetMute({'mute': True})

    def unmute(self):
        """Unmute the audio."""
        return self.xbmc.Application.SetMute({'mute': False})

    def pause(self):
        """Pause/Unpause."""
        return self.xbmc.Player.PlayPause([PLAYER_VIDEO])

    def play(self):
        """Pause/Unpause."""
        return self.pause()

    def stop(self):
        """Stop the video."""
        return self.xbmc.Player.Stop([PLAYER_VIDEO])

    def left(self):
        """Hit the left button."""
        return self.xbmc.Input.Left()

    def right(self):
        """Hit the right button."""
        return self.xbmc.Input.Right()

    def up(self):
        """Hit the up button."""
        return self.xbmc.Input.Up()

    def down(self):
        """Hit the down button."""
        return self.xbmc.Input.Down()

    def back(self):
        """Hit the back button."""
        return self.xbmc.Input.Back()

    def info(self):
        """View the info for the currently selected item."""
        return self.xbmc.Input.Info()

    def select(self):
        """Select the current item."""
        return self.xbmc.Input.Select()

    def ping(self):
        """Returns pong if everything's working."""
        return self.xbmc.JSONRPC.Ping()
