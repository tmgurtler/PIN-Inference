##
# Distance class that determines the distance between key pairs for the PIN
# inference tree
##


class Distance:
    # All defined grouped distance sets for PIN inference
    all_sets = {
        "dist_zero": ["00", "11", "22", "33", "44", "55", "66", "77", "88", "99"],
        "dist_one": ["12", "23", "45", "56", "78", "89", "21", "32", "54", "65", "87", "98", "14", "47", "25", "58", "36", "69", "41", "74", "52", "85", "63", "96", "80", "08"],
        "dist_two": ["13", "46", "79", "31", "64", "97", "17", "28", "39", "71", "82", "93", "50", "05"],
        "dist_three": ["20", "02"],
        "dist_diagonal_one": ["15", "26", "24", "35", "48", "59", "57", "68", "70", "90", "51", "62", "42", "53", "84", "95", "75", "86", "07", "09"],
        "dist_diagonal_two": ["19", "37", "91", "73"],
        "dist_dogleg": ["16", "18", "27", "29", "34", "38", "43", "49", "40", "61", "67", "60", "72", "76", "81", "83", "92", "94", "04", "06"],
        "dist_long_dogleg": ["10", "30", "01", "03"],
        "zero_to_enter": ["0e"],
        "one_to_enter": ["1e"],
        "two_to_enter": ["2e"],
        "three_to_enter": ["3e"],
        "four_to_enter": ["4e"],
        "five_to_enter": ["5e"],
        "six_to_enter": ["6e"],
        "seven_to_enter": ["7e"],
        "eight_to_enter": ["8e"],
        "nine_to_enter": ["9e"]
    }

    def __init__(self, p_digit, next_digit):
        self.distance = self.find(p_digit, next_digit)

    ##
    # This function searches through all possible key pairs to find the
    # pair in question
    ##
    def find(self, p_digit, next_digit):
        search_pair = str(next_digit) + str(p_digit)
        
        for name, keypair_set in self.all_sets.items():
            if search_pair in keypair_set:
                return name

        print("Keypair [" + search_pair + "] cannot be found")
        return ""

    ##
    # @returns the distance of the key pair
    ##
    def get_distance(self):
        return self.distance

# End of file
