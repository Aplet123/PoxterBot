import asyncio

import nacre

import hangups

from os import listdir

class ImageSession:

    images = [f[:-4] for f in listdir("plugins/images")]

    def __init__(self, poxter, config):
        self.poxter = poxter
        self.hangouts = self.poxter.hangouts
        self.config = config
        self.buildHandle()

    def build(self):
        pass

    def buildHandle(self):
        exp = ('^{}(' + "|".join([i for i in self.images]) + ')$').format(self.poxter.config['format'])
        messageFilter = nacre.handle.newMessageFilter(exp)
        async def handle(update):
            if nacre.handle.isMessageEvent(update):
                event = update.event_notification.event
                if messageFilter(event):
                    await self.respond(event)
        self.poxter.updateEvent.addListener(handle)

    async def respond(self, event):
        conversation = self.hangouts.getConversation(event=event)
        await self.hangouts.sendImage(event, conversation)

def load(poxter, config):
    return ImageSession(poxter, config)
