from prismriver.plugin.common import Plugin
from prismriver.struct import Song


class JLyricPlugin(Plugin):
    PLUGIN_ID = 'jlyric'

    def __init__(self, config):
        super(JLyricPlugin, self).__init__(self.PLUGIN_ID, 'J-Lyric', config)

    def search_song(self, artist, title):
        link = "http://search.j-lyric.net/index.php?kt={}&ct=0&ka={}&ca=0".format(
            self.prepare_url_parameter(title, delimiter='+'),
            self.prepare_url_parameter(artist))

        page = self.download_webpage(link)
        if page:
            soup = self.prepare_soup(page)

            lyric_list_pane = soup.find('div', {'id': 'lyricList'})
            if lyric_list_pane is None:
                return None

            artist_pane = lyric_list_pane.find('div', {'class': 'status'}).find('a')
            song_artist = artist_pane.text

            title_pane = lyric_list_pane.find('div', {'class': 'title'}).find('a')
            song_title = title_pane.text
            song_link = title_pane['href']

            lyric_page = self.download_webpage(song_link)
            soup = self.prepare_soup(lyric_page)

            lyric_pane = soup.find('p', {'id': 'lyricBody'})
            lyric = self.parse_verse_block(lyric_pane)

            return Song(song_artist, song_title, self.sanitize_lyrics([lyric]))
