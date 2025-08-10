#!/usr/bin/env python3
import atexit
import functools
import queue
import ssl
import time

import Adafruit_BBIO.GPIO as GPIO
import irc.bot
import irc.connection
import irc.strings

import config

def levelmap(level: int) -> str:
    return "OPEN" if level else "CLOSED"
    

class DoorBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port, password):
        context = ssl.create_default_context()
        wrapper = functools.partial(context.wrap_socket, server_hostname=server)
        ssl_factory = irc.connection.Factory(wrapper=wrapper)
        super().__init__([(server, port, password)], nickname, nickname, connect_factory=ssl_factory)

        self.channel = channel
        self._events = queue.Queue()
        self._last_msg = None
        self._last_msg_ts = 0.0

        GPIO.setup(config.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(config.pin, GPIO.BOTH, callback=self._gpio_callback, bouncetime=config.bounce_ms)

        atexit.register(GPIO.cleanup)

    # ---- IRC lifecycle ----
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self._schedule_event_pump()

    def _schedule_event_pump(self):
        # run _pump_events after EVENT_POLL_SEC (re-schedules itself)
        self.reactor.scheduler.execute_after(config.event_poll_sec, self._pump_events)


    def _pump_events(self):
        # drain all queued GPIO events and act on them
        try:
            while True:
                level, when = self._events.get_nowait()
                msg = f"Switch {levelmap(level)}"
                now = time.monotonic()
                if not (msg == self._last_msg and (now - self._last_msg_ts) < config.dedup_window_sec):
                    self.connection.privmsg(self.channel, msg)
                    self._last_msg = msg
                    self._last_msg_ts = now
        except queue.Empty:
            pass
        finally:
            # reschedule the next pump
            self.reactor.scheduler.execute_after(config.event_poll_sec, self._pump_events)

    # ---- GPIO -> queue ----
    def _gpio_callback(self, _pin):
        # note to self, these run in a separate thread
        try:
            level = GPIO.input(config.pin)
            self._events.put((level, time.monotonic()))
        except Exception as ex:
            # todo: log to console/file
            pass

    # ---- Commands ----
    def on_pubmsg(self, c, e):
        msg = irc.strings.lower(e.arguments[0])
        nick = e.source.nick
        
        if msg == "!door" and nick != config.nick:
            level = GPIO.input(config.pin)
            c.privmsg(self.channel, f"Deadbolt is {levelmap(level)}")

        if msg == "!help" and nick != config.nick:
            c.privmsg(self.channel, "I support the following commands:  !door")

def main():
    channel = config.channel
    nickname = config.nick
    password = config.serverpw
    server = config.server
    port = 6697

    bot = DoorBot(channel, nickname, server, port, password)
    bot.start()

if __name__ == "__main__":
    main()
