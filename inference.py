from common import *
from tree import Tree

def infer(entries, model):
    formatted_entry_list = [(e, pin) for e in actual_entries for pin, actual_entries in entries.items()]
    res = []

    for attempt, pin in formatted_entry_list:
        t = Tree(attempt)
        ranked_choices = t.rank()
        res.append(ranked_choices.index(pin))

    return res

def main():
    res = retrieve_data()
    keystrokes = preprocess_data(res)
    pin_entries_by_user = clean_data(keystrokes)

    all_res = []

    for holdout_user, test_entries in pin_entries_by_user.items():
        training_data = {k,v for k,v in pin_entries_by_user.items() if k != holdout_user}
        training_keypairs = parse_data(training_data)
        training_keypairs = filter_timings(training_keypairs)
        
        entry_model = Model(training_keypairs)

        all_res.append(infer(test_entries, entry_model))

    do_something(all_res)
