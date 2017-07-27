##
# Distance class that determines the distance between key pairs for the PIN
# inference tree
##


class Distance:
    # All defined grouped distance sets for PIN inference
    d_zero = ["00", "11", "22", "33", "44", "55", "66", "77", "88", "99"]
    d_one = ["12", "23", "45", "56", "78", "89", "21", "32", "54", "65",
             "87", "98", "14", "47", "25", "58", "36", "69", "41", "74",
             "52", "85", "63", "96", "80", "08"]
    d_two = ["13", "46", "79", "31", "64", "97", "17", "28", "39", "71",
             "82", "93", "50", "05", "16", "18", "27", "29", "34", "38",
             "43", "49", "40", "61", "67", "60", "72", "76", "81", "83",
             "92", "94", "04", "06", "15", "26", "24", "35", "48", "59",
             "57", "68", "70", "90", "51", "62", "42", "53", "84", "95",
             "75", "86", "07", "09"]
    d_three = ["20", "02", "10", "30", "01", "03", "19", "37", "91", "73"]
    d_to_enter = ["0e", "1e", "2e", "3e", "4e", "5e", "6e", "7e", "8e", "9e"]

    # List of above sets for iterations
    all_distance_sets = [d_zero, d_one, d_two, d_three, d_to_enter]
    set_names = ["0", "1", "2", "3", "e"]

    def __init__(self, p_digit, next_digit):
        self.distance = self.find(p_digit, next_digit)

    ##
    # This function searches through all possible key pairs to find the
    # pair in question
    ##
    def find(self, p_digit, next_digit):
        search_pair = str(next_digit) + str(p_digit)
        set_num = 0
        found = False
        for dist_set in self.all_distance_sets:
            for keypair in dist_set:
                if keypair == search_pair:
                    found = True
                    break
            if found:
                break
            set_num += 1

        if set_num > 4:
            print("Keypair [" + search_pair + "] cannot be found")
        else:
            return self.set_names[set_num]

    ##
    # @returns the distance of the key pair
    ##
    def get_distance(self):
        return self.distance

# End of file
