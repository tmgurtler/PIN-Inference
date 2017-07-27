##
# Node class for the implementation of the PIN inference tree
##

from distance import Distance


class Node:
    def __init__(self, p_digit, digit):
        self.digit = digit
        self.probability = None
        self.distance = Distance(p_digit, digit)
        self.children = []

    ##
    # @returns the digit for this node
    ##
    def get_digit(self):
        return self.digit

    ##
    # @returns the probability for this node
    ##
    def get_probability(self):
        return self.probability

    ##
    # @returns the distance for this node
    ##
    def get_distance(self):
        return self.distance.get_distance()

    ##
    # @returns the list of children for this node
    ##
    def get_children(self):
        return self.children

    ##
    # This function calculates the probability of this node
    # in regards to this node's parent probability
    ##
    def calc_probability(self, parent, model, timing):
        self.probability = parent.probability()\
                           * model.probability(timing, self.distance)

    ##
    # This function adds the given child to the list of children
    # for this node
    ##
    def add_child(self, child):
        self.children.append(child)

    ##
    # This function displays information about this node and its children
    def display(self, level):
        if level == 0:
            print(self.digit)
        else:
            print("\t"*level, str(self.digit) + " dist: " +
                              self.distance.get_distance() + " prob: " +
                              str(self.probability))

        level += 1
        for child in self.children:
            child.display(level)

    ##
    # Function that calculates the number of nodes in the tree
    ##
    def size(self):
        count = 1
        for child in self.children:
            count += child.size()
        return count

# End of file
