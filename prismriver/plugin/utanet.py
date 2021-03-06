from prismriver.plugin.common import Plugin
from prismriver.struct import Song


class UtaNetPlugin(Plugin):
    ID = 'utanet'
    RANK = 9

    def __init__(self, config):
        super(UtaNetPlugin, self).__init__('Uta-Net', config)

    def search_song(self, artist, title):
        link = 'http://www.uta-net.com/search/?Aselect=2&Keyword={}'.format(
                self.prepare_url_parameter(title, delimiter='+'))

        page = self.download_webpage(link)

        if page:
            soup = self.prepare_soup(page)

            search_pane = soup.find('tbody')
            for item in search_pane.findAll('tr', recursive=False):
                tds = item.findAll('td', recursive=False)

                song_artist = tds[1].a.text
                song_title = tds[0].a.text
                song_id = tds[0].a['href'].split('/')[2]

                if self.compare_strings(artist, song_artist) and self.compare_strings(title, song_title):
                    song_link = 'http://www.uta-net.com/user/phplib/svg/showkasi.php?ID={}'.format(song_id)
                    song_xml = self.download_xml(song_link)
                    if song_xml:
                        lyric_pane = song_xml.find('g')

                        lyric = ''
                        for tag in lyric_pane.iter('text'):
                            if tag.text:
                                lyric += (tag.text + '\n')
                            else:
                                lyric += '\n'

                        return Song(song_artist, song_title, self.sanitize_lyrics([lyric]))
