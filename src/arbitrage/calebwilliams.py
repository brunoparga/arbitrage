from typing import List, Tuple


class Market:
    def __init__(
        self,
        name: str,
        url: str,
        initial_probability: int,
        yes_bets: List[Tuple[int, int, int]],
        no_bets: List[Tuple[int, int, int]],
    ):
        self.name = name
        self.url = url
        self.initial_probability = initial_probability
        self.yes_bets = yes_bets
        self.no_bets = no_bets

    @classmethod
    def get_input(cls) -> "Market":
        name = input("Enter the name of the market: ")
        url = input("Enter the URL of the market: ")
        initial_probability = int(input("Enter the initial probability: "))

        yes_bets = []
        no_bets = []

        # Get YES bets
        while True:
            bet_input = input(
                "Enter a YES bet triplet (buy_in,payout,prob) or press Enter to finish: "
            )
            if not bet_input:
                break
            buy_in, payout, prob = map(int, bet_input.split(","))
            yes_bets.append((buy_in, payout, prob))

        # Get NO bets
        while True:
            bet_input = input(
                "Enter a NO bet triplet (buy_in,payout,prob) or press Enter to finish: "
            )
            if not bet_input:
                break
            buy_in, payout, prob = map(int, bet_input.split(","))
            no_bets.append((buy_in, payout, prob))

        cls.validate_input(yes_bets)
        cls.validate_input(no_bets)

        return cls(name, url, initial_probability, yes_bets, no_bets)

    @staticmethod
    def validate_input(input_list: List[Tuple[int, int, int]]) -> None:
        if not input_list:
            return

        if not isinstance(input_list, list):
            raise ValueError(f"Input must be a list, got {input_list}.")

        if len(input_list) < 2:
            raise ValueError("Input list must have at least two elements.")

        def is_3_tuple(element: Tuple[int, int, int]) -> bool:
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


market = Market.get_input()
