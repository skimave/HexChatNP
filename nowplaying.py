# -*- coding: UTF-8 -*-
import dbus
import hexchat
__module_name__ = "Now Playing"
__module_version__ = "0.1"
__module_description__ = "Tells the IRC channel what you are playing via D-bus interface"

def get_mpris_players():
    session_bus = dbus.SessionBus()
    return [service for service in session_bus.list_names() if service.startswith("org.mpris.MediaPlayer2.")]

def find_active_player():
    players = get_mpris_players()
    for player in players:
        status = get_playback_status(player)
        if status == "Playing":
            return player
    return False

def get_playback_status(player_name):
    session_bus = dbus.SessionBus()
    try:
        player_bus = session_bus.get_object(player_name, "/org/mpris/MediaPlayer2")
        player_properties = dbus.Interface(player_bus, "org.freedesktop.DBus.Properties")
        return player_properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
    except dbus.exceptions.DBusException:
        return None

def get_media_info(word, wordeol, userdata):
    channel = hexchat.get_info("channel")
    session_bus = dbus.SessionBus()
    try:
        active_player = find_active_player()
        if active_player is False:
            print("Nothing is playing at the moment.")
            return hexchat.EAT_ALL 
        media_bus = session_bus.get_object(active_player, "/org/mpris/MediaPlayer2")
        media_properties = dbus.Interface(media_bus, "org.freedesktop.DBus.Properties")
        metadata = media_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        artist = metadata['xesam:artist'][0] if metadata['xesam:artist'] else "Unknown Artist"
        # Handle YouTube "topic" channels
        if "- Topic" in artist:
            artist = artist.replace("- Topic", "")
        title = metadata['xesam:title'] if metadata['xesam:title'] else "Unknown Title"

        #Let's use only title and artist
        playing_string =  f"Now playing: {title} - {artist}"
        # TODO Add youtube search logic here if needed
        hexchat.command(f"MSG {channel} {playing_string}")
        return hexchat.EAT_ALL
    except dbus.exceptions.DBusException:
        hexchat.prnt("Nothing is playing at the moment")
        return hexchat.EAT_ALL

hexchat.hook_command('np', get_media_info, help="Sends to the current channel what music is playing at your DBUS interface")
