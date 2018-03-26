import urllib.request
import re
import sys


class WordReader:
    MEANING_URL = "https://dict.longdo.com/search/%s"

    @staticmethod
    def __get_url_content(url):
        fp = urllib.request.urlopen(url)
        content = fp.read().decode("utf8")
        fp.close()
        return content

    @staticmethod
    def get_phonetics(word):
        link = WordReader.CAMBRIDGE_URL % (word)
        html = WordReader.__get_url_content(link)
        pivot = 'class="phoneticspelling">'
        start = html.find(pivot)
        if start == -1:
            return ""
        end = html.find("</span>", start)
        phonetics = html[start + len(pivot) + 1: end - 1]
        phonetics = phonetics.replace('ˈ', '').replace('ˌ', '')
        if len(phonetics) == 0:
            return "@INVALID"

        start = 0
        while start < len(phonetics):
            char = phonetics[start:start + 2]
            if char in WordReader.VALID_IPA:
                start = start + 2
            else:
                char = phonetics[start:start + 1]
                if char in WordReader.VALID_IPA:
                    start = start + 1
                else:
                    print(phonetics, "phonetics error at", start)
                    return "@INVALID " + phonetics
        return phonetics

    @staticmethod
    def get_meanings(word):
        link = WordReader.MEANING_URL % (word)
        html = WordReader.__get_url_content(link)
        start = html.find('NECTEC')
        if (start == -1):
            return ""
        end = html.find('</table>', start)
        scope = html[start: end]

        start = 0
        pivot = 'HREF="search/%s"' % (word)
        meanings = []
        while True:
            start = scope.find(pivot, start)
            if start == -1:
                break
            start = scope.find('[', start)
            end = scope.find('</tr>', start)
            meaning = scope[start: end]
            meaning = re.sub(r'<[^>]*>', '', meaning)
            meaning = meaning.replace(' See also:', '')
            meaning = meaning.replace('[N]', '[n]').replace('[VI]', '[vi]').replace('[VT]', '[vt]').replace('[ADJ]', '[adj]').replace('[ADV]', '[adv]')
            sp = meaning.split(', Syn.')
            meanings.append(sp[0].replace(', ', ','))
            if len(sp) > 1:
                meanings.append('  syn.' + sp[1].replace(',', ';'))
        return meanings[:-1]

if len(sys.argv) > 1:
    words = sys.argv[1:]
    for word in words:
        print(word, "=", WordReader.get_meanings(word))
