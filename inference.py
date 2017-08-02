from common import *
from scipy.stats import gamma
from tree import Tree
from model import Model
from tqdm import tqdm

def generate_distribution(timings, given_set):
        # only test the keypairs we actually have data for
        active_set = [timings[x] for x in given_set]
        active_set = [item for sublist in active_set for item in sublist]
        num_keypresses = len(active_set)

        # Fit a gamma distribution to the data observed
        alpha, loc, beta = gamma.fit(active_set)

        # return the gamma distribution model of the data
        return alpha, loc, beta

##
# This function infers PINs from a set of entries by using a model of Gamma distributions
#
# @input entries - the timings for the PINs we want to infer
# @input model - the Gamma distributions which predict timings
# @returns a list of the number of guesses that it takes to guess the PINs to type
def infer(entries, model):
    # get all the different entries from the dictionary and separate them out to the PIN level
    formatted_entry_list = [(e, pin) for pin, actual_entries in entries.items() for e in actual_entries]
    res = []

    for attempt, pin in tqdm(formatted_entry_list):
        # format attempt into ms timings
        attempt = [(time_b - time_a) for ((key_a, time_a), (key_b, time_b)) in zip(attempt[:-1], attempt[1:])]
        attempt = [int(math.floor(((time_diff.seconds * (10**6)) + time_diff.microseconds) / (10**3))) for time_diff in attempt]

        # make the guess tree of all PINs based on the probabilities suggested by our model
        t = Tree(model, *attempt)

        # the tree will rank all pins by their likelihood
        ranked_choices = t.rank_by_probability()

        just_pins = [choice[0] for choice in ranked_choices]

        # the number of guesses required is the position in this ranked list of the pin
        res.append(just_pins.index(("0000" + str(pin))[-4:]))

    return res

def main():
    # get timings
    res = retrieve_data()
    keystrokes = preprocess_data(res)
    pin_entries_by_user = clean_data(keystrokes)

    all_res = []

    for holdout_user, test_entries in tqdm(pin_entries_by_user.items()):
        # hold out one user to test on
        training_data = {k: v for k,v in pin_entries_by_user.items() if k != holdout_user}
        
        # train our model on all the rest
        training_keypairs = parse_data(training_data)
        training_keypairs = filter_timings(training_keypairs)
        entry_model = Model(training_keypairs)

        # attempt to do inference on the held out user's PINs
        all_res.append(infer(test_entries, entry_model))

    with change_stdout('new.out'):
        print all_res

def test():
    res = retrieve_data()
    keystrokes = preprocess_data(res)
    pin_entries_by_user = clean_data(keystrokes)
    training_keypairs = parse_data(pin_entries_by_user)
    training_keypairs = filter_timings(training_keypairs)
    entry_model = Model(training_keypairs)

    one_a, one_l, one_b = generate_distribution(training_keypairs, all_sets["dist_one"])
    dogleg_a, dogleg_l, dogleg_b = generate_distribution(training_keypairs, all_sets["dist_dogleg"])
    enter_a, enter_l, enter_b = generate_distribution(training_keypairs, all_sets["four_to_enter"])

    t1 = gamma.rvs(one_a, loc=one_l, scale=one_b)
    t2 = gamma.rvs(one_a, loc=one_l, scale=one_b)
    t3 = gamma.rvs(dogleg_a, loc=dogleg_l, scale=dogleg_b)
    t4 = gamma.rvs(enter_a, loc=enter_l, scale=enter_b)

    t = Tree(entry_model, t1, t2, t3, t4)
    with change_stdout("hi.out"):
        print t.rank_by_probability()

main()
