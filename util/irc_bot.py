'''
  @file run_bot.py
  @author Marcus Edel

  IRC Bot send can send messages to a specified channel.
'''

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import irc.client
import jaraco.logging

class IRCBot(object):
  def __init__(self, channel, nickname, server, port=6667):

    self.reactor = irc.client.Reactor()

    self.messages = []
    self.channel = channel
    self.nickname = nickname
    self.server = server
    self.port = port

  def send_messages(self, messages):
    self.messages = messages

    try:
        c = self.reactor.server().connect(self.server, self.port, self.nickname)
    except irc.reactor.ServerConnectionError:
        print(sys.exc_info()[1])
        raise SystemExit(1)

    c.add_global_handler("welcome", self.on_connect)
    c.add_global_handler("join", self.on_join)
    c.add_global_handler("disconnect", self.on_disconnect)
    self.reactor.process_forever()

  def on_connect(self, connection, event):
    if irc.client.is_channel(self.channel):
      connection.join(self.channel)
      return
    self.main_loop(connection)

  def on_join(self, connection, event):
    self.main_loop(connection)

  def get_lines():
    while True:
      yield sys.stdin.readline().strip()

  def main_loop(self, connection):
    for message in self.messages:
      connection.send(message)
    connection.quit("Using irc.client.py")

  def on_disconnect(self, connection, event):
    raise SystemExit()
