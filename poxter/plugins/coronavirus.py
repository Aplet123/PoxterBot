import asyncio

import nacre

import hangups

import requests

from bs4 import BeautifulSoup

class CoronavirusSession:

    equivalent = {
        "China": ["People's Republic of China", "PRC", "P.R.C."],
        "USA": ["United States", "United States of America", "U.S.A.", "US", "U.S."],
        "S. Korea": ["South Korea", "S Korea"],
        "UK": ["United Kingdom", "United Kingdom of Great Britain and Northern Ireland", "U.K."],
        "Diamond Princess": ["Cruise Ship"],
        "UAE": ["United Arab Emirates", "Emirates", "U.A.E."],
        "North Macedonia": ["Macedonia"],
        "DRC": ["Democratic Republic of the Congo", "D.R.C."],
        "CAR": ["Central African Republic", "C.A.R."],
        "St. Vincent Grenadines": ["St. Vincent and the Grenadines", "St. Vincent"],
        "District of Columbia": ["Washington DC", "Washington D.C.", "DC", "D.C."]
    }
    urls = ['https://www.worldometers.info/coronavirus/',
            'https://www.worldometers.info/coronavirus/country/us/']

    def __init__(self, poxter, config):
        self.poxter = poxter
        self.hangouts = self.poxter.hangouts
        self.config = config
        self.buildHandle()

    def build(self):
        pass

    def buildHandle(self):
        messageFilter = nacre.handle.newMessageFilter(
            "^{}coronavirus(\s[a-zA-Z\.'\s]*)?$".format(self.poxter.config['format']))
        async def handle(update):
            if nacre.handle.isMessageEvent(update):
                event = update.event_notification.event
                if messageFilter(event):
                    await self.respond(event)
        self.poxter.updateEvent.addListener(handle)

    def parseInput(self, text):
        if len(text) == 12:
            return ""
        return text[13:].strip()

    def parseTag(self, tag):
        text = tag.contents[0]
        if str(text).startswith('<a') or str(text).startswith('<span'):
            text = text.contents[0]
        return text.strip()

    def scrapePage(self, soup, target):
        table = soup.findAll('tbody')[0]
        for row in table.findAll('tr'):
            col = row.findAll('td')
            title = self.parseTag(col[0])
            if target.lower() == title.lower() or (title in self.equivalent and target.lower() in [x.lower() for x in self.equivalent[title]]):
                return self.parseTag(col[0]) + " active cases: " + self.parseTag(col[6])
        return None

    def getCases(self, text):
        loc = self.parseInput(text)

        for url in self.urls:
            response = requests.get(url)
            if str(response) != "<Response [200]>":
                return "Unable to access data"
            soup = BeautifulSoup(response.text, 'html.parser')

            if url == self.urls[0] and (loc == "" or loc.lower() == "total" or loc.lower() == "world"):
                tag = soup.findAll('div')[30]
                return "Total active cases: " + self.parseTag(tag)

            cases = self.scrapePage(soup, loc)
            if cases:
                return cases

        return "No case number available for " + loc

    async def respond(self, event):
        message = self.getCases(hangups.ChatMessageEvent(event).text)
        conversation = self.hangouts.getConversation(event=event)
        await self.hangouts.send(message, conversation)

def load(poxter, config):
    return CoronavirusSession(poxter, config)