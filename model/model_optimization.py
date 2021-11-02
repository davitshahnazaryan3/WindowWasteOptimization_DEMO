import constraint


class ModelOptimization:
    def __init__(self, tol=0.75):
        """
        All dimensions are in cm
        :param tol: float
        """
        self.TOL = tol
        self.TOL_CENTRAL = 0.0
        self.PROFILE = {"typical": 6.0}

    def get_solutions(self, w, p=None):
        """
        Gets all possible combinations that fit within a single profile length
        :param p: dict                      Profiles
        :param w: OrderedDict               Window properties
        :return: dict                       Combination of dimensions to be used for cutting within a profile
        """
        if p is None:
            p = self.PROFILE

        # Outputs
        outputs = {}

        # count number of unique dimensions and the amount of them
        # key=length, value=count
        windows = {}
        for profile in p:
            windows[profile] = {"dims": {}}

        # no window was created, so don't run analysis
        if w is None:
            return

        for window in w:
            # loop over each window
            if window is not None:
                # get quantity of window
                qnt = int(window["quantity"])
                # get type of window
                window_type = window["type"]

                for l in range(len(window["side"]["length"])):
                    length = window["side"]["length"][l]
                    profile_name = window["side"]["profile"][l]
                    if length is not None:
                        length = float(length)
                        # Get multiplication factor depending on type of window
                        # e.g. type==1, 2 sides for l of (1) and (2)
                        if window_type == 1:
                            factor = [2, 2]
                        elif window_type == 2:
                            factor = [3, 2, 2]
                        elif window_type == 3:
                            factor = [2, 2, 3]
                        else:
                            # type 4
                            factor = [2, 2, 2, 4]

                        # get length of side
                        if length in windows[profile_name]["dims"]:
                            windows[profile_name]["dims"][length] += 1 * qnt * factor[l-1]
                        else:
                            windows[profile_name]["dims"][length] = 1 * qnt * factor[l-1]

        # loop for each profile type and get all combinations pertaining to that profile type
        for profile_name in windows:
            if windows[profile_name]["dims"]:
                # profile length = target
                p_length = float(p[profile_name])

                # Get total sum of length
                total_length = sum([float(key) * val for key, val in windows[profile_name]["dims"].items()])
                windows[profile_name]["total_length"] = total_length

                # Check if any number is divisible by profile length without a remainder
                if any(map(lambda ele: p_length % float(ele) == 0, windows[profile_name]["dims"].keys())):
                    waste_min = p_length - total_length % p_length
                    if waste_min == p_length:
                        waste_min = 0.
                else:
                    waste_min = 2 * p_length - total_length % p_length

                windows[profile_name]["waste_min"] = waste_min

                # Create a list containing all possible lengths
                numbers = {}
                for key in windows[profile_name]["dims"].keys():
                    qnt = int(p_length / float(key))
                    numbers[key] = qnt

                combinations = self.get_combinations(numbers, p_length)

                # Into a dictionary with a unique identifier
                combos = {}
                cnt = 0
                for item in combinations:
                    combos[cnt] = item
                    cnt += 1

                # Extract the combinations to use as a solution
                solutions = self.extract_combinations(combos, windows[profile_name])
                outputs[profile_name] = solutions

        return outputs

    def extract_combinations(self, combinations, windows):
        # Initialize solutions
        solutions = {}

        # Tag to illustrate that all dimensions have been used
        dimensions_left = True

        # Identifier
        idx = 0

        while dimensions_left:
            # Select the combination with lowest waste
            while idx not in combinations:
                idx += 1
            combo = combinations[idx]

            # Add into the solutions
            if idx not in solutions:
                solutions[idx] = combo
                solutions[idx]["count"] = 1
            else:
                solutions[idx]["count"] += 1

            # Subtract quantity of lengths used
            for l in windows["dims"]:
                windows["dims"][l] -= combo[float(l)]

                # Continue until any of the dimensions reached quantity of zero
                if windows["dims"][l] == 0:
                    # Remove the combos containing the dimension
                    for i in list(combinations.keys()):
                        if combinations[i][float(l)] > 0:
                            combinations.pop(i)

                elif windows["dims"][l] < 0:
                    # discount the last added combo
                    solutions[idx]["count"] -= 1
                    # remove all combos containing the dimension that resulted in negative quantity
                    qnt_temp = windows["dims"][l] + combo[float(l)]
                    for i in list(combinations.keys()):
                        if combinations[i][float(l)] > qnt_temp:
                            combinations.pop(i)

                    # correct the quantity
                    for i in windows["dims"]:
                        windows["dims"][i] += combo[float(i)]

                # if all dimensions have been exhausted
                if not combinations:
                    dimensions_left = False

        return solutions

    def get_combinations(self, numbers, target):
        """
        Get all possible combinations
        :param numbers: dict
        :param target: float
        :return: dict
        """
        # Size and counts of each size in a window
        size = [float(x) for x in numbers.keys()]
        counts = list(numbers.values())

        # Create the problem
        problem = constraint.Problem()
        cnt = 0
        for v in size:
            v = float(v)
            problem.addVariable(v, range(counts[cnt] + 1))
            cnt += 1

        problem.addConstraint(constraint.MaxSumConstraint(target, list(size)), list(size))
        problem.addConstraint(constraint.MinSumConstraint(0.1, list(size)), list(size))

        # Get all possible combinations
        combinations = problem.getSolutions()

        # Get waste for each combination
        for i in range(len(combinations)):
            pair = combinations[i]
            s = 0
            for key, value in pair.items():
                s += key * value
            combinations[i]["waste"] = target - s

        # Order the combinations by increasing order based on waste (lowest weight to highest waste)
        self.quick_sort(0, len(combinations) - 1, combinations)

        return combinations

    def partition(self, start, end, arr):
        # initialize pivot's index to start
        pivot_index = start
        pivot = arr[pivot_index]["waste"]

        # run loop till start pointer crosses end pointer, and when it does swap the pivot with element on end pointer
        while start < end:
            # increment start pointer till it finds an element greater than pivot
            while start < len(arr) and arr[start]["waste"] <= pivot:
                start += 1

            # decrement end pointer till it finds an element less than pivot
            while arr[end]["waste"] > pivot:
                end -= 1

            # if start and end have not crossed each other, swap the numbers on start and end
            if start < end:
                arr[start], arr[end] = arr[end], arr[start]

        # swap the pivot element with element on end pointer.
        # this puts pivot on its correct sorted place
        arr[end], arr[pivot_index] = arr[pivot_index], arr[end]

        return end

    def quick_sort(self, start, end, arr):
        if start < end:
            # p is partitioning index, arr[p] is at right place
            p = self.partition(start, end, arr)

            # sort the elements before partition and after partition
            self.quick_sort(start, p - 1, arr)
            self.quick_sort(p + 1, end, arr)


if __name__ == "__main__":
    import timeit

    start_time = timeit.default_timer()
    main = ModelOptimization(tol=0.0)
    p = {"typical": 6.0, "a": 12.0}
    window = [None,
              {"side": {"length": [None, "0.5", "1.0"], "profile": [None, "typical", "typical"]},
               "quantity": "10", "type": 1},
              {"side": {"length": [None, "0.5", "1.0", "2.0"], "profile": [None, "typical", "typical", "typical"]},
               "quantity": "10", "type": 2},
              {"side": {"length": [None, "0.5", "1.2"], "profile": [None, "a", "a"]},
               "quantity": "20", "type": 1}]

    outputs = main.get_solutions(window, p)
    print(outputs)

    elapsed = timeit.default_timer() - start_time
    print('Running time: ', int(elapsed * 10 ** 1) / 10 ** 1, ' seconds')
    print('Running time: ', int((elapsed / 60.) * 10 ** 2) / 10 ** 2, ' minutes')
