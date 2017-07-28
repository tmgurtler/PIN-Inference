# Python code that calculates statistics on data collected

import matplotlib
from common import *
from matplotlib.ticker import FuncFormatter
from contextlib import contextmanager
from collections import defaultdict
from scipy import stats
from dateutil import parser as prsr
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import itertools
import argparse


##
# This function parses keystroke data into interkey timing data while separating data by user
#
# @input keystrokes - a dictionary of dictionaries of lists of lists of pairs of keystrokes and timings
# @returns a list of dictionaries of ints,
#           where the dictionaries connect keypairs (e.g. "12")
#           to every interkey timing used to enter it by a given user
def parse_data_per_user(keystrokes):
    collector = []

    for user, user_data in keystrokes.items():
        all_timings = defaultdict(lambda: [])
        for pin, pin_data in user_data.items():
            entry_bigrams = []

            # collect every bigram from all attempts
            for attempt in pin_data:
                entry_bigrams.extend([(key_a + key_b, times_b - times_a) for ((key_a, times_a), (key_b, times_b)) in zip(attempt[:-1], attempt[1:])])

            # put bigrams in the dictionary and convert Python timedelta objects to integers
            for (bigram, time_diff) in entry_bigrams:
                time_diff_in_ms = int(math.floor(((time_diff.seconds * (10**6)) + time_diff.microseconds) / (10**3)))
                all_timings[bigram].append(time_diff_in_ms)
        collector.append(all_timings)

    return collector

##
# This function roots out the highest X% of data as outliers, while keeping data separate per user
#
# @input timings - a list of dictionaries of lists of ints, where the dictionaries
#                   connect keypairs (e.g. "12") to every interkey
#                   timing used to enter it by a single user
# @input percentile - the threshold above which data gets thrown out
#                       (defaults to 95th, as in top 5% gets thrown out)
# @returns a list of dictionaries of lists of ints,
#           where the dictionaries connect keypairs (e.g. "12")
#           to every interkey timing used by a single user to enter it (without outliers)
def filter_timings_per_user(timings, percentile=95):
    ret = []

    for user_data in timings:
        # get just the timings to figure out percentiles on them
        just_the_timings = [timing for bigram, set_of_timings in user_data.items() for timing in set_of_timings]
        bar = np.percentile(just_the_timings, percentile)

        # filter out all timings which fall below the threshold
        good_pairs = [(bigram, list(filter(lambda x: x < bar, timing))) for bigram, timing in user_data.items()]
        curr = defaultdict(lambda: [])

        # put our new timings back together in the dictionary
        for (bigram, timing) in good_pairs:
            curr[bigram] = (timing)
        ret.append(curr)

    return ret


##
# This function combines all functionalities pertaining obtaining and cleaning data
#
# @returns a dictionary of ints,
#           where the dictionary connects a keypair (e.g. "12")
#           to every interkey timing used to enter it
def obtain_timings():
    raw_data = retrieve_data()
    keystrokes = preprocess_data(raw_data)
    keystrokes = clean_data(keystrokes)
    timings = parse_data(keystrokes)

    return timings

##
# This function combines all functionalities pertaining obtaining and cleaning data, but on a per user level
#
# @returns a dictionary of ints,
#           where the dictionary connects a keypair (e.g. "12")
#           to every interkey timing used to enter it
def obtain_timings_per_user():
    raw_data = retrieve_data()
    keystrokes = preprocess_data(raw_data)
    keystrokes = clean_data(keystrokes)
    timings = parse_data_per_user(keystrokes)

    return timings


##
# This function tests whether the keypairs within a given set have significantly different timings from one another
#
# @input timings - a dictionary of keypairs with their timings
# @input given_set - what set of keypairs to test
def relevance_within_set(timings, given_set, name_of_set, user):
    print "P-value within " + name_of_set + " for user " + user
    print "---"

    # only test the keypairs we actually have data for
    active_set = [x for x in given_set if x in timings.keys()]
    test_pairs = itertools.combinations(active_set, 2)
    
    for x, y in test_pairs:
        t_statistic, p_value = stats.ttest_ind(timings[x], timings[y], equal_var=False)
        print "keypair 1: %s\nkeypair 2: %s\nt: %f\np value: %f\n" % (x, y, t_statistic, p_value)
    print ""

##
# This function only serves to make things look prettier for the histograms
def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'

##
# This function finds the mean and standard deviation of a given set and outputs
# those statistics
#
# @input timings - the set of all timings
# @input given_set - the set to find the mean and standard deviations
# @input name_of_set - a string denoting the name of the set
# @input user - a string identifying the user
def mean_std_of_set(timings, given_set, name_of_set, user):
    print "Mean and STD of " + name_of_set + " for user " + user
    print "---"

    # only test the keypairs we actually have data for
    active_set = [timings[x] for x in given_set]
    active_set = [item for sublist in active_set for item in sublist]
    
    std = np.std(active_set)
    mean = np.mean(active_set)

    print "mean: %f\nstandard deviation: %f\n" % (mean, std)

##
# This function produces a histogram for a given set
#
# @input timings - the set of all timings
# @input given_set - the set to produce a histogram for
# @input name_of_set - a string denoting the name of the set
# @input user - a string identifying the user
def hist_of_set(timings, given_set, name_of_set, show_model, show_raw):
    with cd('plots'):
        # only test the keypairs we actually have data for
        active_set = [timings[x] for x in given_set]
        active_set = [item for sublist in active_set for item in sublist]
        num = len(active_set)

        # if no data, don't bother plotting anything
        if not bool(active_set):
            return

        # Fit a gamma distribution to the data observed
        alpha, loc, beta = stats.gamma.fit(active_set)
        scale = beta ** (-1)
        x = np.linspace(0, 650, 1000)
        model_name = name_of_set +"\nmodeled as Gamma dist"

        ##
        # this is a hack so that we can always make sure that
        # the same class gets the same color, independent of run
        color = {
            "dist_zero": "black",

            "dist_one": "red",
            "dist_one_horizontal": "green",
            "dist_one_vertical": "blue",
            "dist_one_up": "black",
            "dist_one_right": "orange",
            "dist_one_down": "cyan",
            "dist_one_left": "purple",

            "dist_two": "blue",
            "dist_two_horizontal": "green",
            "dist_two_vertical": "red",
            "dist_two_up": "black",
            "dist_two_right": "orange",
            "dist_two_down": "cyan",
            "dist_two_left": "purple",

            "dist_three": "green",
            "dist_three_up": "red",
            "dist_three_down": "blue",

            "dist_diagonal_one": "magenta",
            "dist_dogleg": "orange",
            "dist_long_dogleg": "cyan",
            "dist_diagonal_two": "purple",

            "zero_to_enter": "red",
            "one_to_enter": "magenta",
            "two_to_enter": "goldenrod",
            "three_to_enter": "orange",
            "four_to_enter": "pink",
            "five_to_enter": "cyan",
            "six_to_enter": "blue",
            "seven_to_enter": "purple",
            "eight_to_enter": "green",
            "nine_to_enter": "black"
        }

        # plot the gamma distribution model of the data
        if show_model:
            plt.plot(x,stats.gamma.pdf(x, alpha, loc=loc, scale=beta),'--', color=color[name_of_set],label=model_name)

        # force the histogram bin edges to always fall on multiples of 25, from 50 to 625
        bin_setter = [50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625]
        ys, binEdges = np.histogram(active_set, bins=bin_setter, normed=True)

        ##
        # xs should be the middle of the bin
        # (and using binEdges for this means that we can guarantee len(xs) == len(ys))
        xs = [(x + y) / 2 for x, y in zip(binEdges[:-1], binEdges[1:])]
        name = name_of_set + "\nn = " + str(num)

        # here we plot a rough fit to the histogram, so that multiple overlapping distributions can be seen at once
        if show_raw or not show_model:
            plt.plot(xs, ys,'-', color=color[name_of_set], label=name)
    
##
# This function tests whether two given sets have significantly different timings from one another
#
# @input timings - a dictionary of keypairs with their timings
# @input set_a - the first set of keypairs to test
# @input set_b - the first set of keypairs to test
def relevance_between_sets(timings, set_a, name_a, set_b, name_b):
    # collect all timings from all keypairs in the sets
    timings_for_a = [timings[x] for x in set_a]
    timings_for_a = [item for sublist in timings_for_a for item in sublist]

    timings_for_b = [timings[x] for x in set_b]
    timings_for_b = [item for sublist in timings_for_b for item in sublist]

    t_statistic, p_value = stats.ttest_ind(timings_for_a, timings_for_b, equal_var=False)
    print "%s vs. %s\nt: %f\np value: %f\n" % (name_a, name_b, t_statistic, p_value)

##
# This function compares every combination of two sets within a superset,
# to see if they have significantly different timings from one another
#
# @input timings - a dictionary of keypairs with their timings
# @input set_a - the first set of keypairs to test
# @input set_b - the first set of keypairs to test
def relevance_between_sets_from_superset(timings, superset):
    for name_a, name_b in itertools.combinations(superset, 2):
        relevance_between_sets(timings, all_sets[name_a], name_a, all_sets[name_b], name_b)

##
# Perform all functionality with data from all users
def main_all(args):
    timings = obtain_timings()
    timings = filter_timings(timings)
    
    flag_no_print = args.text_output == ""
    
    if flag_no_print:
        file_out = "all_users"
    else:
        file_out = args.text_output

    with cd('outputs'):
        with change_stdout(file_out + '.out'):
            if not flag_no_print:
                print "Analyzing all users:\n"
                print "~~~~~~~~~~~~~~~~~~~~~~\n"

            for name in list_of_lists[args.superlist]:
                hist_of_set(timings, all_sets[name], name, args.m, args.r)
                if not flag_no_print:
                    mean_std_of_set(timings, all_sets[name], name, "ALL")

            ##
            # Create the formatter using the function to_percent. This multiplies all the
            # default labels by 100, making them all percentages
            formatter = FuncFormatter(to_percent)

            # Set the formatter
            plt.gca().yaxis.set_major_formatter(formatter)

            # Labels on the graph
            plt.ylabel('Frequency')
            plt.xlabel('Interkey Time in ms')
            plt.title(args.plot_title + " across all users")
            plt.xlim([0,650])
            plt.grid(True)
            legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            with cd('plots'):
                plt.savefig(args.output_plot + '.png', bbox_extra_artists=(legend,), bbox_inches='tight')
            plt.clf()

            if not flag_no_print:
                print "~~~~~~~~~~~~~~~~~~~~~~\n"
                print "Calculating differences between sets:"
                print "---\n"
                relevance_between_sets_from_superset(timings, list_of_lists[args.superlist])

##
# Perform all functionality with data from individual users
def main_per_user(args):
    timings = obtain_timings_per_user()
    timings = filter_timings_per_user(timings)

    flag_no_print = args.text_output == ""
    
    if flag_no_print:
        file_out = "user"
    else:
        file_out = args.text_output

    i = 1

    for user_data in timings:
        with cd('outputs'):
            with change_stdout(file_out + '.' + str(i) + '.out'):
                if not flag_no_print:
                    print "Analyzing user " + str(i) + ":\n"
                    print "~~~~~~~~~~~~~~~~~~~~~~\n"

                for name in list_of_lists[args.superlist]:
                    hist_of_set(user_data, all_sets[name], name, args.m, args.r)
                    if not flag_no_print:
                        mean_std_of_set(user_data, all_sets[name], name, str(i))

                ##
                # Create the formatter using the function to_percent. This multiplies all the
                # default labels by 100, making them all percentages
                formatter = FuncFormatter(to_percent)

                # Set the formatter
                plt.gca().yaxis.set_major_formatter(formatter)

                # Labels on the graph
                plt.ylabel('Frequency')
                plt.xlabel('Interkey Time in ms')
                plt.title(args.plot_title + " for user " + str(i))
                plt.xlim([0,750])
                plt.grid(True)
                legend = plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

                with cd('plots'):
                    plt.savefig(args.output_plot + '.' + str(i) + '.png', bbox_extra_artists=(legend,), bbox_inches='tight')
                plt.clf()

                if not flag_no_print:
                    print "~~~~~~~~~~~~~~~~~~~~~~\n"
                    print "Calculating differences between sets:"
                    print "---\n"
                    relevance_between_sets_from_superset(user_data, list_of_lists[args.superlist])

                i += 1

# python timing_stats.py [-a] [-i] [-m] [-r] <superlist> <output_plot> [--plot_title "title of the plot"] [--text_output <text_output_file>]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('superlist', help='what list of keypair sets to compare')
    parser.add_argument('output_plot', help='the output file')
    parser.add_argument('--plot_title', help='title of the plot', default="PDF of key latencies")
    parser.add_argument('--text_output', help='file output for textual stats', default="")
    parser.add_argument('-a', help='all users mode', action="store_true")
    parser.add_argument('-i', help='individual users mode', action="store_true")
    parser.add_argument('-m', help='gamma model mode', action="store_true")
    parser.add_argument('-r', help='raw data mode', action="store_true")
    args = parser.parse_args()

    if args.a or not args.i:
        main_all(args)
    if args.i:
        main_per_user(args)
