# MAL-playlist
Welcome to MAL-playlist, a python tool to retrieve your MyAnimeList and automatically search for YouTube videos of opening and ending themes for every anime. All of the results are then saved into an HTML file. The hope was to directly make a YouTube playlist but that would require working with the YouTube API and I am really not bothered to do it ._.

## Usage
The program is packaged as a module and can be run with `py -m project` from within the repository directory.
The only external package used is [selenium](https://pypi.org/project/selenium/), so if you have it installed you can just run the program.
In this code, Firefox is used for selenium, so you need it installed, or you can change the code to your preferred browser in the `mal_search` function.
If you want to create a virtual environment run `pipenv sync` (you need [pipenv](https://pypi.org/project/pipenv/) installed and [Python 3.12](https://www.python.org/downloads/)).

To obtain your won anime list, you need to change the "__main__.py" file, at the bottom change `name` to your username, the integer (3rd argument) in the `html_encode` function describes how many of the YouTube search results will be saved in the HTML file.

When you run the program an HTML file with name "anime_playlist_{username}.html" is created. While the program is still running, progress is printed in the console.