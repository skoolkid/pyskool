from unittest.mock import Mock

import pyskooltest  # Puts PYSKOOL_HOME on sys.path
from pyskool import sound

def _beeper(**sounds):
    """Return a Beeper with the given mock sound effects (keyed by ID) and no
    sounds directory."""
    beeper = sound.Beeper(None, {})
    beeper.sounds.update(sounds)
    return beeper

def test_play_unknown_sound():
    # The JUMP sound effect isn't loaded (e.g. because its file is missing),
    # so nothing is played, and the beeper isn't busy
    bell = Mock()
    beeper = _beeper(BELL=bell)

    assert beeper.play(sound.JUMP) is None
    bell.play.assert_not_called()
    assert beeper.channel is None
    assert not beeper.is_busy()

def test_play_in_suspend_mode():
    # Playing a sound effect in SUSPEND mode (the default) makes the beeper
    # keep hold of the channel it's playing on, so it's busy until the sound
    # effect has finished
    bell = Mock()
    channel = bell.play.return_value
    channel.get_busy.return_value = True
    beeper = _beeper(BELL=bell)

    beeper.play(sound.BELL)
    bell.play.assert_called_once_with()
    assert beeper.channel is channel
    assert beeper.is_busy()

    channel.get_busy.return_value = False
    assert not beeper.is_busy()
    assert beeper.channel is None

def test_play_in_async_mode():
    # Playing a sound effect in ASYNC mode doesn't make the beeper keep hold
    # of the channel it's playing on, so it isn't busy
    jump = Mock()
    jump.play.return_value.get_busy.return_value = True
    beeper = _beeper(JUMP=jump)

    beeper.play(sound.JUMP, sound.ASYNC)
    jump.play.assert_called_once_with()
    assert beeper.channel is None
    assert not beeper.is_busy()

def test_play_in_async_mode_during_suspend_mode_sound():
    # Playing a sound effect in ASYNC mode while one is playing in SUSPEND mode
    # leaves the beeper busy with the SUSPEND mode sound effect
    bell, jump = Mock(), Mock()
    bell_channel = bell.play.return_value
    bell_channel.get_busy.return_value = True
    beeper = _beeper(BELL=bell, JUMP=jump)

    beeper.play(sound.BELL, sound.SUSPEND)
    beeper.play(sound.JUMP, sound.ASYNC)
    bell.play.assert_called_once_with()
    jump.play.assert_called_once_with()
    assert beeper.channel is bell_channel
    assert beeper.is_busy()

def test_is_busy_with_no_channel():
    # No sound effect has been played in SUSPEND mode, so the beeper isn't busy
    beeper = _beeper()

    assert beeper.channel is None
    assert not beeper.is_busy()
    assert beeper.channel is None

def test_is_busy_while_channel_is_busy():
    # A sound effect is still playing in SUSPEND mode, so the beeper is busy,
    # and keeps hold of the channel for as long as it's playing
    channel = Mock()
    channel.get_busy.return_value = True
    beeper = _beeper()
    beeper.channel = channel

    assert beeper.is_busy()
    assert beeper.is_busy()
    assert channel.get_busy.call_count == 2
    assert beeper.channel is channel

def test_is_busy_after_channel_has_finished():
    # A sound effect played in SUSPEND mode has finished, so the beeper isn't
    # busy; it lets go of the channel, and doesn't check it again
    channel = Mock()
    channel.get_busy.return_value = False
    beeper = _beeper()
    beeper.channel = channel

    assert not beeper.is_busy()
    assert beeper.channel is None
    assert not beeper.is_busy()
    channel.get_busy.assert_called_once_with()

def test_pause_while_busy():
    # A sound effect is playing in SUSPEND mode, so pausing the beeper pauses
    # the channel it's playing on
    channel = Mock()
    channel.get_busy.return_value = True
    beeper = _beeper()
    beeper.channel = channel

    beeper.pause()
    channel.pause.assert_called_once_with()
    assert beeper.paused
    assert beeper.channel is channel

def test_pause_while_paused():
    # The beeper is already paused, so pausing it again does nothing
    channel = Mock()
    channel.get_busy.return_value = True
    beeper = _beeper()
    beeper.channel = channel

    beeper.pause()
    beeper.pause()
    channel.pause.assert_called_once_with()
    assert beeper.paused

def test_pause_with_no_channel():
    # No sound effect is playing in SUSPEND mode, so there's nothing to pause
    beeper = _beeper()

    beeper.pause()
    assert not beeper.paused

def test_pause_after_channel_has_finished():
    # The sound effect played in SUSPEND mode has finished, so there's nothing
    # to pause
    channel = Mock()
    channel.get_busy.return_value = False
    beeper = _beeper()
    beeper.channel = channel

    beeper.pause()
    channel.pause.assert_not_called()
    assert not beeper.paused
    assert beeper.channel is None

def test_unpause_while_paused():
    # The beeper was paused while a sound effect was playing in SUSPEND mode,
    # so unpausing it unpauses the channel the sound effect is playing on
    channel = Mock()
    channel.get_busy.return_value = True
    beeper = _beeper()
    beeper.channel = channel
    beeper.pause()

    beeper.unpause()
    channel.unpause.assert_called_once_with()
    assert not beeper.paused
    assert beeper.channel is channel

def test_unpause_while_unpaused():
    # The beeper was paused and then unpaused, so unpausing it again does
    # nothing
    channel = Mock()
    channel.get_busy.return_value = True
    beeper = _beeper()
    beeper.channel = channel
    beeper.pause()

    beeper.unpause()
    beeper.unpause()
    channel.unpause.assert_called_once_with()
    assert not beeper.paused

def test_unpause_while_not_paused():
    # A sound effect is playing in SUSPEND mode, but the beeper isn't paused,
    # so unpausing it does nothing
    channel = Mock()
    channel.get_busy.return_value = True
    beeper = _beeper()
    beeper.channel = channel

    beeper.unpause()
    channel.unpause.assert_not_called()
    assert not beeper.paused
