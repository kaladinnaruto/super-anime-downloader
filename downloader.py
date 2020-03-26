import requests as REQ
from bs4 import BeautifulSoup as BS
import subprocess as SP
import re as REGEX

#-------------------------------------------
class Anime:
    def __init__(self, url):
        animeSoup = BS(REQ.get(url).text, 'html.parser')
        animeID = animeSoup.find(id="movie_id")['value']
        animeAlias = animeSoup.find(id="alias_anime")['value']
        animeLastEp = animeSoup.find(id="episode_page").find_all('a')[-1]['ep_end']
        #----private data members------
        self.__title = animeSoup.title.text.replace(" at Gogoanime", '')
        self.__mainpageURL = url
        self.__ajaxURL = "https://ajax.gogocdn.net/ajax/load-list-episode?ep_start=0&ep_end=" + animeLastEp + "&id=" + animeID + "&default_ep=0&alias=" + animeAlias
        self.__ajaxSoup = BS(REQ.get(self.__ajaxURL).text, 'html.parser')
        self.__eptotal = len(self.__ajaxSoup.find_all('a'))
        #------------------------------

    def getTitle(self):
        return self.__title
    def getURL(self):
        return self.__mainpageURL
    def getTotalEpisodeCount(self):
        return self.__eptotal

    def collectAllEpisodes(self):
        self.__episodeList = []
        for li in self.__ajaxSoup.find_all('li'):
            self.__episodeList.insert(0, Episode(self.__title + " - " + " ".join(li.text.split()), "https://www.gogoanime.io" + li.find('a')['href'].strip()))
    def collectEpisodes(self, start, end):
        self.__episodeList = []
        for li in self.__ajaxSoup.find_all('li')[-start:-(end+1):-1]:
            self.__episodeList.insert(0, Episode(self.__title + " - " + " ".join(li.text.split()), "https://www.gogoanime.io" + li.find('a')['href'].strip()))

    def downloadEpisodes(self):
        for episode in reversed(self.__episodeList):
            episode.download()
    def displayEpisodes(self):
        for ep in reversed(self.__episodeList):
            print(ep.getTitle())
    def displayDownloadLinks(self):
        for epis in reversed(self.__episodeList):
            epis.get_Mp4UploadDownloadLink()
    def playEpisodesOnline(self):
        pass
#-------------------------------------------
class Episode:
    def __init__(self, title, url):
        self.__title = title
        self.__url = url
        mp4ElementList = BS(REQ.get(url).text, 'html.parser').find_all('li', {'class':'mp4'})
        if len(mp4ElementList) is 0:
            self.__mp4uploadEmbed = "not_found"
        else:
            self.__mp4uploadEmbed = mp4ElementList[0].find('a')['data-video']

    def get_Mp4UploadDownloadLink(self):
        scripts = BS(REQ.get(self.__mp4uploadEmbed).text, 'html.parser').find_all('script', type="text/javascript")
        evalText = scripts[len(scripts)-1].text
        evalItems = evalText.split('|')
        del evalItems[:evalItems.index('navigator')+1]
        videoID = [a for a in evalItems if len(a)>30][0]
        #
        w3strPossiblesList = REGEX.findall(r'{|s\d{1,999}|}|{|www\d{1,999}|}', evalText)
        w3str = "www"
        if len(w3strPossiblesList) is not 0:
            w3str = max(w3strPossiblesList, key=len)
        #
        retstr = "https://" + w3str + ".mp4upload.com:" + evalItems[evalItems.index(videoID)+1] + "/d/" + videoID + "/video.mp4"
        print("Got:-", retstr)
        return retstr

    def getTitle(self):
        return self.__title
    def download(self):
        if self.__mp4uploadEmbed is "not_found":
            print("\n", "::: COULD NOT FIND ::: EPISODE:-", self.__title, "| Server=MP4-UPLOAD\n")
        else:
            print("===== DOWNLOADING EPISODE:", self.__title.replace(' ', '_'))
            options = " -x 10 --max-tries=5 --retry-wait=10 --check-certificate=false -d downloaded -o " + self.__title.replace(' ', '_') + ".mp4"
            SP.call(("aria2c " + self.get_Mp4UploadDownloadLink() + options).split())
#-------------------------------------------

###
#https://www16.gogoanime.io/category/sin-nanatsu-no-taizai-dub
#https://www16.gogoanime.io/sin-nanatsu-no-taizai-dub-episode-4
#https://ajax.gogocdn.net/ajax/load-list-episode?ep_start=0&ep_end=70&id=7451&default_ep=0&alias=douluo-dalu-2nd-season
###

def main():
    print("\n====================[ Gogoanime Downloader ]====================\n")
    theanime = Anime(input("\t - Enter Anime main-page URL: "))
    print(" -FOUND:", theanime.getTotalEpisodeCount(), " Episodes in TOTAL!")
    theanime.collectEpisodes(int(input("\t - Start From Episode:")), int(input("\t - End At Episode:")))
    #os.system("cls")
    print("\nStarting Download using aria2...\n")
    theanime.displayEpisodes()
    theanime.displayDownloadLinks()
    #theanime.downloadEpisodes()
    print("\n==================== DOWNLOAD FINISHED !!! ====================\n")

main()