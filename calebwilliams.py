def validate_input(input_list):
    if not isinstance(input_list, list):
        raise ValueError(f"Input must be a list, got {input_list}.")

    if len(input_list) < 2:
        raise ValueError("Input list must have at least two elements.")

    def is_3_tuple(element):
        return type(element) is tuple and len(element) == 3

    for i in range(len(input_list)):
        element = input_list[i]
        if not is_3_tuple(element):
            raise ValueError(
                f"Every element in the list must be a 3-tuple, got {element}."
            )

        buy_in, payout, prob = element

        # buy-ins can be zero if I already have a position in the market
        if buy_in < 0:
            raise ValueError(f"All buy-ins must be positive, got {buy_in}")

        if payout < buy_in:
            raise ValueError(
                f"Found a negative net payout: buy-in {buy_in}, payout {payout}."
            )

        if prob <= 0 or prob >= 100:
            raise ValueError(
                f"All probabilities must be between 0 and 100, got {prob}"
            )

        if i < len(input_list) - 1:
            next_buy_in, next_payout, next_prob = input_list[i + 1]
            if payout > next_payout:
                raise ValueError(
                    f"Payouts must always increase, but as the buy-in of {buy_in} grows to {next_buy_in}, the payout decreases from {payout} to {next_payout}."
                )

            if i < len(input_list) - 2:
                _, _, two_probs_down = input_list[i + 2]
                if (prob > next_prob and next_prob < two_probs_down) or (
                    prob < next_prob and next_prob > two_probs_down
                ):
                    raise ValueError(
                        "Probabilities must either always increase or always decrease."
                    )


class Market:
    def __init__(self, name, initial_probability, yes_bets, no_bets):
        self.name = name
        self.initial_probability = initial_probability
        self.yes_bets = yes_bets
        self.no_bets = no_bets
        validate_input(yes_bets)
        validate_input(no_bets)


yes_caleb = [
    (15, 17, 86),
    (25, 29, 87),
    (35, 40, 87),
    (45, 52, 88),
    (60, 69, 89),
]
no_caleb = [
    (5, 112, 95),
    (15, 300, 94),
    (25, 451, 93),
    (35, 573, 91),
    (45, 674, 89),
]
Market("Foo", 96, yes_caleb, no_caleb)
