##
# Tree class for the PIN inference software
##
from node import Node


class Tree:
    def __init__(self, model, t1, t2, t3, t4):
        self.root = Node("e", 0)
        self.model = model
        self.build(self.root, 0)
        self.timings = [t1, t2, t3, t4]

    ##
    # @returns the root node of this tree
    ##
    def get_root(self):
        return self.root

    ##
    # This function builds a tree containing all possible 4 digit PINs
    ##
    def build(self, parent, level):
        if parent is not None and level < 4:
            for x in range(0, 10):
                new_child = Node(parent, x, self.model, self.timings[level])
                parent.add_child(new_child)
                self.build(new_child, level + 1)

    # TODO rank all PINs in order of highest to lowest probability
    # This function ranks all possible PINs in the order of highest
    # to lowest probability
    ##
    def rank(self):
        pin_list = self.extract()
        print(pin_list.__len__())


    ##
    # This function extracts all possible PINs and their probabilities
    ##
    def extract(self):
        pin_list = []
        if self.root.get_children() is not None:
            pin_list.extend(self.root.extract(""))
        return pin_list

    ##
    # This function displays the contents of this tree
    ##
    def display(self):
        self.root.display(0)

    ##
    # This function counts the total number of nodes in this tree
    ##
    def size(self):
        count = 0
        if self.root.get_children() is not None:
            count += self.root.size()
        print(count)

    def num_leaves(self):
        count = 0
        if self.root.is_leaf():
            return 1
        count += self.root.num_leaves()
        return count

# End of file
