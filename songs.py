import contextlib
with contextlib.redirect_stdout(None):
    from pygame import mixer
    
import requests
import sys
import os
from bs4 import BeautifulSoup


base_url = 'http://www.songspk.name'

def movie_finder(base_url, movie_name):
    found = False
    base="https://songspk.zone/browse/bollywood-albums-col"
    print ('Is that name right? Lemme check...\n')
    cond=True
    pgnum=1
    possible_matches = []
    while cond : 
        movie_list_url = ''.join([base,"/", movie_name[0].lower(), "?page=",str(pgnum)])
        print ("Searching Page number ",pgnum)
        response = requests.get(movie_list_url)
        parser = BeautifulSoup(response.content,"html.parser")
        webpage_check = parser.find('div',attrs={'class': 'archive-empty'})
        if webpage_check :
            break
        if pgnum > 25 :
            break
        pgnum+=1
        
        links = parser.findAll('a')
        
        for link in links:
            movie = link.text.replace("\n", "").replace("\t", "").replace("&nbsp;", "")
            movie_short_name = movie.split('-')[0].strip()
            if movie_name.lower() in movie_short_name.lower():
                possible_matches.append(link)
                found = True
    return found, possible_matches

def songs_finder(base_url, movie):
    print ('\nHere are the songs for your movie...\n')
    link_attrs = movie.get('href')
    songs_url = ''.join([base_url, link_attrs])
    #print(songs_url)
    res = requests.get(songs_url)
    parser = BeautifulSoup(res.content,"html.parser")
    songs=[]
    link = parser.find('div', attrs={'class': 'page-tracklist-body'})
    htag = link.findAll('h3')
    for kk in htag:
        songs.append(kk.find('a'))
    return songs


def download_song(song, dir_path):
    print ("\nDownloading {0}.mp3 Please wait...".format(song.text.replace("\n", "")))
    dirName = song.text.replace("\n", "").replace("\t", "").replace("&nbsp;", "")
    #print("Song name: ",dirName)
    #print("link is: ",song.get('href'))
    
    file_path = os.path.join(dir_path, (dirName + '.mp3'))
    
    
    download_url = ''.join([base_url, song.get('href').lower()])
   
    
    res = requests.get(download_url)
    parser = BeautifulSoup(res.content,"html.parser")
    song = parser.findAll('a',attrs={'class': 'btn btn-block btn-default'})[-1]
    link=song.get('href')
    #print("url is: ",link)


    with open(file_path, "wb") as f:
        #print ("Downloading %s" % file_path)
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            x=0
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(100 * dl / total_length)
                if done is x :
                    #sys.stdout.write("%d%%\t" % ( done) ,end ='\r')
                    sys.stdout.write("\r[%d]" % (done)) 
                    sys.stdout.flush()
                    x+=10


def main():
    while True:
        print ("=" * 80)
        print ("Hi! I am your Zinn Aladin :)    Let's Download Songs In A Jiffy")
        print ("=" * 80)

        movie_name = input("Enter the Movie Name: ")
        
        found = False

        if not movie_name:
            print ("Movie name cannot be empty")
            continue

        found, possible_matches = movie_finder(base_url, movie_name.lower())
        if found:
            print ('\nI got your back buddy!\n\nDownloading all the songs from "',movie_name.strip() ,'"')
            #Let user select a movie in case of multiple matches
            if len(possible_matches) > 1:
                print ('We have found multiple matches...')
                for num, single_match in enumerate(possible_matches):
                    print (num + 1, single_match.text.replace("\n", "").replace("\t", "").replace("&nbsp;", ""))
                try:
                    choice = int(input("Enter which movie you want to proceed with: ")) - 1
                    movie = possible_matches[choice]
                except (ValueError, IndexError):
                    print ('Inv')
                    continue
            else:
                movie = possible_matches[0]
            #Getting songs page for selected movie
            songs = songs_finder(base_url, movie)
            #Showing song list and asking user to select a song to download
            #print ('Following songs found...')
            for num, song in enumerate(songs):
                print (num + 1, song.text.replace("\n", "").replace("\t", "").replace("&nbsp;", ""))
            
            try:
                track_no = 0#int(input("Enter the song number you want to download(0 to download all): 22 for cancel "))

                resp = True #input("Do you want to create folder '%s'?(y)" %movie.text)
                if track_no is 22 :
                    continue
                if resp:
                    dir_path  = os.path.join(os.getcwd(), movie.text.replace("\n", "").replace("\t", "").replace("&nbsp;", "")) 
                    if os.path.isdir(dir_path):
                        print ("Directory '%s' already exist. Skipping..."%(dir_path))
                    else:
                        os.mkdir(dir_path)
                else:
                    dir_path = os.getcwd()
                if track_no == 0:
                    for song in songs:
                        #call downloader function
                        download_song(song, dir_path)
                else:
                    download_song(songs[track_no - 1], dir_path)
                mixer.init()
                mixer.music.load("music.mp3")
                mixer.music.play()
                print ('Download complete')

            except (ValueError, IndexError):
                mixer.init()
                mixer.music.load("music.mp3")
                mixer.music.play()
                print ('Done')
                #sys.exit(1)
        else:
            print ("Movie not found")

if __name__ == '__main__':
    main()
