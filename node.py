##
# Node class for the implementation of the PIN inference tree
##

from distance import Distance


class Node:
    def __init__(self, parent, digit, model, time):
        self.digit = digit
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

    def is_leaf(self):
        if self.children.__len__() == 0:
            return True
        return False

    def num_leaves(self):
        count = 0
        if self.is_leaf():
            count += 1

        for child in self.children:
            count += child.num_leaves()

        return count


    ##
    # This function extracts the individial PINs in relation to this node
    ##
    def extract(self, curr_str):
        print(curr_str)
        if self.get_digit() != "e":
            curr_str += str(self.get_digit())

        for child in self.children:
            curr_str += child.extract(curr_str)
        return curr_str


# End of file
