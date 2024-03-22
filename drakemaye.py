import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit, minimize


def validate_inputs(input_pairs):
    for x, y in input_pairs:
        if x <= 0:
            raise ValueError(f"Negative buy-in found in input {input_pairs}.")
        if y < x:
            raise ValueError(
                f"Negative net payout found in input {input_pairs}."
            )

    sorted_buy_ins = sorted(input_pairs, key=lambda pair: pair[0])
    buy_ins, payouts = zip(*sorted_buy_ins)

    for i in range(1, len(payouts)):
        if payouts[i] < payouts[i - 1]:
            raise ValueError(
                f"Payouts must always increase, but as the buy-in of {buy_ins[i-1]} grows to {buy_ins[i]}, the payout decreases from {payouts[i-1]} to {payouts[i]}."
            )

    return np.array(buy_ins), np.array(payouts)


def calculate_probabilities(yes_data, no_data):
    # Extract buy-ins and payouts
    yes_buy_ins, yes_payouts = yes_data[0], yes_data[1]
    no_buy_ins, no_payouts = no_data[0], no_data[1]

    # Calculate average odds for "yes" and "no" bets
    yes_odds = np.mean(yes_payouts / yes_buy_ins)
    no_odds = np.mean(no_payouts / no_buy_ins)

    # Convert odds to implied probabilities
    yes_prob = 1 / (1 + yes_odds)
    no_prob = 1 - (1 / (1 + no_odds))

    # Normalize probabilities to sum up to 1 (or 100%)
    total_prob = yes_prob + no_prob
    yes_prob_normalized = yes_prob / total_prob
    no_prob_normalized = no_prob / total_prob

    return yes_prob_normalized, no_prob_normalized


def approximate_payouts(data):
    buy_ins, payouts = data
    initial_guess = [
        (max(payouts) - min(payouts)) / np.log(max(buy_ins)),
        1,
        min(payouts),
    ]
    fun = lambda x, a, b, c: a * np.log(x + b) + c
    (a, b, c), _ = curve_fit(
        fun, buy_ins, payouts, p0=initial_guess, maxfev=10000
    )
    return lambda x: fun(x, a, b, c)


def optimize(yes_data, no_data):
    yes_curve = approximate_payouts(yes_data)
    no_curve = approximate_payouts(no_data)
    yes_prob, no_prob = calculate_probabilities(yes_data, no_data)

    def expected_value(yes_buy, no_buy):
        yes_gain = yes_prob * yes_curve(yes_buy)
        no_gain = no_prob * no_curve(no_buy)
        total_buy = yes_buy + no_buy
        return yes_gain + no_gain - total_buy

    def neg_expected_value(buys):
        return -expected_value(*buys)

    initial_guess = [10, 10]
    bounds = [(0, None), (0, None)]
    result = minimize(neg_expected_value, initial_guess, bounds=bounds)
    opt_yes_buy, opt_no_buy = result.x if result.success else (0, 0)
    opt_yes_buy, opt_no_buy = int(np.round(opt_yes_buy)), int(
        np.round(opt_no_buy)
    )
    opt_ev = expected_value(
        opt_yes_buy, opt_no_buy
    )  # Recalculate EV for rounded values
    print(
        f"Optimal YES buy: {opt_yes_buy}, Optimal NO buy: {opt_no_buy}, Optimal Expected Value: {opt_ev:.2f}"
    )

    # Grid for visualization
    yes_buy_range = np.linspace(0, max(yes_data[0]), 100)
    no_buy_range = np.linspace(0, max(no_data[0]), 100)
    yes_buy_mesh, no_buy_mesh = np.meshgrid(yes_buy_range, no_buy_range)
    expected_values = np.vectorize(expected_value)(yes_buy_mesh, no_buy_mesh)

    return (
        yes_buy_mesh,
        no_buy_mesh,
        expected_values,
        opt_yes_buy,
        opt_no_buy,
        opt_ev,
    )


def visualize(result):
    (
        yes_buy_mesh,
        no_buy_mesh,
        expected_values,
        opt_yes_buy,
        opt_no_buy,
        opt_ev,
    ) = result
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    surface = ax.plot_surface(
        yes_buy_mesh,
        no_buy_mesh,
        expected_values,
        cmap="viridis",
        edgecolor="none",
    )
    ax.scatter(
        opt_yes_buy, opt_no_buy, opt_ev, color="r", s=50
    )  # Optimal point

    fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)
    ax.set_xlabel("Buy YES")
    ax.set_ylabel("Buy NO")
    ax.set_zlabel("Expected Value")
    plt.show()


def main(yes_market, no_market):
    yes_data = validate_inputs(yes_market)
    no_data = validate_inputs(no_market)

    optimized_result = optimize(yes_data, no_data)
    visualize(optimized_result)


yes_drake = [(10, 35), (12, 41), (20, 68), (25, 85), (30, 101)]
no_drake = [(1, 14), (10, 28), (12, 30), (20, 41), (30, 55)]

yes_caleb = [(15, 17), (25, 29), (35, 40), (45, 52), (60, 69)]
no_caleb = [(5, 112), (15, 300), (25, 451), (35, 573), (45, 674)]

main(yes_caleb, no_caleb)
