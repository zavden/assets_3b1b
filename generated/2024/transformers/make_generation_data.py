"""Data for the SYNTHETIC language model that replaces GPT-2 / GPT-3 in the scenes of
_2024/transformers/{chm,generation,auto_regression,old_auto_regression,supplements}.py.

In the original, `gpt2_predict_next_token` loads GPT-2's weights (transformers) and
`gpt3_predict_next_token` calls the OpenAI API (openai.Completion). Here there are no weights or
key, so each scene carries a synthetic model (n-grams over the real BPE vocabulary of
GPT-2 via tiktoken) that reads this file:

  _lib/data/2024/transformers/data/synthetic_gpt_data.json
    "scripts":     full texts (seed + continuation) written for this conversion. They are the
                   n-gram's "modern corpus" and, when the generated text matches one of
                   them token by token, the model gives the script's continuation with high probability.
    "first_steps": "author" predictions for the prefixes that the scenes show in detail
                   (prefix -> [[token, probability], ...]); the remaining mass is spread by the n-gram.
    "chat_answers": canned answers for ChatbotFeedback (chm.py).

All the text is original (it does not come from any model or any book). The probabilities are
plausible, not those of the real models.

Usage: python make_generation_data.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[3]
OUT = LIB / "data" / "2024" / "transformers" / "data" / "synthetic_gpt_data.json"


def clean_text(text):
    """Same as generation.py's clean_text: collapses whitespace."""
    return " ".join(text.split())


SYSTEM_PROMPT = clean_text("""
    What follows is a conversation between a user and a helpful,
    very knowledgeable AI assistant.
""")


def chat(user_prompt, answer):
    return "\n\n".join([SYSTEM_PROMPT, user_prompt, "AI Assistant:" + answer])


SCRIPTS = [
    # SimpleAutogregression (default seed)
    "Behold, a wild pi creature, foraging in its native habitat. It moves slowly through the tall "
    "grass, pausing now and then to nibble on the tender shoots of the numerical vine. The creature "
    "is unusually shy, but if you stay very still, it may come close enough for you to see the "
    "faint circle painted across its back. Researchers have long wondered why this species only "
    "appears at dusk, when the shadows are long and the air smells of rain. Some believe it is a "
    "matter of safety, while others say it is simply following the light across the meadow, where "
    "the rest of its family is waiting. When night finally falls, they gather by the stream and "
    "drink together under the stars.",

    # GPT3CleverestAutocomplete
    "To date, the cleverest thinker of all time was Albert Einstein, whose theory of relativity "
    "changed the way we understand space and time. Born in 1879, he published four groundbreaking "
    "papers in a single year and went on to win the Nobel Prize in Physics in 1921. Many scholars, "
    "however, point to Isaac Newton, whose laws of motion and universal gravitation laid the "
    "foundation for classical physics, as an equally strong candidate. Others argue that the title "
    "belongs to someone like Leonardo da Vinci, who excelled in art, anatomy, and engineering.",

    # GPT3OnLearningSimpler
    "The most effective way to learn computer science is to start with the basics and build up from "
    "there. Begin by learning a programming language such as Python, which has a gentle syntax and "
    "a large community. Then work through small projects that interest you, such as a text-based "
    "game or a simple website, and read other people's code to see how they solve problems. Once "
    "you are comfortable writing programs, study data structures and algorithms, because they teach "
    "you how to think about efficiency and structure. It also helps to learn how computers "
    "actually work, from binary numbers and logic gates up to operating systems and networks. "
    "Finally, practice every day, even if only for a short time, and do not be afraid to make "
    "mistakes. Debugging your own errors is one of the best teachers there is, and every program "
    "you finish will make the next one easier to start. A good habit is to explain what you have "
    "learned to someone else, because teaching reveals the gaps in your understanding. Open source "
    "projects offer another great way to learn, since you can read real code written by "
    "experienced engineers and even contribute small fixes of your own. Along the way, try to "
    "build a few larger programs that bring many ideas together, like a chat application or a "
    "tiny search engine. Over time, the pieces start to connect, and what once looked like a "
    "pile of unrelated tricks begins to feel like a single coherent subject.",

    # GPT3OnLongPassages
    "Writing long passages seems to involve more foresight and planning than what single-word "
    "prediction might suggest. When a person writes an essay, they usually have a rough outline in "
    "mind before the first sentence appears, and each paragraph is shaped by where the argument is "
    "headed. A model that only looks at the words so far can still produce fluent text, but it is "
    "not obvious that it plans ahead in the same way. Some researchers argue that the internal "
    "representations of large models encode far more about the future than the next word alone, "
    "and that is part of why the text they write can stay coherent for pages at a time.",

    # LowTempExample / HighTempExample
    "Once upon a time, there was a little girl named Lily who loved to explore the forest behind "
    "her house. Every morning she would put on her red boots, pack a small basket with bread and "
    "apples, and set off along the winding path. One day, she came across a tiny fox with a "
    "bandaged paw, sitting beside a fallen log. \"Do not be afraid,\" said Lily, kneeling down. "
    "\"I can help you.\" The fox looked at her with bright amber eyes, and for the first time in "
    "many years, it spoke. \"Thank you,\" it whispered. \"I have been waiting for someone kind to "
    "come along.\" Lily smiled and carefully wrapped a fresh cloth around its paw. From that day "
    "on, the two of them were the best of friends, and they spent every morning exploring the "
    "forest together, discovering hidden streams, old stone bridges, and secret meadows full of "
    "wildflowers. When winter came, the fox led Lily to a warm cave where they sat by the fire "
    "and told stories until the snow melted away.",

    # MidTempExample
    "If you could see the underlying probability distributions a large language model uses when "
    "generating text, then you would notice that, at every step, the model is not choosing a "
    "single word but weighing hundreds of possibilities. Most of the weight sits on a handful of "
    "likely candidates, while a long tail of unlikely words shares what remains. Sampling from "
    "that distribution at temperature one produces text that is varied but still coherent, "
    "whereas a lower temperature makes the output more predictable and a higher one makes it "
    "stranger and less reliable. In the end, the choice of temperature is a trade between "
    "creativity and consistency. For a story, you may want a little more randomness, so that the "
    "text surprises the reader. For a legal summary or a piece of code, you probably want the most "
    "likely word nearly every time. Either way, the same underlying machine is doing the work: it "
    "reads everything written so far, turns it into a list of probabilities, and then a single "
    "word is drawn from that list before the whole process repeats. Do that a few hundred times "
    "and you get a paragraph, a poem, or an essay.",

    # ChatBotPrompt / ChatBotPrompt2 / ChatBotPrompt3
    chat(
        "User: Give me some ideas for what to do when visiting Paris.",
        " Sure! Here are a few ideas for your visit. First, take a walk along the Seine and enjoy the "
        "views of Notre-Dame and the Eiffel Tower. Second, visit the Louvre, which houses the Mona "
        "Lisa and thousands of other works of art. You might also climb the hill of Montmartre for a "
        "sweeping view of the city and a stop at the Sacre-Coeur. In the evening, find a small "
        "restaurant in the Latin Quarter and try some French onion soup. Finally, do not forget to "
        "pick up a fresh croissant at a local bakery in the morning!",
    ),
    chat(
        "User: Can you explain what temperature is, in the context of softmax?",
        " Of course! In the context of softmax, temperature is a parameter that controls how sharp or "
        "how flat the resulting probability distribution is. The softmax function divides each score "
        "by the temperature before exponentiating and normalizing. With a low temperature, the "
        "largest score dominates and the distribution becomes nearly deterministic. With a high "
        "temperature, the scores are squeezed together and the distribution becomes closer to "
        "uniform. A temperature of one leaves the scores unchanged.",
    ),
    chat(
        "User: Can you give me some ideas for what to do while visiting Munich?",
        " Absolutely! Munich has a lot to offer. You could start with a stroll through the Marienplatz "
        "and watch the famous glockenspiel at the New Town Hall. Next, spend an afternoon in the "
        "English Garden, one of the largest city parks in the world, where you can even watch people "
        "surf on the river. If you enjoy museums, the Deutsches Museum is a wonderful place for "
        "science and technology. And of course, no trip is complete without visiting a traditional "
        "beer hall for a pretzel and some Bavarian food.",
    ),

    # PredictTheNextWord (chm.py)
    "Paris is a city in France. It is the capital and most populous city of the country, with an "
    "estimated population of over two million residents within its city limits. Located on the "
    "Seine River, in the north of the country, Paris has been a major center of finance, "
    "diplomacy, commerce, fashion, and the arts since the seventeenth century. The city is known "
    "for its museums and architectural landmarks, including the Louvre, the Eiffel Tower, and the "
    "cathedral of Notre-Dame, which attract millions of visitors every year.",

    # ThatWhichDoesNotKillMe / RiverBankProbParts
    "Down by the river bank, the water ran slowly under the willows, and the children came every "
    "afternoon to skip stones across the surface. Their laughter carried far along the water, "
    "where the old fisherman sat mending his nets in the shade. Nobody could remember a time when "
    "he had not been there, and nobody thought to ask him how long the river had been running "
    "that way.",

    # AthleteCompletion
    "Michael Jordan plays the sport of basketball. He is widely regarded as one of the greatest "
    "players in the history of the game, and spent most of his career with the Chicago Bulls, "
    "where he won six championships.",

    # PredictionVsGeneration
    "The goal of predicting the next word is to build a model that captures the structure of "
    "language well enough to continue any piece of text in a sensible way.",

    # ManyParallelPredictions
    "Harry Potter was a highly unusual boy in many ways. For one thing, he hated the summer "
    "holidays more than any other time of year. For another, he really wanted to do his homework "
    "but was forced to do it in secret, in the dead of night.",

    # El fluffy blue creature
    "the fluffy blue creature roamed the land, searching for something to eat. It had been walking "
    "for hours across the open plains, and its small round belly was beginning to rumble.",
]

# prefix -> [(token, probability), ...]
FIRST_STEPS = {
    "Behold, a wild pi creature, foraging in its native": [
        (" habitat", .28), (" land", .09), (" environment", .06), (" tongue", .05), (" country", .045),
        (" language", .04), (" home", .03), (" soil", .025), (" village", .02), (" territory", .02),
        (" forest", .015), (" form", .012),
    ],
    "To date, the cleverest thinker of all time was": [
        (" Albert", .12), (" probably", .10), (" Isaac", .07), (" Leonardo", .06), (" Aristotle", .045),
        (" undoubtedly", .04), (" Einstein", .035), (" Stephen", .03), (" Plato", .03), (" Newton", .025),
        (" Socrates", .02), (" Nikola", .02),
    ],
    "The most effective way to learn computer science is": [
        (" to", .39), (" by", .12), (" through", .07), (" practice", .035), (" with", .03), (" the", .028),
        (" a", .02), (" hands", .02), (" not", .015), (" project", .01), (" simply", .01), (" learning", .01),
        (" via", .01), (" probably", .01), (" first", .008), (" actually", .008), (" really", .008),
        (" building", .007), (" coding", .007), (" immersion", .005),
    ],
    "Writing long passages seems to involve more foresight and planning than what single-word prediction": [
        (" might", .16), (" can", .11), (" would", .09), (" alone", .07), (" suggests", .06), (" implies", .05),
        (" is", .045), (" seems", .04), (" allows", .03), (" does", .03), (" requires", .025), (",", .02),
        (" could", .02), (" will", .015), (" has", .012), (" involves", .01), (" may", .01), (" appears", .008),
        (" typically", .006), (" offers", .005),
    ],
    "the fluffy blue creature": [
        (" was", .13), (" in", .07), (" is", .06), (",", .06), (" that", .045), (" with", .04), (" had", .035),
        (" from", .03), (" on", .028), (" and", .025), (" who", .02), (" looked", .02),
    ],
    "the fluffy blue creature roamed the": [
        (" land", .21), (" earth", .08), (" forest", .08), (" countryside", .045), (" streets", .04),
        (" woods", .04), (" planet", .035), (" world", .035), (" fields", .03), (" skies", .025),
        (" jungle", .02), (" plains", .02),
    ],
    "Once upon a time, there was a": [
        (" little", .10), (" young", .09), (" man", .06), (" princess", .045), (" girl", .04), (" boy", .035),
        (" king", .033), (" time", .03), (" poor", .025), (" beautiful", .022), (" small", .02), (" woman", .02),
    ],
    "If you could see the underlying probability distributions a large language model uses when generating text, then": [
        (" you", .26), (" it", .09), (" the", .07), (" you'd", .06), (" what", .035), (" this", .03), (" we", .028),
        (" there", .026), (" I", .024), (" perhaps", .02), (" how", .018), (" these", .016),
    ],
    "The goal of predicting the next": [
        (" word", .21), (" step", .13), (" generation", .08), (" token", .07), (" move", .05), (" event", .04),
        (" year", .03), (" decade", .025), (" level", .02), (" state", .018), (" frame", .015), (" element", .012),
    ],
    "Paris is a city in": [
        (" France", .56), (" the", .11), (" Texas", .05), (" northern", .04), (" Europe", .03), (" central", .025),
        (" Île", .02), (" Tennessee", .018), (" Kentucky", .015), (" Ontario", .012), (" Illinois", .012), (" Idaho", .01),
    ],
    "Down by the river bank": [
        (",", .22), (" where", .12), (" the", .07), (" in", .05), (".", .05), (" of", .04), (" at", .04),
        (" there", .03), (" near", .03), (" is", .025), (" and", .025), (" was", .02),
    ],
    "Michael Jordan plays the sport of": [
        (" basketball", .94), (" golf", .012), (" baseball", .008), (" hockey", .006), (" football", .005),
        (" Basketball", .004), (" soccer", .004), (" tennis", .003), (" bas", .003), (" b", .002),
        (" the", .002), (" basket", .002),
    ],
    "Harry": [
        (" Potter", .41), (" Styles", .06), (" Truman", .03), (" Kane", .025), (" Reid", .02), (" Redknapp", .02),
        (",", .02), (" and", .018), (" Houdini", .015), (" Winston", .012),
    ],
    "Harry Potter": [
        (" and", .21), (" is", .10), (",", .09), (" was", .08), ("'s", .07), (" has", .04), (" series", .03),
        (" fans", .03), (" books", .02), (" in", .018),
    ],
    "Harry Potter was": [
        (" a", .22), (" born", .08), (" the", .06), (" an", .05), (" first", .04), (" not", .04), (" released", .03),
        (" written", .02), (" so", .02), (" one", .018),
    ],
    "Harry Potter was a": [
        (" boy", .13), (" wizard", .10), (" young", .08), (" very", .05), (" great", .05), (" fictional", .04),
        (" good", .03), (" book", .03), (" character", .028), (" lonely", .02),
    ],
    "Harry Potter was a highly": [
        (" unusual", .38), (" successful", .12), (" skilled", .06), (" intelligent", .05), (" respected", .04),
        (" talented", .04), (" gifted", .035), (" popular", .03), (" regarded", .025), (" trained", .02),
    ],
    "Harry Potter was a highly unusual": [
        (" boy", .42), (" wizard", .12), (" young", .06), (" child", .05), (" character", .04), (" man", .04),
        (" and", .03), (",", .03), (" student", .02), (" kind", .015),
    ],
    "Harry Potter was a highly unusual boy": [
        (".", .55), (",", .20), (" who", .05), (" in", .03), (" with", .03), (" and", .03), ("\n", .02),
        (" -", .02), (" for", .015), (" indeed", .01),
    ],
}

CHAT_ANSWERS = [
    " Sure! The internet grew out of ARPANET, a research network funded by the US Department of Defense. "
    "The first message was sent over ARPANET in 1969, and the modern internet took shape in 1983, when "
    "the network adopted the TCP/IP protocols.",

    " The internet was not invented at a single moment. It began with ARPANET in 1969, a project that "
    "connected a few university computers, and it grew over the following decades as new networks "
    "joined and agreed on shared protocols such as TCP/IP.",

    " Great question! The internet was invented in 1990 by Tim Berners-Lee, who created the World Wide Web "
    "at CERN and also built the first web browser.",

    " The internet was invented in 1850 by Samuel Morse, who sent the first email across the Atlantic "
    "using telegraph wires.",

    " Sure! In the late 1960s, researchers in the United States developed ARPANET to let computers share "
    "information. In the 1970s, Vint Cerf and Bob Kahn designed the protocols that let separate networks "
    "talk to each other, and by the 1990s the web had made the internet available to everyone.",

    " I am not sure, but I think the internet was invented sometime in the 1980s by a group of "
    "engineers working on telephone cables.",

    " Happy to help! The internet developed gradually. Packet switching was proposed in the early 1960s, "
    "ARPANET went live in 1969, email appeared in 1971, and the World Wide Web was introduced in 1989.",

    " That is a complicated question with many answers, but most historians agree that the internet "
    "began as ARPANET in 1969 and became public in the 1990s.",
]


def main():
    data = {
        "scripts": SCRIPTS,
        "first_steps": {k: [list(x) for x in v] for k, v in FIRST_STEPS.items()},
        "chat_answers": CHAT_ANSWERS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"escrito {OUT}")


if __name__ == "__main__":
    main()
