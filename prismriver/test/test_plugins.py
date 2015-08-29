import logging
import random
from time import sleep
import unittest
import hashlib
import os

from prismriver.main import search_sync
from prismriver.struct import SearchConfig


class TestPlugins(unittest.TestCase):
    def check_plugin(self, plugin_id, artist, title, lyric_hashes):
        logging.basicConfig(format='%(asctime)s %(levelname)s [%(module)s] %(message)s', level=logging.DEBUG)

        config = self.get_search_config(plugin_id)
        result = search_sync(artist, title, config)

        self.assertEqual(1, len(result), 'Wrong songs count')
        self.assertEqual(len(lyric_hashes), len(result[0].lyrics), 'Wrong lyrics count')

        index = 0
        for lyric_hash in lyric_hashes:
            logging.debug('Lyric #{}:\n'.format(index) + result[0].lyrics[index])
            self.assertEqual(lyric_hash, self.get_md5(result[0].lyrics[index]),
                             'Different text in #{} lyrics'.format(index))
            index += 1

    def setUp(self):
        max_delay = int(os.getenv('PRISMRIVER_TEST_MAX_DELAY', '0'))
        delay = random.randint(0, max_delay)
        logging.debug('Wait {}sec. before executing test...'.format(delay))
        sleep(delay)

    def get_md5(self, value):
        return hashlib.md5(value.encode('utf-8')).hexdigest()

    def get_search_config(self, plugin_id):
        return SearchConfig(enabled_plugins=[plugin_id])

    def test_amalgama_01(self):
        self.check_plugin('amalgama',
                          'Modern Talking', "You're My Heart, You're My Soul",
                          ['7236c048b8f71ba1e7485136efba5abf',
                           '1aa073ad09ad5b3d10cc67e4d4060ab7',
                           '7b2a083cfbf7d20ad7e1b3749b229564'])

    def test_amalgama_02(self):
        self.check_plugin('amalgama',
                          'Modern Talking', 'China in Her Eyes (Rap Version)',
                          ['23b184a36effe86c42ec29e65fcbc512',
                           '9bc36b6bd9160f86f7378964d6267928',
                           'bbeccf0b9e0670bdcb4049aa38ae5f29'])

    def test_animelyrics_01(self):
        self.check_plugin('animelyrics',
                          'Yui Horie', 'ALL MY LOVE',
                          ['38f0889fce3c422d894d1e766e14f492',
                           'f474cf8ef4017fd9a2adda76c88bde2c',
                           '5636bb331d8d91da75c4477a78e0ae56'])

    def test_animelyrics_02(self):
        self.check_plugin('animelyrics',
                          'supercell', 'Kokuhaku',
                          ['12933b6f2b339d01b9b1bbb7228525c4',
                           'fa2bdfc06457002b0640ac4f6d782ced'])

    def test_animelyrics_03(self):
        self.check_plugin('animelyrics',
                          'Konomi Suzuki', 'Yume no Tsuzuki',
                          ['ddc2639d5ce46acfba260d38cc21a74a',
                           'c05345db62f58cff9ca2c9facf038d1e'])

    def test_animelyrics_04(self):
        self.check_plugin('animelyrics',
                          ' Luca Yumi', 'Truth',
                          ['b67b5b76497a3bf3dfde36c58f489279',
                           '68a292d2337da33f80bf80c8e01bc81f',
                           '680a12a7055ca78f51e9a3e80a9af8fd'])

    # def test_azlyrics_01(self):
    #     self.check_plugin('azlyrics',
    #                       'Modern Talking', "You're My Heart, You're My Soul",
    #                       ['c02cee74bc3d8bc20ed95e8ff5b39c13'])

    # def test_azlyrics_02(self):
    #     self.check_plugin('azlyrics',
    #                       'Modern Talking', "Atlantis Is Calling (S.O.S. For Love)",
    #                       ['4b826df521c5a9ca057796daa760b5b7'])

    def test_bopfm_01(self):
        self.check_plugin('bopfm',
                          'Modern Talking', "You're My Heart, You're My Soul",
                          ['aa7dac06fc6c3b820f588f8b0b702541'])

    # def test_chartlyrics_01(self):
    #     self.check_plugin('chartlyrics',
    #                       'James Brown', 'Prisoner of Love',
    #                       ['a4cc13ee79455148090068388b74b8cf'])

    def test_elyrics_01(self):
        self.check_plugin('elyrics',
                          'C.C. Catch', "V.i.p. (they're Calling Me Tonight)",
                          ['f841980a7040ff3733e41cf75f075b04'])

    def test_elyrics_02(self):
        self.check_plugin('elyrics',
                          'Dschinghis Khan', 'Pistolero',
                          ['4be7cef73596ded5201904c31b4ced91'])

    def test_jlyric_01(self):
        self.check_plugin('jlyric',
                          '宇多田ヒカル', 'Beautiful World',
                          ['0f8a63e0369675653f2c734a534555fe'])

    def test_jlyric_02(self):
        self.check_plugin('jlyric',
                          '浜崎あゆみ', 'Bold & Delicious',
                          ['87cdd3d59e867ece975a49c2129d3aa6'])

    def test_kget_01(self):
        self.check_plugin('kget',
                          'YUI', 'CHE.R.RY ～Bossa Live Version～',
                          ['7f96f730bf8b3181d203d2ca50bf2112'])

    def test_kget_02(self):
        self.check_plugin('kget',
                          'Groove Coverage', '7 years & 50 days (Cascada vs. Plazmatek Remix)',
                          ['7efbe88d207031795a16f85f5c2f2460'])

    def test_kget_03(self):
        self.check_plugin('kget',
                          '浜崎あゆみ', 'A Song for ××',
                          ['e06cfe45fa4e261ff92c30fd444ce39e'])

    def test_leoslyrics_01(self):
        self.check_plugin('leoslyrics',
                          'Groove Coverage', 'Moonlight Shadow [Extended Version]',
                          ['4d865496dfa31f0e5994d7c646af17d1'])

    def test_leoslyrics_02(self):
        self.check_plugin('leoslyrics',
                          'Ace of Base', "Never Gonna Say I'm Sorry [Long]",
                          ['f3e7fbdfd3c1bc85a21dad24188b75b4'])

    def test_letras_01(self):
        self.check_plugin('letras',
                          'Ayumi Hamasaki', 'Is This Love?',
                          ['8a8ffe4e08b0d438bc145eaff0a1eec5'])

    def test_letssingit_01(self):
        self.check_plugin('letssingit',
                          "Blackmore's Night", 'Shadow Of The Moon',
                          ['d41eb27d17ea1adcd1f1eabc7e27ce37'])

    def test_lololyrics_01(self):
        self.check_plugin('lololyrics',
                          'Daft Punk', 'Harder, Better, Faster, Stronger',
                          ['b97a0f09485238d5fb09780c44d54c51'])

    def test_lololyrics_02(self):
        self.check_plugin('lololyrics',
                          'Groove Coverage', 'Holy Virgin (Radio Edit)',
                          ['5348e8a8cb887b00ae918dffe518ed51'])

    def test_lyricalnonsense_01(self):
        self.check_plugin('lyricalnonsense',
                          'supercell', 'ワールドイズマイン',
                          ['e8ec2964d298caa61aeddb2e353ec574',
                           '57e83798afde4fc3aa0fdd65adf0012f',
                           '85cb77dbc3635102f118205672311ea8',
                           '7baa703eab3a32e76cc2c86f0a8e1c04'])

    # def test_lyricshuddle_01(self):
    #     self.check_plugin('lyricshuddle',
    #                       'Daft Punk', "One More Time (romanthony's Unplugged Version)",
    #                       ['9931445a1c03a8cc78745ffcba611691'])

    # def test_lyricshuddle_02(self):
    #     self.check_plugin('lyricshuddle',
    #                       'Daft Punk', "Harder, Better, Faster, Stronger (neptunes Remix)",
    #                       ['995db98bba775ccf4e8cbc97efd37e98'])

    def test_lyricsmania_01(self):
        self.check_plugin('lyricsmania',
                          'Ayumi Hamasaki', '(Miss)understood',
                          ['42029923f3f4a69d2c6b0b3525e387c1'])

    def test_lyricsmania_02(self):
        self.check_plugin('lyricsmania',
                          'Joe Esposito', 'You\'re The Best',
                          ['ee9de08277a90ad90f0caae8bcb2ae23'])

    def test_lyricsnmusic_01(self):
        self.check_plugin('lyricsnmusic',
                          'Joe Dassin', 'Le Moustique',
                          ['492a37b433c45767a589eefbec8060a3'])

    def test_lyricsreg_01(self):
        self.check_plugin('lyricsreg',
                          'Groove Coverage', '7 Years & 50 Days',
                          ['de1d69411a7e4eada406fdd48d32281e'])

    def test_lyricwiki_01(self):
        self.check_plugin('lyricwiki',
                          'Sound Holic', 'Grip & Break Down !!',
                          ['ea12362512264723fee26192a3ea53b5'])

    def test_lyricwiki_02(self):
        self.check_plugin('lyricwiki',
                          'Kalafina', 'Red Moon',
                          ['a2cf1a1d1b54145d262418d22cac9381',
                           '3a8a2b0b4ec438a9cef665b861ef0f43'])

    def test_lyricwiki_03(self):
        self.check_plugin('lyricwiki',
                          'Jeff Williams & Casey Lee Williams', 'Red Like Roses (Red Trailer)',
                          ['e27047e110f688d3b0a8ba8ea381f245'])

    def test_lyricwiki_04(self):
        self.check_plugin('lyricwiki',
                          "Blackmore's Night", 'Beyond The Sunset',
                          ['c68011d57b164ae6c719fcf116a31541'])

    def test_lyrster_01(self):
        self.check_plugin('lyrster',
                          'Groove Coverage', 'Damn!',
                          ['b7efbc6c5899c123e0459324c66732ac'])

    def test_lyrster_02(self):
        self.check_plugin('lyrster',
                          'Pink Floyd', 'The Wall (complete)',
                          ['5011d7e7a1a26480601237820e65ef4d'])

    def test_megalyrics_01(self):
        self.check_plugin('megalyrics',
                          'Joe Dassin', 'Salut',
                          ['6882d41054640c1c4e9749af1f08966f',
                           'f6a941fd3d5297f25062d3912bea3752'])

    def test_megalyrics_02(self):
        self.check_plugin('megalyrics',
                          'Rammstein', 'Du hast',
                          ['9776ed55e1c7ca636a2fb69721127dc5',
                           '91f572732889601128280fb06eac2a95'])

    def test_metrolyrics_01(self):
        self.check_plugin('metrolyrics',
                          'Ace of Base', "Never Gonna Say I'm Sorry",
                          ['69bc545282aabd9f4e0135c82eb9a803'])

    def test_metrolyrics_02(self):
        self.check_plugin('metrolyrics',
                          'Joe Dassin', "Et Si Tu N'existais Pas",
                          ['fd488f806589f80ee18db6a78c051035'])

    def test_nitrolyrics_01(self):
        self.check_plugin('nitrolyrics',
                          'C. C. Catch', "Can't Catch Me",
                          ['231af8f3447878ac33625e9e36c36047'])

    def test_nitrolyrics_02(self):
        self.check_plugin('nitrolyrics',
                          'Bad Boys Blue', 'A World Without You (michelle)',
                          ['ad1240f4f772fc36e5286c4a4f29f187'])

    def test_touhouwiki_01(self):
        self.check_plugin('touhouwiki',
                          'FELT', 'World Around Us',
                          ['49c8b1f1d35cc7627b9f163d2301ef58'])

    def test_touhouwiki_02(self):
        self.check_plugin('touhouwiki',
                          'ShibayanRecords', 'Fall In The Dark',
                          ['29f3f203077b522be3d5da484732d0f0',
                           '0d6849e8150afc2c529fa790b5531968',
                           'c0d7a18839b1da9c2236a63559c6d8a5'])

    def test_touhouwiki_03(self):
        self.check_plugin('touhouwiki',
                          'Shinra-bansho', '受け入れられない真実',
                          ['bf8cc305e81594b38d5b282b58e53d68',
                           'a7de7b5e4460d573c87feded75709bce',
                           '3b5ae103d34b8a1e5d782f8439b400ad'])

    def test_vagalume_01(self):
        self.check_plugin('vagalume',
                          'Ito Kanako', 'Hacking To The Gate',
                          ['34a5b44635a7aeaac6242fdac86198f5'])
