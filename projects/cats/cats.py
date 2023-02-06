"""Typing test implementation"""

from utils import *
from ucb import main, interact, trace
from datetime import datetime


###########
# Phase 1 #
###########

def choose(paragraphs, select, k):
    """Return the Kth paragraph from PARAGRAPHS for which SELECT called on the
    paragraph returns true. If there are fewer than K such paragraphs, return
    the empty string.
    """
    # BEGIN PROBLEM 1

    selected_paragraphs = []
    for i in range(len(paragraphs)):
        if select(paragraphs[i]):
            selected_paragraphs.append(paragraphs[i])
    if len(selected_paragraphs) <= k:
        return ''
    else:
        return selected_paragraphs[k]


def about(topic):
    """Return a select function that returns whether a paragraph contains one
    of the words in TOPIC.
    >>> about_dogs = about(['dog', 'dogs', 'pup', 'puppy'])
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup!'], about_dogs, 0)
    'Cute Dog!'
    >>> choose(['Cute Dog!', 'That is a cat.', 'Nice pup.'], about_dogs, 1)
    'Nice pup.'
    """
    assert all([lower(x) == x for x in topic]), 'topics should be lowercase.'

    def select(paragraph):
        # convert lists to sets (and parses paragraph) to compare them with intersection function

        topic_set = set(topic)
        paragraph_set = set(split(lower(remove_punctuation(paragraph))))

        if topic_set.intersection(paragraph_set):
            return True
        return False

    return select


def accuracy(typed, reference):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    when compared to the prefix of REFERENCE that was typed.

    >>> accuracy('Cute Dog!', 'Cute Dog.')
    50.0
    >>> accuracy('A Cute Dog!', 'Cute Dog.')
    0.0
    >>> accuracy('cute Dog.', 'Cute Dog.')
    50.0
    >>> accuracy('Cute Dog. I say!', 'Cute Dog.')
    50.0
    >>> accuracy('Cute', 'Cute Dog.')
    100.0
    >>> accuracy('', 'Cute Dog.')
    0.0
    """

    typed_words = split(typed)
    reference_words = split(reference)
    percentage = 0
    j = len(typed_words)

    if not typed_words or not reference_words:
        return 0.0
    if len(typed_words) != len(reference_words):
        j = min(len(typed_words), len(reference_words))

    for i in range(j):
        if typed_words[i] == reference_words[i]:
            percentage += 1

    return (percentage / len(typed_words)) * 100


def wpm(typed, elapsed):
    """Return the words-per-minute (WPM) of the TYPED string."""
    assert elapsed > 0, 'Elapsed time must be positive'
    minute = 60

    return (len(typed) / 5) * (minute / elapsed)


def autocorrect(user_word, valid_words, diff_function, limit):
    """Returns the element of VALID_WORDS that has the smallest difference
    from USER_WORD. Instead, returns USER_WORD if that difference is greater
    than LIMIT.
    """

    dif = []
    if user_word in valid_words:
        return user_word

    for i in range(len(valid_words)):
        dif.append(diff_function(user_word, valid_words[i], limit))

    if min(dif) > limit:
        return user_word

    return valid_words[dif.index(min(dif))]


def sphinx_swap(start, goal, limit):
    """A diff function for autocorrect that determines how many letters
    in START need to be substituted to create GOAL, then adds the difference in
    their lengths.
    """

    if start == "" or goal == "" or limit < 0:
        return abs(len(start) - len(goal))

    elif limit < 0:
        return limit ** limit

    else:
        if start[:1] == goal[:1]:
            return sphinx_swap(start[1:], goal[1:], limit)
        else:
            return sphinx_swap(start[1:], goal[1:], limit - 1) + 1


def feline_fixes(start, goal, limit):
    """A diff function that computes the edit distance from START to GOAL."""

    if start == "" or goal == "" or limit < 0:
        return abs(len(start) - len(goal))

    elif limit < 0:
        return limit ** limit

    elif start[:1] == goal[:1]:
        return feline_fixes(start[1:], goal[1:], limit)

    else:
        add = feline_fixes(start, goal[1:], limit - 1) + 1
        remove = feline_fixes(start[1:], goal, limit - 1) + 1
        substitute = feline_fixes(start[1:], goal[1:], limit - 1) + 1
        return min(add, remove, substitute)


def final_diff(start, goal, limit):
    """A diff function. If you implement this function, it will be used."""
    assert False, 'Remove this line to use your final_diff function'


###########
# Phase 3 #
###########


def report_progress(typed, prompt, id, send):
    """Send a report of your id and progress so far to the multiplayer server."""
    correct = 0

    for i in range(len(typed)):
        if typed[i] != prompt[i]:
            correct = i
            break
        else:
            correct = len(typed)

    progress = correct / len(prompt)
    send_progress = {
        'id': id,
        'progress': progress
    }
    send(send_progress)
    return progress


def fastest_words_report(times_per_player, words):
    """Return a text description of the fastest words typed by each player."""
    game = time_per_word(times_per_player, words)
    fastest = fastest_words(game)
    report = ''
    for i in range(len(fastest)):
        words = ','.join(fastest[i])
        report += 'Player {} typed these fastest: {}\n'.format(i + 1, words)
    return report


def time_per_word(times_per_player, words):
    """Given timing data, return a game data abstraction, which contains a list
    of words and the amount of time each player took to type each word.

    Arguments:
        times_per_player: A list of lists of timestamps including the time
                          the player started typing, followed by the time
                          the player finished typing each word.
        words: a list of words, in the order they are typed.
    """

    for i in range(len(times_per_player)):
        for j in range(len(times_per_player[i]) - 1):
            times_per_player[i][j] = times_per_player[i][j + 1] - times_per_player[i][j]
        times_per_player[i].pop()

    return game(words, times_per_player)


def fastest_words(game):
    """Return a list of lists of which words each player typed fastest.

    Arguments:
        game: a game data abstraction as returned by time_per_word.
    Returns:
        a list of lists containing which words each player typed fastest
    """
    players = range(len(all_times(game)))  # An index for each player
    words = range(len(all_words(game)))  # An index for each word
    temp = 0
    player = 0
    fastest_player = []
    # create list of lists
    for i in players:
        fastest_player.append([])

    # find fastest player
    for i in words:
        for j in players:
            if temp == 0:
                temp = time(game, j, i)
                player = j
            elif time(game, j, i) < temp:
                temp = time(game, j, i)
                player = j
        fastest_player[player].append(word_at(game, i))
        temp = 0

    return fastest_player


def game(words, times):
    """A data abstraction containing all words typed and their times."""
    assert all([type(w) == str for w in words]), 'words should be a list of strings'
    assert all([type(t) == list for t in times]), 'times should be a list of lists'
    assert all([isinstance(i, (int, float)) for t in times for i in t]), 'times lists should contain numbers'
    assert all([len(t) == len(words) for t in times]), 'There should be one word per time.'
    return [words, times]


def word_at(game, word_index):
    """A selector function that gets the word with index word_index"""
    assert 0 <= word_index < len(game[0]), "word_index out of range of words"
    return game[0][word_index]


def all_words(game):
    """A selector function for all the words in the game"""
    return game[0]


def all_times(game):
    """A selector function for all typing times for all players"""
    return game[1]


def time(game, player_num, word_index):
    """A selector function for the time it took player_num to type the word at word_index"""
    assert word_index < len(game[0]), "word_index out of range of words"
    assert player_num < len(game[1]), "player_num out of range of players"
    return game[1][player_num][word_index]


def game_string(game):
    """A helper function that takes in a game object and returns a string representation of it"""
    return "game(%s, %s)" % (game[0], game[1])


enable_multiplayer = False  # Change to True when you


##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        reference = choose(paragraphs, select, i)
        if not reference:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(reference)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print("Nice work!")
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, reference))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Typing Test")
    parser.add_argument('topic', help="Topic word", nargs='*')
    parser.add_argument('-t', help="Run typing test", action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)
