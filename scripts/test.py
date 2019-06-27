from bs4 import BeautifulSoup

with open("../memorygame/game.html") as fp:
    soup = BeautifulSoup(fp, "lxml")

text = soup.find(id="text_default")

print text.contents[0]
