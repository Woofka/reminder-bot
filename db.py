from typing import Optional, Tuple, List
import pickle
import os


class BaseDB:
    def create(self, text: str, cron: str) -> Optional[Tuple[int, str, str]]:
        raise NotImplementedError("Method create is not implemented")

    def get(self, _id: int) -> Optional[Tuple[int, str, str]]:
        raise NotImplementedError("Method get is not implemented")

    def get_list(self) -> List[Tuple[int, str, str]]:
        raise NotImplementedError("Method get_list is not implemented")

    def update(self, _id: int, text: str, cron: str) -> bool:
        raise NotImplementedError("Method update is not implemented")

    def delete(self, _id: int) -> bool:
        raise NotImplementedError("Method delete is not implemented")


class PickleDB(BaseDB):
    def __init__(self, path: str):
        if not os.path.exists(os.path.abspath(os.path.dirname(path))):
            raise FileNotFoundError(f'Some directories in path {path} don\'t exist')

        self._path = path
        self._data = {
            'next_id': 0,
            'data': {}
        }

        self._load()

    @property
    def _enrties(self):
        return self._data['data']

    @property
    def _next_id(self):
        return self._data['next_id']

    def _inc_next_id(self):
        self._data['next_id'] += 1

    def _load(self):
        if os.path.exists(self._path):
            with open(self._path, 'rb') as f:
                self._data = pickle.load(f)

    def _save(self):
        with open(self._path, 'wb') as f:
            pickle.dump(self._data, f)

    def create(self, text: str, cron: str) -> Optional[Tuple[int, str, str]]:
        self._enrties[self._next_id] = (text, cron)
        _id = self._next_id
        self._inc_next_id()
        self._save()
        return _id, text, cron

    def get(self, _id: int) -> Optional[Tuple[int, str, str]]:
        entry = self._enrties.get(_id, None)
        if entry is None:
            return None
        return _id, entry[0], entry[1]

    def get_list(self) -> List[Tuple[int, str, str]]:
        result = []
        for _id, (text, cron) in self._enrties.items():
            result.append((_id, text, cron))
        return result

    def update(self, _id: int, text: str, cron: str) -> bool:
        if _id not in self._enrties:
            return False
        self._enrties[_id] = (text, cron)
        self._save()
        return True

    def delete(self, _id: int) -> bool:
        if _id not in self._enrties:
            return False
        del self._enrties[_id]
        self._save()
        return True
