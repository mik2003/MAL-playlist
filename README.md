# MAL-playlist
Welcome to MAL-playlist, a python tool to retrieve your MyAnimeList and automatically search for YouTube videos of opening and ending themes for every anime. All of the results are then saved into an HTML file. The hope was to directly make a YouTube playlist but that would require working with the YouTube API and I am really not bothered to do it ._.

## Usage
The program has some dependencies. To create the virtual environment run `pipenv sync` (you need [pipenv](https://pypi.org/project/pipenv/) installed and [Python 3.12](https://www.python.org/downloads/)).

To obtain your own anime list playlist, you need to change the "\_\_main\_\_.py" file, change the argument of the `html_encode` function to your username, then run the program.

When you run the program an HTML file with name "anime_playlist_{username}.html" is created. While the program is still running, progress is printed in the console.

For now, the program uses the MAL API only for retrieving individual anime information, because there are some inconsistences between the anime list retrieved through the API and the one scraped using selenium.

## See also
[Take a look at my MAL profile :)](https://myanimelist.net/profile/mik2003)
