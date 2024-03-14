import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.optimize import curve_fit

def validate_inputs(payouts):
    pairs_are_proper = all(x > 0 and y >= x for x, y in payouts)
    sorted_buy_ins = sorted(payouts, key=lambda pair: pair[0])
    buy_ins, payouts = zip(*sorted_buy_ins)
    is_monotonic = all(
        payouts[i] >= payouts[i-1] for i in range(1, len(payouts))
    )
    return (buy_ins, payouts, pairs_are_proper and is_monotonic)

def graph_models_and_points(x_data, y_data):
    x_max = max(x_data)
    x_range = np.linspace(0, 3 * x_max, 400)

    [
        exp_model,
        log_model,
        pow_model,
        inv_model
    ] = [
        approximate_payouts(fun, x_data, y_data) for fun in [
            "exp",
            "log",
            "pow",
            "inv"
        ]
    ]

    # Plotting
    plt.figure(figsize=(25, 15))
    plt.scatter(x_data, y_data, color='red', label='Data Points')  # Plot the data points
    plt.plot(x_range, [exp_model(x) for x in x_range], label='Exponential Model', linestyle='-')
    plt.plot(x_range, [log_model(x) for x in x_range], label='Logarithmic Model', linestyle='--')
    plt.plot(x_range, [pow_model(x) for x in x_range], label='Power Model', linestyle='-.')
    plt.plot(x_range, [inv_model(x) for x in x_range], label='Inverse Model', linestyle=':')

    plt.xlim(0, 5 * x_max)
    plt.ylim(bottom=0, top=5 * max(y_data))  # Ensure y-axis starts at 0
    plt.xlabel('Investment')
    plt.ylabel('Payout')
    plt.title('Model Comparisons with Input Data Points')
    plt.legend()
    plt.grid(True)
    # plt.show()

    return exp_model, log_model, pow_model, inv_model

def approximate_payouts(fun, buy_ins, payouts):
    models = {
        "exp": lambda x, a, b, c: a * np.exp(b * x) + c,
        "log": lambda x, a, b, c: a * np.log(x + b) + c,
        "pow": lambda x, a, b, c: a * (x ** b) + c,
        "inv": lambda x, a, b, c: a / (b * x + c)
    }

    if fun == "exp":
        initial_guess = [min(payouts), 0.1, min(payouts)]
    elif fun == "log":
        initial_guess = [(max(payouts) - min(payouts)) / np.log(max(buy_ins)), 1, min(payouts)]
    else:
        # Default initial guess for other models
        initial_guess = [1, 1, 1]

    (a, b, c), _ = curve_fit(
        models[fun],
        np.array(buy_ins),
        np.array(payouts),
        p0=initial_guess,
        maxfev=10000
    )
    return lambda x: models[fun](x, a, b, c)

def visualize(yes_payouts, no_payouts, p_yes, p_no):
    # Adapted for callable functions returned by approximate_payouts
    yes_payout = approximate_payouts(yes_payouts)
    no_payout = approximate_payouts(no_payouts)

    def expected_value(yes_buy, no_buy):
        return p_yes * yes_payout(yes_buy) + p_no * no_payout(no_buy) - yes_buy - no_buy

    yes_buy_range = np.linspace(0, 30, 100)
    no_buy_range = np.linspace(0, 30, 100)
    yes_buy_mesh, no_buy_mesh = np.meshgrid(yes_buy_range, no_buy_range)

    # Vectorized calculation of expected values
    expected_values = expected_value(yes_buy_mesh, no_buy_mesh)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surface = ax.plot_surface(yes_buy_mesh, no_buy_mesh, expected_values, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
    fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)  # Adding a colorbar for clarity

    ax.set_xlabel('Buy YES')
    ax.set_ylabel('Buy NO')
    ax.set_zlabel('Expected Value')
    plt.show()

def main(market_data):
    buy_ins, payouts, is_valid = validate_inputs(market_data)
    if not is_valid:
        return "Invalid inputs"

    funs = graph_models_and_points(buy_ins, payouts)
    # use funs[1], the logarithmic model

    print("Payouts for a $50 bet:")
    for name, fun in [("exp", "log", "pow", "inv"), funs]:
        print(round(fun(50)))

market_data = [(10, 35), (12, 41), (20, 68), (25, 85), (30, 101)]
main(market_data)