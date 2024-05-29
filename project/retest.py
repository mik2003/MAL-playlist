import re

# Define the regular expression pattern
pattern = (
    r"(?:#(?P<index>\d+):)?"
    + r"\s*\"(?P<name>[^\"]+)\""
    + r"\s*(?:by\s+(?P<artist>(?:(?!\s+\(ep).)+))?"
    + r"\s*(?:\((?P<episode>ep.+)\))?"
)

# Example string
string = '#1: "Sora no Mori de (\u7a7a\u306e\u68ee\u3067)" by Mami Kawada (\u5ddd\u7530\u307e\u307f) (eps 1-11)'

# Match the pattern
match = re.search(pattern, string)


# Extract the components
def extract_components(match):
    if match:
        name = match.group("name")
        artist = match.group("artist")
        episode = match.group("episode")
        return name, artist, episode
    return None, None, None


name, artist, episode = extract_components(match)

print(f"String 1 -> Name: {name}, Artist: {artist}, Episode: {episode}")
