import json
import os


class TranslationWorker:
    def __init__(self, session, chat):
        self.session = session
        self.Chats = chat
        self.available = os.listdir('translations')
        text = 'Available translations:'
        for i in self.available:
            text += ' ' + i.split('.')[0]
        
        print(text)
        self.translations = {}
        if self.available:
            for i in self.available:
                with open(f'translations/{i}', 'r') as file:
                    self.translations[i.split('.')[0]] = json.load(file)

        print('Translations loaded')

    def get_translation(self, data):
        try:
            return self.translations[self.get_lang(data)]
        except IndexError:
            return 1

    def get_labels(self):
        labels = {}
        for key, value in self.translations.items():
            labels[key] = value['label']

        return labels

    def get_lang(self, data):
        try:
            chat_id = data.chat.id
        except AttributeError:
            chat_id = data.message.chat.id

        lang = self.session.query(self.Chats.language).filter_by(chat_id=chat_id).first()[0]
        return lang
