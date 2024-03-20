import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.optimize import curve_fit

def graph_models(data):
    x_data, y_data = data
    x_max = max(x_data)
    x_range = np.linspace(0, 3 * x_max, 400)

    [
        exp_model,
        log_model,
        pow_model,
        inv_model
    ] = [
        approximate_payouts(fun, data) for fun in [
            "exp",
            "log",
            "pow",
            "inv"
        ]
    ]

    # Plotting
    plt.figure(figsize=(10, 6))
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
    plt.show()

def report(funs):
    print("Payouts for a $50 bet:")
    for name, fun in zip(["exp", "log", "pow", "inv"], funs):
        print(round(fun(50)))

def validate_inputs(input_pairs):
    for x, y in input_pairs:
        if x <= 0:
            raise ValueError(f"Negative buy-in found in input {input_pairs}.")
        if y < x:
            raise ValueError(f"Negative net payout found in input {input_pairs}.")

    sorted_buy_ins = sorted(input_pairs, key=lambda pair: pair[0])
    buy_ins, payouts = zip(*sorted_buy_ins)

    for i in range(1, len(payouts)):
        if payouts[i] < payouts[i-1]:
            raise ValueError(
                f"Payouts must always increase, but as the buy-in of {buy_ins[i-1]} grows to {buy_ins[i]}, the payout decreases from {payouts[i-1]} to {payouts[i]}."
            )

    return np.array(buy_ins), np.array(payouts)

def approximate_payouts_2(fun, data):
    buy_ins, payouts = data
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
        buy_ins,
        payouts,
        p0=initial_guess,
        maxfev=10000
    )
    return lambda x: models[fun](x, a, b, c)

def approximate_payouts(data):
    buy_ins, payouts = data
    initial_guess = [(max(payouts) - min(payouts)) / np.log(max(buy_ins)), 1, min(payouts)]
    fun = lambda x, a, b, c: a * np.log(x + b) + c
    (a, b, c), _ = curve_fit(fun, buy_ins, payouts, p0=initial_guess, maxfev=10000)
    return lambda x: fun(x, a, b, c)

def optimize(yes_data, no_data, p_yes, p_no):
    yes_curve = approximate_payouts(yes_data)
    no_curve  = approximate_payouts(no_data)

    def expected_value(yes_buy, no_buy):
        total_buy = yes_buy + no_buy
        yes_gain = p_yes * yes_curve(yes_buy)
        no_gain = p_no * no_curve(no_buy)
        return yes_gain + no_gain - total_buy

    yes_buy_range = np.linspace(0, 30, 100)
    no_buy_range = np.linspace(0, 30, 100)
    yes_buy_mesh, no_buy_mesh = np.meshgrid(yes_buy_range, no_buy_range)

    # Vectorized calculation of expected values
    expected_values = expected_value(yes_buy_mesh, no_buy_mesh)

    return yes_buy_mesh, no_buy_mesh, expected_values

def visualize(result):
    yes_buy_mesh, no_buy_mesh, expected_values = result
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surface = ax.plot_surface(
        yes_buy_mesh,
        no_buy_mesh,
        expected_values,
        rstride=1,
        cstride=1,
        cmap='viridis',
        edgecolor='none'
    )
    fig.colorbar(surface, ax=ax, shrink=0.5, aspect=5)  # Adding a colorbar for clarity

    ax.set_xlabel('Buy YES')
    ax.set_ylabel('Buy NO')
    ax.set_zlabel('Expected Value')
    plt.show()

def main(yes_market, no_market):
    yes_data = validate_inputs(yes_market)
    no_data = validate_inputs(no_market)
    
    optimized_result = optimize(yes_data, no_data, 0.23, 0.77)
    visualize(optimized_result)

yes_market = [(10, 35), (12, 41), (20, 68), (25, 85), (30, 101)]
no_market = [(1, 14), (10, 28), (12, 30), (20, 41), (30, 55)]
main(yes_market, no_market)