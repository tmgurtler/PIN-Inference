from common import *
from tree import Tree

##
# This function infers PINs from a set of entries by using a model of Gamma distributions
#
# @input entries - the timings for the PINs we want to infer
# @input model - the Gamma distributions which predict timings
# @returns a list of the number of guesses that it takes to guess the PINs to type
def infer(entries, model):
    # get all the different entries from the dictionary and separate them out to the PIN level
    formatted_entry_list = [(e, pin) for e in actual_entries for pin, actual_entries in entries.items()]
    res = []

    for attempt, pin in formatted_entry_list:
        # make the guess tree of all PINs based on the probabilities suggested by our model
        t = Tree(attempt, model)

        # the tree will rank all pins by their likelihood
        ranked_choices = t.rank()

        # the number of guesses required is the position in this ranked list of the pin
        res.append(ranked_choices.index(pin))

    return res

def main():
    # get timings
    res = retrieve_data()
    keystrokes = preprocess_data(res)
    pin_entries_by_user = clean_data(keystrokes)

    all_res = []

    for holdout_user, test_entries in pin_entries_by_user.items():
        # hold out one user to test on
        training_data = {k,v for k,v in pin_entries_by_user.items() if k != holdout_user}
        
        # train our model on all the rest
        training_keypairs = parse_data(training_data)
        training_keypairs = filter_timings(training_keypairs)
        entry_model = Model(training_keypairs)

        # attempt to do inference on the held out user's PINs
        all_res.append(infer(test_entries, entry_model))

    do_something(all_res)
