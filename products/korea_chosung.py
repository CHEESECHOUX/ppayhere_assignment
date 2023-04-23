import re

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ',
                'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


def get_chosung(word):
    chosung_word = ''
    for ch in word:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', ch):
            chosung = ord(ch) - 44032
            chosung = int(chosung / 588)
            if chosung < 0 or chosung >= len(CHOSUNG_LIST):
                return ''
            chosung_word += CHOSUNG_LIST[chosung]
        else:
            chosung_word += ch
    return chosung_word
