
# stage_text.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A looping info text
#

class TextLoop(list):

    def __init__(self, init_list=None):
        super(TextLoop, self).__init__()

        if init_list:
            self += init_list

        self._idx = 0

    def get_next(self):
        if not self:
            return

        self._idx += 1

        if self._idx == len(self):
            self._idx = 0

        return self[self._idx]

STAGE_TEXT = TextLoop([
    _(u"In 1978, the fastest computer in the world was the " \
      u"Cray 1 \N{EM DASH} it cost $7 million and weighed as " \
      u"much as an average elephant! Your Kano is about 4 " \
      u"times faster than the Cray 1. To keep it up to speed, " \
      u"we're downloading new games, apps and projects, and " \
      u"streamlining the computer's memory. This should take " \
      u"about 15 minutes. In the meantime, why not take a " \
      u"phone picture of your Kano? Send it to us at " \
      u"<b>hello@kano.me</b> and we'll share it with the " \
      u"world. You can also search for the white rabbit on " \
      u"<b>http://world.kano.me</b>"),

    _(u"Computers can learn new ideas quickly. Right now, " \
      u"we're updating the Updater tool. Once this step is " \
      u"finished, the Updater will relaunch. How do computers " \
      u"think? They are made of electrical switches, " \
      u"connected together in clever ways. If a switch is on, " \
      u"that means \"yes\" or \"1\"; if it's off, that means " \
      u"\"no\" or \"0\". These little yes-no switches become " \
      u"a binary code \N{EM DASH} for words, sounds, rules, " \
      u"and more. Your computer has over 10 million tiny " \
      u"switches, called transistors, in its brain. In your " \
      u"brain, these switches are cells called neurons. " \
      u"They're talking to each other right now."),

    _(u"Python is one of the world's most popular programming " \
      u"languages. A programming language takes words that " \
      u"humans can understand, and translates them into " \
      u"instructions that the computer's switches can " \
      u"understand. A good \"make a sandwich\" program would " \
      u"go through all the steps necessary to get the " \
      u"sandwich made, from \"grab bread\" to \"pick up " \
      u"knife\" to \"put it on a plate.\" The computer " \
      u"follows a program in Python the way a cook follows a " \
      u"recipe in English. Python code can build volcanos in " \
      u"Minecraft, grab \"Gangnam Style\" from YouTube, and " \
      u"move millions of dollars in the New York Stock " \
      u"Exchange."),

    _(u"The name \"Kano\" comes from Kan\N{LATIN SMALL LETTER O WITH MACRON} Jigor\N{LATIN SMALL LETTER O WITH MACRON}. He " \
      u"was a Japanese schoolteacher, inventor of the art of judo. " \
      u"His motto: Maximum efficiency, minimum effort. In " \
      u"Greek, Kano means \"I make\". (Kano is also the largest " \
      u"city in Northern Nigeria.) What makes Kano different to " \
      u"other computers? All of the ideas in its brain are open " \
      u"for you to see. Just visit <b>github.com/KanoComputing</b> " \
      u"to see the code. Kano can also change forms\N{HORIZONTAL ELLIPSIS} " \
      u"You can turn it into a robot, server, radio, and more. Visit " \
      u"<b>world.kano.me/projects</b> for powerup ideas. Want a look " \
      u"inside Kano HQ? Hang with our wizards at <b>blog.kano.me</b>"),

    _(u"Kano OS is an operating system, which means it " \
      u"connects all the programs together. This OS is based " \
      u"on Linux, whose code is open \N{EM DASH} that means " \
      u"that it's free for anyone to download, change or even " \
      u"sell. Its code is written by hobbyists and makers " \
      u"worldwide, not just professionals. Kano uses Debian, " \
      u"a fun and powerful \"distribution\" of Linux which " \
      u"the International Space Station also uses to run its " \
      u"robotic systems \N{EM DASH} to keep the astronauts " \
      u"from losing their lunch!"),

    _(u"We're almost done! With your Kano computer, you'll " \
      u"make awesome games, code your own music, stream " \
      u"videos around your house, tell stories, and much " \
      u"more. Your computer is open, and its powers are at " \
      u"your command. If you want to get new cool projects " \
      u"from us each week, join the community at"),

    _(u"Your Kano will now reboot!\n" \
      u"\n" \
      u"See you in a while\N{HORIZONTAL ELLIPSIS}")
])
