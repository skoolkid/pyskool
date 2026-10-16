import pytest

from pyskooltest import pygame  # Imported without pygame's warnings
from pyskool.input import Keyboard

class Pygame:
    """Stand-ins for pygame.event.get() and pygame.key.get_pressed() that
    supply the given events and pressed keys, and record the order in which
    they're called."""
    def __init__(self, monkeypatch):
        self.events = []
        self.pressed_keys = ()
        self.calls = []
        monkeypatch.setattr(pygame.event, 'get', self.get_events)
        monkeypatch.setattr(pygame.key, 'get_pressed', self.get_pressed)

    def get_events(self):
        self.calls.append('event.get')
        events, self.events = self.events, []
        return events

    def get_pressed(self):
        self.calls.append('key.get_pressed')
        return self.pressed_keys

@pytest.fixture
def pg(monkeypatch):
    return Pygame(monkeypatch)

def _key_down(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)

def _key_downs(*keys):
    return [_key_down(key) for key in keys]

def test_init_pumps_event_queue(pg):
    # Creating a keyboard processes the event queue straight away
    pg.events = [_key_down(pygame.K_a)]
    pg.pressed_keys = (True,)
    keyboard = Keyboard()

    assert pg.calls == ['event.get', 'key.get_pressed']
    assert keyboard.key_down_events == _key_downs(pygame.K_a)
    assert not keyboard.got_quit()
    assert keyboard.pressed_keys == (True,)
    assert not keyboard.writing

def test_pump_with_no_events(pg):
    keyboard = Keyboard()
    pg.pressed_keys = (False, True)

    keyboard.pump()
    assert keyboard.key_down_events == []
    assert not keyboard.got_quit()
    assert keyboard.pressed_keys == (False, True)

def test_pump_collects_key_down_events(pg):
    # Key-down events are collected in the order they occurred; other events
    # (such as key-up events and mouse movements) are ignored
    keyboard = Keyboard()
    pg.events = [
        _key_down(pygame.K_q),
        pygame.event.Event(pygame.KEYUP, key=pygame.K_q),
        pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0)),
        _key_down(pygame.K_o),
        _key_down(pygame.K_q)
    ]

    keyboard.pump()
    assert keyboard.key_down_events == _key_downs(pygame.K_q, pygame.K_o, pygame.K_q)
    assert not keyboard.got_quit()

def test_pump_with_quit_event(pg):
    # A quit event (the window close button was clicked) is noted, and any
    # key-down events are still collected
    keyboard = Keyboard()
    pg.events = [_key_down(pygame.K_a), pygame.event.Event(pygame.QUIT), _key_down(pygame.K_b)]

    keyboard.pump()
    assert keyboard.got_quit()
    assert keyboard.key_down_events == _key_downs(pygame.K_a, pygame.K_b)

def test_pump_resets_state(pg):
    # Each pump discards the key-down events and quit event collected by the
    # previous one
    keyboard = Keyboard()
    pg.events = [_key_down(pygame.K_a), pygame.event.Event(pygame.QUIT)]
    keyboard.pump()
    assert keyboard.got_quit()

    keyboard.pump()
    assert keyboard.key_down_events == []
    assert not keyboard.got_quit()

def test_pump_gets_pressed_keys_after_clearing_event_queue(pg):
    # The pressed keys are collected after the event queue has been cleared
    # (otherwise keys may appear to "stick")
    keyboard = Keyboard()
    pg.calls.clear()
    pg.pressed_keys = (True, False)

    keyboard.pump()
    assert pg.calls == ['event.get', 'key.get_pressed']
    assert keyboard.pressed_keys == (True, False)

def test_pump_while_writing(pg):
    # Pumping the event queue while Eric is writing on a blackboard collects
    # key-down events as usual, and doesn't stop him writing
    keyboard = Keyboard()
    keyboard.start_writing()
    pg.events = [_key_down(pygame.K_e)]

    keyboard.pump()
    assert keyboard.key_down_events == _key_downs(pygame.K_e)
    assert keyboard.writing
