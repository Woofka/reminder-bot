from __future__ import annotations
from typing import Optional, List
from db import PickleDB


db = PickleDB('data.pickle')


class Notification:
    def __init__(self, _id: int, text: str, cron: str):
        self._id = _id
        self._text = text
        self._cron = cron

    @property
    def id(self):
        return self._id

    @property
    def text(self):
        return self._text

    @property
    def cron(self):
        return self._cron

    @text.setter
    def text(self, new_text):
        update_ok = db.update(self._id, new_text, self._cron)
        if update_ok:
            self._text = new_text

    @cron.setter
    def cron(self, new_cron):
        update_ok = db.update(self._id, self._text, new_cron)
        if update_ok:
            self._cron = new_cron

    @classmethod
    def create(cls, text: str, cron: str) -> Optional[Notification]:
        tmp = db.create(text, cron)
        if tmp is None:
            return None
        return cls(tmp[0], tmp[1], tmp[2])

    @classmethod
    def get(cls, _id: int) -> Optional[Notification]:
        tmp = db.get(_id)
        if tmp is None:
            return None
        return cls(tmp[0], tmp[1], tmp[2])

    @classmethod
    def get_list(cls) -> List[Notification]:
        tmp_list = db.get_list()
        result = []
        for _id, text, cron in tmp_list:
            result.append(cls(_id, text, cron))
        return result

    def delete(self) -> bool:
        return db.delete(self._id)

    def __repr__(self):
        return f'<Notification: {self._id}, {self._text}, {self._cron}>'
