"""Generates the _2024/transformers data in _lib/data/2024/transformers/data/ (in the original they lived
in Grant's output folder, Path(get_output_dir(), "2024/transformers/data/")). The scenes
that read them change DATA_DIR to Path(get_directories()["data"], "2024/transformers/data/").

- glove-wiki-gigaword-50 (+ .vectors.npy): the 50-dimensional GloVe vectors (Stanford NLP,
  PDDL license), downloaded with gensim.downloader and saved as KeyedVectors, as
  embedding.get_word_to_vec_model does. About 66 MB of download (~/gensim-data is reused if already there).
- tale_of_two_cities.txt: Dickens's book (public domain), from Project Gutenberg (#98).
- facts.txt, pile_of_text.txt, athlete_sports.txt, murder_story.txt, harry_potter_3.txt:
  placeholder texts written for this conversion. harry_potter_3.txt only keeps what the
  code needs from the original (it starts with "Harry Potter was a highly unusual boy", ends with
  "Professor Snape" and has more than 2474 visible characters); the rest is original text.
  murder_story.txt has the sentences the scene looks for ("It was a dark and stormy night.",
  "therefore, the murderer was", "Derek!"").

Usage: python make_transformers_data.py [--no-download]"""
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
OUT = LIB / "data" / "2024" / "transformers" / "data"

GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/98/pg98.txt"
GLOVE = "glove-wiki-gigaword-50"

FACTS = """\
Michael Jordan plays basketball
The Eiffel Tower is in Paris
Water boils at 100 degrees Celsius at sea level
The Pacific is the largest ocean on Earth
Mount Everest is the tallest mountain above sea level
The human heart has four chambers
Light from the Sun takes about eight minutes to reach Earth
Honey never spoils if it is kept sealed
Octopuses have three hearts
The Great Wall of China is thousands of kilometers long
Jupiter is the largest planet in the Solar System
A triangle's angles add up to 180 degrees
Penguins live almost exclusively in the Southern Hemisphere
The Amazon rainforest spans nine countries
Shakespeare wrote Hamlet
The speed of sound in air is about 343 meters per second
Bananas are botanically berries
The Moon has no atmosphere to speak of
DNA has the shape of a double helix
Tokyo is the capital of Japan
Diamonds are made of carbon
The chess knight moves in an L shape
Venus spins in the opposite direction to most planets
Sharks existed before trees
A year on Mercury lasts 88 Earth days
Ada Lovelace wrote one of the first computer programs
The Nile flows north into the Mediterranean
Glass is made mostly from sand
Hummingbirds can fly backwards
Pi is irrational
"""

PILE = """\
Preheat the oven to 180 degrees and grease a round cake tin.
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
Breaking: local team wins the championship after a dramatic overtime.
The meeting has been moved to Thursday at 3pm, please update your calendars.
Once upon a time, in a village at the edge of a great forest, lived a clockmaker.
Theorem. Every bounded monotone sequence of real numbers converges.
Customer review: arrived on time, works as described, would buy again.
To install the package, run pip install and restart your terminal.
The mitochondria is the powerhouse of the cell.
Dear hiring manager, I am writing to apply for the position of research assistant.
Stir the onions slowly until they turn golden brown.
Weather forecast: scattered showers in the morning, clearing by the afternoon.
SELECT name, age FROM users WHERE age > 30 ORDER BY name;
The committee approved the budget with a vote of seven to two.
In 1969, two astronauts walked on the surface of the Moon.
Q: What is the capital of Australia? A: Canberra.
The quick brown fox jumps over the lazy dog.
Remember to water the tomatoes twice a week during the summer.
Chapter 3. The storm reached the harbor just before midnight.
Error: file not found. Check the path and try again.
The derivative of the sine function is the cosine function.
Thanks for your order! Your package will ship within two business days.
She looked out the window and wondered whether the train would ever come.
Abstract. We study the convergence of gradient descent on overparameterized networks.
Mix the flour, sugar and salt, then add the butter in small cubes.
The museum opens at nine and closes at five on weekdays.
for i in range(10): print(i ** 2)
Photosynthesis converts light energy into chemical energy.
The defendant pleaded not guilty to all charges.
Turn left at the second traffic light and continue for two kilometers.
A prime number has exactly two positive divisors.
The orchestra tuned their instruments as the audience took their seats.
Battery low. Connect your device to a charger.
He had never seen so many stars in a single night.
Interest rates are expected to remain unchanged this quarter.
The recipe serves four people and takes about forty minutes.
Lemma 2. If f is continuous on a closed interval, then f is bounded.
Our hiking trail climbs 600 meters over the first five kilometers.
Please keep your seatbelt fastened while the sign is illuminated.
The cat knocked a glass off the table and looked entirely unbothered.
git commit -m "Fix off by one error in the parser"
The library will be closed on Monday for the public holiday.
Vaccines train the immune system to recognize specific pathogens.
The novel follows three generations of a family of lighthouse keepers.
Add salt to taste and serve warm with fresh bread.
Scientists discovered a new species of frog in the cloud forest.
The function returns None if the key is missing.
Our quarterly revenue grew by twelve percent year over year.
It was the first snowfall of the year, and the streets were silent.
The ratio of a circle's circumference to its diameter is constant.
Tickets go on sale Friday at 10am.
The volcano last erupted more than three hundred years ago.
Sort the list in place, then remove duplicates.
The bridge was designed to sway slightly in strong winds.
Please find the attached report and let me know if you have questions.
Bees communicate the location of flowers through a waggle dance.
The final exam covers chapters one through eight.
Whisk the eggs until light and fluffy.
The train to the airport leaves every fifteen minutes.
A good proof is one that makes the result feel inevitable.
"""

ATHLETES = """\
Michael Jordan plays basketball
Serena Williams plays tennis
Lionel Messi plays soccer
Tom Brady plays football
Usain Bolt competes in sprinting
Simone Biles competes in gymnastics
Tiger Woods plays golf
Wayne Gretzky played hockey
Babe Ruth played baseball
Michael Phelps competes in swimming
"""

MURDER_STORY = """\
It was a dark and stormy night. The wind hammered the shutters of Ashgrove Manor, and the lights \
flickered twice before steadying. In the library, seven guests waited for a dinner that would never \
be served, because their host, old Mr. Whitlow, had not come down from his study.

The butler found him at a quarter past eight, slumped over his desk with an untouched cup of tea at \
his elbow. The window was latched from the inside, the door had been locked, and the only key hung \
on a ribbon around the dead man's neck.

Inspector Hale arrived an hour later, soaked to the bone and in no mood for riddles. He listened to \
each guest in turn. The niece had argued with her uncle about money. The doctor had been seen leaving \
the kitchen with a small brown bottle. The gardener swore he had spent the whole evening in the shed.

Then there was Derek, the quiet secretary, who had typed every one of Mr. Whitlow's letters for \
twenty years. He spoke softly, answered every question, and kept glancing at the clock on the mantel, \
as if he were late for something.

Hale walked the corridors until midnight. He measured the window, weighed the key, and sniffed the \
cold tea. He noted that the clock in the study ran exactly eleven minutes slow, and that someone had \
recently wound it.

At dawn he gathered everyone in the library. The tea had been poisoned after the door was locked, he \
explained, which meant the poison had been placed in the cup long before, by someone who knew the old \
man's habits better than anyone. The slow clock had given that person an alibi.

"Only one of you knew when he would drink it, and only one of you wound that clock," Hale said, \
turning slowly toward the fireplace. "And therefore, the murderer was Derek!"
"""

PASSAGE = """\
Harry Potter was a highly unusual boy, at least according to everyone who lived on his street, and \
he had long since stopped arguing with them about it. Summer had arrived early that year, heavy and \
still, and the hedges along the road had been trimmed so neatly that they looked painted onto the \
pavement. Every morning the same car pulled out of the same driveway at the same minute, and every \
evening it returned, and in between nothing whatsoever seemed to happen.
Inside the house, he kept his books under a loose board beneath the bed, where nobody would think to \
look. He read them late at night by the light of a small torch, turning the pages slowly so the paper \
would not rustle. There was an essay due when term began, a long one, about a subject he found both \
fascinating and slightly ridiculous, and he had promised himself he would finish it before the end \
of July.
His aunt had other plans for his summer. There were windows to wash, a garden shed to sort, and an \
entire attic of boxes that apparently could not survive another year without being labelled. He \
carried the boxes down the narrow ladder one by one, sneezing at the dust, and stacked them in the \
hall according to a system that changed every afternoon. Some held old curtains, some held cracked \
plates, and one, which he was told never to open, rattled in a way that made the cat leave the room. \
In the evenings his cousin watched television at a volume that made the glasses in the cupboard hum, \
and his uncle read the newspaper aloud, complaining about every single article in turn, from the \
price of petrol to the weather in countries he had never visited and never intended to.
The essay did not cooperate. Each paragraph seemed to wander off in a direction of its own, and every \
time he crossed out a sentence, two more appeared to take its place. He wrote about candles that \
refused to stay lit, about old rules that nobody remembered making, and about the strange habit grown \
people had of insisting that nothing interesting had ever happened to them.
Outside, the street lamps buzzed and the moths circled them in patient loops. Somewhere a dog barked \
three times and then thought better of it. He put down his pen, rubbed his eyes, and counted the days \
until he could leave again: thirty one, if he did not count today, which he decided he would not.
The letters arrived the next morning, all at once, tapping at the window before the sun was properly \
up. One was from a friend who wrote mostly in capital letters, one was from a friend who wrote in \
very small and very tidy handwriting, and one was a printed list of the books he would need for the \
coming year. He read them all twice, grinning, and hid them with the others under the board.
By the afternoon the house had returned to its usual silence. He sat at the desk by the window and \
looked again at the unfinished essay, then at the list of books, then at the timetable that had come \
folded inside the last envelope. Most of it was exactly what he had expected. One line, however, made \
him groan out loud, because double lessons on a Monday morning meant two full hours in the cold stone \
room at the bottom of the stairs with his least favourite teacher, Professor Snape"""


def write_texts():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "facts.txt").write_text(FACTS.strip("\n"))
    (OUT / "pile_of_text.txt").write_text(PILE.strip("\n"))
    (OUT / "athlete_sports.txt").write_text(ATHLETES.strip("\n"))
    (OUT / "murder_story.txt").write_text(MURDER_STORY.strip("\n"))
    (OUT / "harry_potter_3.txt").write_text(PASSAGE)
    n_glyphs = len(re.sub(r"\s", "", PASSAGE))
    assert n_glyphs > 2474, n_glyphs


def fetch_tale_of_two_cities():
    path = OUT / "tale_of_two_cities.txt"
    if path.exists():
        return
    raw = urllib.request.urlopen(GUTENBERG_URL, timeout=60).read().decode("utf-8-sig")
    start = raw.index("*** START OF")
    start = raw.index("\n", start) + 1
    end = raw.index("*** END OF")
    path.write_text(raw[start:end].strip() + "\n")


def fetch_glove():
    path = OUT / GLOVE
    if path.exists():
        return
    # Uses gensim's cache (~/gensim-data or GENSIM_DATA_DIR); only downloads if it is not there
    import gensim.downloader
    model = gensim.downloader.load(GLOVE)
    model.save(str(path))


def main():
    write_texts()
    if "--no-download" not in sys.argv:
        fetch_tale_of_two_cities()
        fetch_glove()
    print("ok")


if __name__ == "__main__":
    main()
