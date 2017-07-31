##
# Node class for the implementation of the PIN inference tree
##

from distance import Distance


class Node:
    def __init__(self, parent, digit, model, time):
        self.digit = digit

        if parent is None:
            self.distance = None
            self.probability = 1
        else:
            self.distance = Distance(parent.get_digit(), digit)
            self.probability = parent.get_probability()\
                * model.probability(self.distance.get_distance(), time)
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
    # This function adds the given child to the list of children
    # for this node
    ##
    def add_child(self, child):
        self.children.append(child)

    ##
    # This function determines if this node is a leaf node
    ##
    def is_leaf(self):
        if self.children.__len__() == 0:
            return True
        return False

    ##
    # This function extracts the individual PINs in relation to this node
    ##
    def extract(self, curr_str, pin_list):
        if self.get_digit() != "e":
            curr_str += str(self.get_digit())

        if self.is_leaf():
            return pin_list.append([curr_str, self.get_probability()])
        else:
            for child in self.children:
                child.extract(curr_str, pin_list)
        return pin_list


# End of file
