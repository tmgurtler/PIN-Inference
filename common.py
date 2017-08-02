from contextlib import contextmanager
from collections import defaultdict
from dateutil import parser as prsr
import numpy as np
import sqlite3
import math
import sys
import os

CODE_FOR_BACKSPACE = "b"
CODE_FOR_ENTER = "e"

# defined (and so large) mostly just for convenience's sake
all_sets = {
    "dist_zero": ["00", "11", "22", "33", "44", "55", "66", "77", "88", "99"],
    "dist_one": ["12", "23", "45", "56", "78", "89", "21", "32", "54", "65", "87", "98", "14", "47", "25", "58", "36", "69", "41", "74", "52", "85", "63", "96", "80", "08"],
    "dist_one_horizontal": ["12", "23", "45", "56", "78", "89", "21", "32", "54", "65", "87", "98"],
    "dist_one_left": ["21", "32", "54", "65", "87", "98"],
    "dist_one_right": ["12", "23", "45", "56", "78", "89"],
    "dist_one_vertical": ["14", "47", "25", "58", "36", "69", "41", "74", "52", "85", "63", "96", "80", "08"],
    "dist_one_up": ["41", "74", "52", "85", "63", "96", "08"],
    "dist_one_down": ["14", "47", "25", "58", "36", "69", "80"],
    "dist_two": ["13", "46", "79", "31", "64", "97", "17", "28", "39", "71", "82", "93", "50", "05"],
    "dist_two_horizontal": ["13", "46", "79", "31", "64", "97"],
    "dist_two_left": ["31", "64", "97"],
    "dist_two_right": ["13", "46", "79"],
    "dist_two_vertical": ["17", "28", "39", "71", "82", "93", "50", "05"],
    "dist_two_up": ["71", "82", "93", "05"],
    "dist_two_down": ["17", "28", "39", "50"],
    "dist_three": ["20", "02"],
    "dist_three_up": ["02"],
    "dist_three_down": ["20"],
    "dist_diagonal_one": ["15", "26", "24", "35", "48", "59", "57", "68", "70", "90", "51", "62", "42", "53", "84", "95", "75", "86", "07", "09"],
    "dist_diagonal_two": ["19", "37", "91", "73"],
    "dist_dogleg": ["16", "18", "27", "29", "34", "38", "43", "49", "40", "61", "67", "60", "72", "76", "81", "83", "92", "94", "04", "06"],
    "dist_long_dogleg": ["10", "30", "01", "03"],
    "zero_to_enter": ["0e"],
    "one_to_enter": ["1e"],
    "two_to_enter": ["2e"],
    "three_to_enter": ["3e"],
    "four_to_enter": ["4e"],
    "five_to_enter": ["5e"],
    "six_to_enter": ["6e"],
    "seven_to_enter": ["7e"],
    "eight_to_enter": ["8e"],
    "nine_to_enter": ["9e"]
}

list_of_lists = {
    # all the different distance one sets (varying direction)
    "dir_one_sets": [
        "dist_one",
        "dist_one_horizontal",
        "dist_one_vertical",
        "dist_one_up",
        "dist_one_right",
        "dist_one_down",
        "dist_one_left"
    ],

    # all the different distance two sets (varying direction)
    "dir_two_sets": [
        "dist_two",
        "dist_two_horizontal",
        "dist_two_vertical",
        "dist_two_up",
        "dist_two_right",
        "dist_two_down",
        "dist_two_left"
    ],

    # all the different distance three sets (varying direction)
    "dir_three_sets": [
        "dist_three",
        "dist_three_up",
        "dist_three_down"
    ],

    # all the sets from a number to enter
    "to_enter_sets": [
        "zero_to_enter",
        "one_to_enter",
        "two_to_enter",
        "three_to_enter",
        "four_to_enter",
        "five_to_enter",
        "six_to_enter",
        "seven_to_enter",
        "eight_to_enter",
        "nine_to_enter"
    ],

    # all the sets from a number to enter (high digits only)
    "to_enter_high": [
        "zero_to_enter",
        "six_to_enter",
        "seven_to_enter",
        "eight_to_enter",
        "nine_to_enter"
    ],

    # all the sets from a number to enter (low digits only)
    "to_enter_low": [
        "one_to_enter",
        "two_to_enter",
        "three_to_enter",
        "four_to_enter",
        "five_to_enter"
    ],

    # compare zero to enter against distance two (same distance, theoretically)
    "enter_checker_zero_sets": [
        "zero_to_enter",
        "dist_two"
    ],

    # compare long distances to enter (similar)
    "enter_checker_one_sets": [
        "one_to_enter",
        "two_to_enter",
        "four_to_enter"
    ],

    # compare the long doglegs vs. numbers to enter (same distance, theoretically)
    "enter_checker_three_sets": [
        "three_to_enter",
        "seven_to_enter",
        "dist_long_dogleg"
    ],

    # compare the diagonal two distance vs. five to enter (same distance, theoretically)
    "enter_checker_five_sets": [
        "five_to_enter",
        "dist_diagonal_two"
    ],

    # compare the doglegs vs. numbers to enter (same distance, theoretically)
    "enter_checker_six_sets": [
        "six_to_enter",
        "eight_to_enter",
        "dist_dogleg"
    ],

    # compare the diagonal one distance vs. nine to enter (same distance, theoretically)
    "enter_checker_nine_sets": [
        "nine_to_enter",
        "dist_diagonal_one"
    ],

    # compare just the straight line distances
    "mainline_dist_sets": [
        "dist_zero",
        "dist_one",
        "dist_two",
        "dist_three"
    ],

    # compare the distances between one and two, inclusive
    "betweener_one_sets": [
        "dist_one",
        "dist_diagonal_one",
        "dist_dogleg",
        "dist_two"
    ],

    # compare the distances between two and three, inclusive
    "betweener_two_sets": [
        "dist_two",
        "dist_diagonal_two",
        "dist_long_dogleg",
        "dist_three"
    ],

    # compare all the distances
    "dist_sets": [
        "dist_zero",
        "dist_one",
        "dist_two",
        "dist_three",
        "dist_diagonal_one",
        "dist_diagonal_two",
        "dist_dogleg",
        "dist_long_dogleg"
    ],

    # compare what we can for inference
    "model_sets": [
        "dist_zero",
        "dist_one",
        "dist_two",
        "dist_three",
        "dist_diagonal_one",
        "dist_diagonal_two",
        "dist_dogleg",
        "dist_long_dogleg",
        "zero_to_enter",
        "one_to_enter",
        "two_to_enter",
        "three_to_enter",
        "four_to_enter",
        "five_to_enter",
        "six_to_enter",
        "seven_to_enter",
        "eight_to_enter",
        "nine_to_enter"
    ],

    "display_sets": [
        "dist_zero",
        "dist_two"
    ]
}

##
# This functionality allows us to temporarily change our working directory
#
# @input newdir - the new directory (relative to our current position) we want to be in
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

##
# This functionality allows us to temporarily change where stdout routes
#
# @input new_out - the file that stdout will get routed to temporarily
@contextmanager
def change_stdout(new_out):
    prev_out = sys.stdout
    sys.stdout = open(new_out, 'w')
    try:
        yield
    finally:
        sys.stdout.close()
        sys.stdout = prev_out

##
# This function pulls data from the SQLite database
#
# @returns a list of 4-tuples of keystroke timings
def retrieve_data():
    conn = sqlite3.connect('attempts.db')
    c = conn.cursor()

    c.execute('SELECT userString, pinAttempted, keyPressed, time FROM attempts WHERE userString != "wpZ8r" AND userString != "jFuj7" AND userString != "c7fcH" AND userString != "wtGa3"')
    res = c.fetchall()
    conn.close()

    return res

##
# This function organizes data by user and PIN
#
# @input res - a list of 4-tuples of keystroke timings
# @returns a dictionary of dictionaries of pairs,
#           where the top-level dictionary connects users to all PINs they enter and
#           the lower dictionary connects a PIN to all keystrokes used while entering the PIN and timings of each
#           in the format of a list of pairs (key pressed, time)
def preprocess_data(res):
    keystrokes = defaultdict(lambda: defaultdict(lambda: []))

    # make sure data is sorted by timestamp
    res = sorted(res, key=lambda x: x[3])

    # parser.parse reads a timestamp into a Python timedate object
    for keystroke in res:
        keystrokes[keystroke[0]][int(keystroke[1])].append((keystroke[2], prsr.parse(keystroke[3])))

    return keystrokes


##
# This function organizes data by individual PIN attempt,
# while throwing out attempts that include using the clear button or are just incorrect
#
# @input keystrokes - a dictionary of dictionaries of lists of pairs of keystrokes and timings
# @returns a dictionary of dictionaries of lists of lists of pairs,
#           where the top-level dictionary connects users to all PINs they enter and
#           the lower dictionary connects a PIN to all keystrokes used while entering the PIN and timings of each
#           in the format of a list of lists of pairs [[data corresponding to entering one PIN once] ... [(key pressed, time) ...] ...]
def clean_data(keystrokes):
    for user, user_data in keystrokes.items():
        for pin, pin_data in user_data.items():
            # collector for each sublist, which correspond to individual PINs
            all_attempts = []

            attempt = []
            flag_backspace = False
            
            for (key, time) in pin_data:
                # throw out any attempt that involves a backspace
                if key == CODE_FOR_BACKSPACE:
                    flag_backspace = True

                # enter is the last key pressed per PIN entry
                if key != CODE_FOR_ENTER:
                    attempt.append((key, time))
                else:
                    # default to assuming the PIN is wrong
                    flag_incorrect = True
                    # needs try/except because some entries are "" and int("") throws an exception
                    try:
                        pin_entered = "".join([x for (x,y) in attempt])
                        flag_incorrect = pin_entered != ("0000" + str(pin))[-4:]
                    except:
                        pass

                    # don't leave out the enter keystroke
                    attempt.append((key, time))

                    # only add our PIN attempt if it is good
                    if not flag_backspace and not flag_incorrect:
                        all_attempts.append(attempt)
                    
                    # only reset things at new PIN
                    attempt = []
                    flag_backspace = False

            keystrokes[user][pin] = all_attempts

    return keystrokes

##
# This function parses keystroke data into interkey timing data
#
# @input keystrokes - a dictionary of dictionaries of lists of lists of pairs of keystrokes and timings
# @returns a dictionary of lists of ints,
#           where the dictionary connects a keypair (e.g. "12")
#           to every interkey timing used to enter it
def parse_data(keystrokes):
    all_timings = defaultdict(lambda: [])

    for user, user_data in keystrokes.items():
        for pin, pin_data in user_data.items():
            entry_bigrams = []

            # collect every bigram from all attempts
            for attempt in pin_data:
                entry_bigrams.extend([(key_a + key_b, times_b - times_a) for ((key_a, times_a), (key_b, times_b)) in zip(attempt[:-1], attempt[1:])])

            # put bigrams in the dictionary and convert Python timedelta objects to integers
            for (bigram, time_diff) in entry_bigrams:
                time_diff_in_ms = int(math.floor(((time_diff.seconds * (10**6)) + time_diff.microseconds) / (10**3)))
                all_timings[bigram].append(time_diff_in_ms)

    return all_timings

##
# This function roots out the highest X% of data as outliers
#
# @input timings - a dictionary of lists of ints, where the dictionary
#                   connects a keypair (e.g. "12") to every interkey
#                   timing used to enter it
# @input percentile - the threshold above which data gets thrown out
#                       (defaults to 95th, as in top 5% gets thrown out)
# @returns a dictionary of lists of ints,
#           where the dictionary connects keypairs (e.g. "12")
#           to every interkey timing used to enter it (without outliers)
def filter_timings(timings, percentile=95):
    # get just the timings to figure out percentiles on them
    just_the_timings = [timing for bigram, set_of_timings in timings.items() for timing in set_of_timings]
    bar = np.percentile(just_the_timings, percentile)

    # filter out all timings which fall below the threshold
    good_pairs = [(bigram, list(filter(lambda x: x < bar, timing))) for bigram, timing in timings.items()]
    ret = defaultdict(lambda: [])

    # put our new timings back together in the dictionary
    for (bigram, timing) in good_pairs:
        ret[bigram] = (timing)

    return ret
