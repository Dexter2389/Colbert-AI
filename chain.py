import re
import random
import operator
import bisect
import json
from unidecode import unidecode
from splitters import split_into_sentences

BEGIN = "__BEGIN__"
END = "__END__"


def accumulate(iterable, func=operator.add):
    """
    Cumulative calculations. (Summation, by default.)
    """
    it = iter(iterable)
    total = next(it)
    yield total
    for element in it:
        total = func(total, element)
        yield total


class MarkovChain(object):
    """
    Markov Chain which has beginning and end.
    """

    def __init__(self, corpus, state_size):
        """
        corpus: It is a list of lists where the outer list like a sentence and the inner list is
        contains the words that make the sentence.

        state_size: items used to represent the state of the model.
        """
        self.state_size = state_size
        self.model = self.build(corpus, self.state_size)
        # self.precompute_begin_state()

    def build(self, corpus, state_size):
        """
        Returns a dict of dicts where the keys of the outer dict represent all possible states, and
        point to the inner dicts. The inner dicts represent all possibilities for the "next" item in
         the chain, along with the count of times it appears.
        """
        model = {}

        for run in corpus:
            items = ([BEGIN] * state_size) + run + [END]
            for i in range(len(run) + 1):
                state = tuple(items[i:i + state_size])
                follow = items[i + state_size]
                if state not in model:
                    model[state] = {}

                if follow not in model[state]:
                    model[state][follow] = 0

                model[state][follow] += 1

        return model

    def move(self, state):
        """
        Randomly chooses item based on the given state..
        """
        choices, weights = zip(*self.model[state].items())
        cumdist = list(accumulate(weights))
        r = random.random() * cumdist[-1]
        selection = choices[bisect.bisect(cumdist, r)]
        return selection

    def gen(self, init_state=None):
        """
        Starting with a naive "BEGIN" state, RETURNS a generator that will yield successive items
        until the chain reaches the "END" state.
        """
        state = init_state or (BEGIN,) * self.state_size
        while True:
            next_word = self.move(state)
            if next_word == END:
                break
            yield next_word
            state = tuple(state[1:]) + (next_word,)

    def walk(self, init_state=None):
        """
        Returns a list representing a single run of the markov model
        """
        return list(self.gen(init_state))

    def to_json(self):
        """
        Converts the list into a string
        """
        return json.dumps(list(self.model.items()))


DEFAULT_MAX_OVERLAP_RATIO = 0.7
DEFAULT_MAX_OVERLAP_TOTAL = 20
DEFAULT_TRIES = 8


class Text(object):
    def __init__(self, input_text, state_size=2, chain=None, parsed_sentences=None,
                 retain_original=True):
        """
        input_text: A string.
        state_size: An integer, indicating the number of words in the model's state.
        parsed_sentences: It is a list of lists where the outer list like a sentence and the inner
        list is contains the words that make the sentence.
        """

        can_make_sentences = parsed_sentences is not None or input_text is not None
        self.retain_original = retain_original and can_make_sentences
        self.state_size = state_size

        if self.retain_original:
            self.parsed_sentences = parsed_sentences or list(
                self.generate_corpus(input_text))

            # Rejoined text lets us assess the novelty of generated sentences
            self.rejoined_text = self.sentence_join(
                map(self.word_join, self.parsed_sentences))
            self.chain = chain or MarkovChain(
                self.parsed_sentences, state_size)

        else:
            if not chain:
                parsed = parsed_sentences or self.generate_corpus(input_text)
            self.chain = chain or MarkovChain(parsed, state_size)

    def to_dict(self):
        """
        Makes a Python dict of all the data
        """
        return {
            "state_size": self.state_size,
            "chain": self.chain.to_json,
            "parsed_sentences": self.parsed_sentences if self.retain_original else None
        }

    def sentence_split(self, text):
        """
        Splits full-text string into a list of sentences
        """
        return split_into_sentences(text)

    def sentence_join(self, sentences):
        """
        Rejoins a list of sentences into the full text
        """
        return " ".join(sentences)

    word_split_pattern = re.compile(r"\s+")

    def word_split(self, sentence):
        """
        Splits the sentence into list of words
        """
        return re.split(self.word_split_pattern, sentence)

    def word_join(self, words):
        """
        Rejoins a list of words into a sentence
        """
        return " ".join(words)

    def text_sentences_input(self, sentence):
        """
        A sentence filter that will reject any sentences that has strange punctuation in it
        """
        if len(sentence.strip()) == 0:
            return False

        reject_pat = re.compile(r"(^')|('$)|\s'|'\s|[\"(\(\)\[\])]")

        # Decode unicode, mainly to normalize fancy quotation marks

        if sentence.__class__.__name__ == "str":
            decoded = sentence

        else:
            decoded = unidecode(sentence)

        # Sentence shouldn't contain problematic characters

        if re.search(reject_pat, decoded):
            return False

        return True

    def generate_corpus(self, text):
        """
        Returns a list of list of sentences, each containing list of words.
        """
        if isinstance(text, str):
            sentences = self.sentence_split(text)

        else:
            sentences = []
            for line in text:
                sentences += self.sentence_split(line)

        passing = filter(self.text_sentences_input, sentences)
        runs = map(self.word_split, passing)

        return runs

    def text_sentences_output(self, words, max_overlap_ratio, max_overlap_total):
        """
        Given a generated list of words, accept or reject it. This one rejects sentences that too
        closely match the original text, namely those that contain any identical sequence of words
        of X length, where X is the smaller number of (a) `max_overlap_ratio` (default: 0.7) of the
        total number of words, and (b) `max_overlap_total` (default: 15).
        """
        # Rejects chunk that is similar

        overlap_ratio = int(round(max_overlap_ratio * len(words)))
        overlap_max = min(max_overlap_total, overlap_ratio)
        overlap_over = overlap_max + 1

        gram_count = max((len(words) - overlap_max), 1)
        grams = [words[i:i + overlap_over] for i in range(gram_count)]

        for gm in grams:
            gram_joined = self.word_join(gm)
            if gram_joined in self.rejoined_text:
                return False

        return True

    def make_sentences(self, init_state=None, **kwargs):
        """
        Attempts "tries" (default: 10) times to generate a valid sentence, based on the model and
        "test_sentences_output". Passes "max_overlap_ratio" and "max_overlap_total" to
        "test_sentences_output".

        If successful, returns the sentence as a string. If not, returns None.

        If "init_state" (a tuple of "self.chain.state_size" words) is not specified, this method
        chooses a sentence-start at random, in accordance with the model.

        If "test_output" is set as False then the "text_sentences_output" check will be skipped.

        If "max_words" is specified, the word count for the sentence will be evaluated against the
        provided limit.
        """

        tries = kwargs.get("tries", DEFAULT_TRIES)
        mor = kwargs.get("max_overlap_ratio", DEFAULT_MAX_OVERLAP_RATIO)
        mot = kwargs.get("max_overlap_total", DEFAULT_MAX_OVERLAP_TOTAL)
        test_output = kwargs.get("test_output", True)
        max_words = kwargs.get("max_words", None)

        if init_state is not None:
            prefix = list(init_state)
            for word in prefix:
                if word == BEGIN:
                    prefix = prefix[1:]
                else:
                    break

        else:
            prefix = []

        for _ in range(tries):
            words = prefix + self.chain.walk(init_state)
            if max_words is not None and len(words) > max_words:
                continue
            if test_output and hasattr(self, "rejoined_text"):
                if self.text_sentences_output(words, mor, mot):
                    return self.word_join(words)

            else:
                return self.word_join(words)

        return None

    def make_short_sentence(self, max_chars, min_chars=0, **kwargs):
        """
        Tries making a sentence of no more than "max_chars" characters and optionally no less than
        "min_chars" charcaters, passing **kwargs to "self.make_sentence".
        """
        tries = kwargs.get("tries", DEFAULT_TRIES)

        for _ in range(tries):
            sentence = self.make_sentences(**kwargs)
            if sentence and max_chars >= len(sentence) >= min_chars:
                return sentence
