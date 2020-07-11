import logging
import os.path
from collections.abc import Iterable


class Hasher:
    SEPARATORS = ('', '-', '_', '', '/', '.',)
    VOCABULARY_FILENAME = 'words_alpha.txt'

    def __init__(self, data, words_count=1, res_count=1, sep=''):

        self.data = data
        self.words_count = min(10, int(words_count) if isinstance(words_count, int) else 1)
        self.res_count = min(10, int(res_count) if isinstance(res_count, int) else 1)
        self.sep = sep if sep in Hasher.SEPARATORS else ''

        vocabulary_path = os.path.join(os.path.dirname(__file__), Hasher.VOCABULARY_FILENAME)
        vocabulary_path = os.path.normpath(vocabulary_path)
        with open(vocabulary_path) as voc_file:
            self.voc = voc_file.read().split()
            self.voc_count = len(self.voc)

        self._set_logger()

    def _set_logger(self):
        self.logger = logging.getLogger('hasher')
        self.logger.setLevel(logging.INFO)
        logger_handler = logging.StreamHandler()
        logger_handler.setLevel(logging.INFO)
        logger_formatter = logging.Formatter('%(name)s - %(message)s')
        logger_handler.setFormatter(logger_formatter)
        self.logger.addHandler(logger_handler)

    def log(self, msg):
        self.logger.info(msg)

    def _get_neighbors(self):
        for res_index in range(1, self.res_count + 1):
            words = [] if res_index > 1 else [self.base_word, ]
            for words_index in range(1, self.words_count + 1):
                curr_index = self.base_word_index + words_index
                try:
                    curr_word = self.voc[curr_index].capitalize()
                    words.append(curr_word)
                except IndexError as e:
                    self.log(f'Ошибка при обращении к слову по индексу {curr_index}: {e.args}')
                    break
            self.base_word_index = curr_index
            curr_words_as_str = self.sep.join(words)
            self.result.append(curr_words_as_str)

    def _hash(self, data):
        result = 0
        if not isinstance(data, Iterable):
            data = str(data)

        if isinstance(data, str) and len(data) == 1:
            result = ord(data)
            self.log(f'ord({data}) = {result}')
            return result

        if isinstance(data, Iterable):
            if isinstance(data, dict):
                for key, value in data.items():
                    result += self._hash(key)
                    result += self._hash(value)
                return result
            for item in data:
                result += self._hash(item)
            return result

        result = ord(str(data))
        self.log(f'ord({data}) = {result}')
        return result

    def get_result(self):
        self.result = []
        hash_sum = self._hash(self.data)
        self.base_word_index = hash_sum if hash_sum <= self.voc_count else self.voc_count // len(str(hash_sum))
        self.base_word = self.voc[self.base_word_index].capitalize()

        neighbors_required = self.words_count > 1 or self.res_count > 1
        if neighbors_required:
            neighbors = self._get_neighbors()

        self.log(f'result = {self.result}')
        return self.result


def main():
    data = {}
    data['str'] = 'this is a test input for my hasher'
    data['int'] = 100500
    data['list'] = ['one', 'two', 'three', {'key_1': 'aaa', 'key_2': 'bbb'},
                    ({'another': 'first'}, {'inner': 'next'}, {'object': 'last'})]

    hasher = Hasher(data=data, words_count=5, res_count=8, sep='/')
    hasher.get_result()


if __name__ == '__main__':
    main()
