##
# Tree class for the PIN inference software
##
from node import Node


class Tree:
    def __init__(self, model, t1, t2, t3, t4):
        self.root = Node(None, "e", model, 0)
        self.model = model
        self.timings = [t1, t2, t3, t4]
        self.build(self.root, 0)

    ##
    # @returns the root node of this tree
    ##
    def get_root(self):
        return self.root

    ##
    # This function builds a tree containing all possible 4 digit PINs
    # new_child = Node(parent, x, self.model, self.timings[level])
    ##
    def build(self, parent, level):
        if parent is not None and level < 4:
            for x in range(0, 10):
                new_child = Node(parent, x, self.model, self.timings[level])
                parent.add_child(new_child)
                self.build(new_child, level + 1)

    ##
    # This function ranks all possible PINs in the order of highest
    # to lowest probability
    ##
    def rank_by_probability(self):
        pin_list = self.extract()
        pin_sorted = sorted(pin_list, key=lambda x: x[1], reverse=True)
        return pin_sorted

    ##
    # This function extracts all possible PINs and their probabilities
    ##
    def extract(self):
        pin_list = []
        if self.root.get_children() is not None:
            pin_list = self.root.extract("", pin_list)
        return pin_list

# End of file
