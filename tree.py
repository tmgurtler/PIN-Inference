from node import Node


class Tree:
    def __init__(self, root):
        self.root = root
        self.build(self.root, 1)

    def get_root(self):
        return self.root

    # TODO check this builds correctly
    def build(self, parent, level):
        count = 0
        level += 1
        while level < 5:
            for x in range(0, 9):
                count += 1
                print(count)
                new_child = Node(x, parent.get_digit())
                parent.add_child(new_child)
                self.build(new_child, level)

    # TODO rank all PINs in order of highest to lowest probability
    def rank(self):
        return 0

    def display(self):
        self.root.display(0)

    def size(self):
        count = 1
        if self.root.get_children() is not None:
            count += self.root.size()

        print(count)
