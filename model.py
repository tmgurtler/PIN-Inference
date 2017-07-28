##
# Model class that calculates probabilities given timings

from common import *
from scipy.stats import gamma
from math import log

class Model:
    ##
    # Constructor for model that takes in keypairs and automatically generates
    # the gamma distributions and set probabilities for them.
    #
    # @input keypairs - a dictionary of lists of ints,
    #                   where the dictionary connects a keypair (e.g. "12")
    #                   to every interkey timing used to enter it
    def __init__(self, keypairs):
        self.__distributions = defaultdict(lambda: None)
        self.__set_probabilities = defaultdict(lambda: 0.0)
        total = 0
        
        for set_name in list_of_lists["model_sets"]:
            self.__distributions[set_name], num_keypresses = self.__generate_distribution(keypairs, all_sets[set_name])
            self.__set_probabilities[set_name] = float(num_keypresses)
            total += num_keypresses

        for key in self.__set_probabilities:
            self.__set_probabilities[key] = self.__set_probabilities[key] / total
   
    ##
    # This function produces an individual gamma distribution for a given set
    #
    # @input timings - the set of all timings
    # @input given_set - the set to produce a distribution for
    #
    # @returns the distribution for that set and the number of keypresses seen in that set
    def __generate_distribution(self, timings, given_set):
        # only test the keypairs we actually have data for
        active_set = [timings[x] for x in given_set]
        active_set = [item for sublist in active_set for item in sublist]
        num_keypresses = len(active_set)

        # Fit a gamma distribution to the data observed
        alpha, loc, beta = gamma.fit(active_set)

        # return the gamma distribution model of the data
        return gamma(alpha, loc=loc, scale=beta), num_keypresses

    ##
    # This function gives the logprob of a keypress being in a particular set
    # given that we observed a given timing
    #
    # @input trial_set - the set whose distribution we want to test with
    # @input timing - the timing we are testing
    #
    # @returns the logprob of this conditional event
    def probability(trial_set, timing):
        return log(__distributions[trial_set].pdf(timing)) + log(__set_probabilities[trial_set])
