"""
Techno-economic analysis for continuous-flow ibuprofen electrosynthesis.

This script reproduces the economic figures reported in the manuscript:

    Figure 4 - Levelized Cost of Production (LCOP) breakdown
    Figure 5 - Raw-material cost contribution breakdown

The economic inputs were obtained from the AVEVA Process Simulation model.
The calculations convert annual costs, capital costs, and instantaneous
cost rates into contributions expressed in USD per tonne of ibuprofen.

Required packages:
    numpy
    matplotlib
"""

import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# GENERAL TECHNO-ECONOMIC ASSUMPTIONS
# =============================================================================

DISCOUNT_RATE = 0.10
PROJECT_LIFETIME_YEARS = 20
OPERATING_DAYS_PER_YEAR = 330
PRODUCT_FLOW_KG_H = 610.0

OPERATING_SECONDS_PER_YEAR = 3600 * 24 * OPERATING_DAYS_PER_YEAR

PRODUCT_FLOW_KG_S = PRODUCT_FLOW_KG_H / 3600


def calculate_capital_recovery_factor(discount_rate, lifetime_years):
    """Calculate the capital recovery factor (CRF)."""
    return (
        discount_rate
        * (1 + discount_rate) ** lifetime_years
        / ((1 + discount_rate) ** lifetime_years - 1)
    )


CRF = calculate_capital_recovery_factor(
    DISCOUNT_RATE,
    PROJECT_LIFETIME_YEARS,
)


# =============================================================================
# COLOR PALETTE
# =============================================================================

# Okabe-Ito colorblind-friendly palette
OKABE_ITO = {
    "blue": "#0072B2",
    "orange": "#D55E00",
    "green": "#009E73",
    "vermillion": "#E69F00",
    "sky_blue": "#56B4E9",
    "purple": "#CC79A7",
    "gray": "#999999",
}


# =============================================================================
# AVEVA PROCESS SIMULATION OUTPUTS
# =============================================================================

# Economic results for the two IL-price scenarios.
#
# Units:
#   utility_musd_per_year       = million USD/year
#   raw_material_musd_per_year  = million USD/year
#   capital_musd                = million USD
#   maintenance_musd_per_year   = million USD/year
#   labor_musd_per_year         = million USD/year
#   product_flow_kg_s           = kg/s


HIGH_IL_PRICE_CASE = {
    "label": r"IL price: \$290 kg$^{-1}$",
    "utility_musd_per_year": 2371234.07882832 / 1e6,
    "raw_material_musd_per_year": 56146916.79564739 / 1e6,
    "capital_musd": 41.633094969591461,
    "maintenance_musd_per_year": 751855.048395998 / 1e6,
    "labor_musd_per_year": 0.8,
    "product_flow_kg_s": 610 / 3600,
}


LOW_IL_PRICE_CASE = {
    "label": r"IL price: \$29 kg$^{-1}$",
    "utility_musd_per_year": 2377557.3036541576 / 1e6,
    "raw_material_musd_per_year": 23739774.932467852 / 1e6,
    "capital_musd": 41.722084070628171,
    "maintenance_musd_per_year": 753462.108954804 / 1e6,
    "labor_musd_per_year": 0.8,
    "product_flow_kg_s": 610 / 3600,
}


ECONOMIC_CASES = [
    HIGH_IL_PRICE_CASE,
    LOW_IL_PRICE_CASE,
]


# =============================================================================
# AVEVA RAW-MATERIAL COST RATES
# =============================================================================

# Cost rates used to generate the raw-material contribution breakdown.
# Values are given in USD/s.

IL_MAKEUP_290_USD_PER_S = 1.2193775348101577
IL_MAKEUP_29_USD_PER_S = 0.12193775348103331
MTBE_MAKEUP_USD_PER_S = 0.23088
PRECURSOR_MAKEUP_USD_PER_S = 0.17858971513913546


# =============================================================================
# UNIT-CONVERSION FUNCTIONS
# =============================================================================


def musd_per_year_to_usd_per_t(
    cost_musd_per_year,
    product_flow_kg_s,
):
    """
    Convert an annual operating cost from million USD/year to USD/t product.
    """
    annual_product_kg = product_flow_kg_s * OPERATING_SECONDS_PER_YEAR

    annual_product_t = annual_product_kg / 1000

    return cost_musd_per_year * 1e6 / annual_product_t


def capital_musd_to_usd_per_t(
    total_capital_musd,
    product_flow_kg_s,
):
    """
    Annualize total capital investment using the CRF and convert to USD/t.
    """
    annualized_capital_musd = total_capital_musd * CRF

    return musd_per_year_to_usd_per_t(
        annualized_capital_musd,
        product_flow_kg_s,
    )


def usd_per_s_to_usd_per_t(
    cost_usd_per_s,
    product_flow_kg_s,
):
    """
    Convert an instantaneous cost rate from USD/s to USD/t product.
    """
    annual_cost_usd = cost_usd_per_s * OPERATING_SECONDS_PER_YEAR

    annual_product_kg = product_flow_kg_s * OPERATING_SECONDS_PER_YEAR

    annual_product_t = annual_product_kg / 1000

    return annual_cost_usd / annual_product_t


# =============================================================================
# FIGURE 4: LCOP BREAKDOWN
# =============================================================================


def plot_lcop_breakdown():
    """
    Plot the LCOP contribution breakdown for the two IL-price scenarios.
    """
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 6))

    scenario_labels = [case["label"] for case in ECONOMIC_CASES]

    x = np.arange(len(ECONOMIC_CASES))
    width = 0.58

    # Calculate LCOP contributions for each scenario.
    process_values = []

    for case in ECONOMIC_CASES:
        product_flow = case["product_flow_kg_s"]

        process_values.append(
            [
                musd_per_year_to_usd_per_t(
                    case["utility_musd_per_year"],
                    product_flow,
                ),
                musd_per_year_to_usd_per_t(
                    case["raw_material_musd_per_year"],
                    product_flow,
                ),
                musd_per_year_to_usd_per_t(
                    case["maintenance_musd_per_year"],
                    product_flow,
                ),
                musd_per_year_to_usd_per_t(
                    case["labor_musd_per_year"],
                    product_flow,
                ),
                capital_musd_to_usd_per_t(
                    case["capital_musd"],
                    product_flow,
                ),
            ]
        )

    components = [
        ("Utility", OKABE_ITO["blue"]),
        ("Raw material", OKABE_ITO["orange"]),
        ("Maintenance", OKABE_ITO["green"]),
        ("Labor", OKABE_ITO["gray"]),
        ("Capital", OKABE_ITO["purple"]),
    ]

    bottom = np.zeros(len(ECONOMIC_CASES))

    for component_index, (component_name, color) in enumerate(components):
        heights = [values[component_index] for values in process_values]

        ax.bar(
            x,
            heights,
            width,
            bottom=bottom,
            label=component_name,
            color=color,
            edgecolor="white",
            linewidth=0.8,
        )

        bottom += np.array(heights)

    ax.set_xticks(x)
    ax.set_xticklabels(
        scenario_labels,
        fontweight="bold",
    )

    ax.set_ylabel(
        r"Levelized cost contribution (\$ t$^{-1}$)",
        fontweight="bold",
    )

    ax.set_title(
        "LCOP Breakdown",
        fontweight="bold",
        pad=15,
    )

    ax.legend(frameon=True)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, max(bottom) * 1.15)

    fig.tight_layout(rect=(0, 0.03, 1, 1))

    output_file = "economic_analysis_lcop_stacked_bar.png"

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved Figure 4 to {output_file}")


# =============================================================================
# FIGURE 5: RAW-MATERIAL COST BREAKDOWN
# =============================================================================


def plot_raw_material_breakdown():
    """
    Compare raw-material LCOP contributions for IL prices of
    290 USD/kg and 29 USD/kg.

    The numerical inputs are AVEVA-derived cost rates in USD/s.
    """

    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 6))

    product_flow_kg_s = HIGH_IL_PRICE_CASE["product_flow_kg_s"]

    # Total raw-material contribution from the high-IL-price AVEVA case.
    total_raw_per_t = musd_per_year_to_usd_per_t(
        HIGH_IL_PRICE_CASE["raw_material_musd_per_year"],
        product_flow_kg_s,
    )

    # Individual raw-material contributions.
    il_290_per_t = usd_per_s_to_usd_per_t(
        IL_MAKEUP_290_USD_PER_S,
        product_flow_kg_s,
    )

    il_29_per_t = usd_per_s_to_usd_per_t(
        IL_MAKEUP_29_USD_PER_S,
        product_flow_kg_s,
    )

    mtbe_per_t = usd_per_s_to_usd_per_t(
        MTBE_MAKEUP_USD_PER_S,
        product_flow_kg_s,
    )

    precursor_per_t = usd_per_s_to_usd_per_t(
        PRECURSOR_MAKEUP_USD_PER_S,
        product_flow_kg_s,
    )

    # Remaining raw-material contribution.
    #
    # This follows the calculation used in the original script:
    # "Other chemicals" is obtained from the high-IL-price case
    # and is kept unchanged between the two IL-price scenarios.
    other_chemicals_per_t = max(
        total_raw_per_t - il_290_per_t - mtbe_per_t - precursor_per_t,
        0.0,
    )

    scenario_values = [
        [
            il_290_per_t,
            mtbe_per_t,
            precursor_per_t,
            other_chemicals_per_t,
        ],
        [
            il_29_per_t,
            mtbe_per_t,
            precursor_per_t,
            other_chemicals_per_t,
        ],
    ]

    components = [
        ("IL make-up", OKABE_ITO["green"]),
        ("MTBE make-up", OKABE_ITO["orange"]),
        ("Fresh precursor", OKABE_ITO["sky_blue"]),
        ("Other chemicals", OKABE_ITO["gray"]),
    ]

    scenario_labels = [
        r"IL: \$290 kg$^{-1}$",
        r"IL: \$29 kg$^{-1}$",
    ]

    x = np.arange(len(scenario_values))
    width = 0.58
    bottom = np.zeros(len(scenario_values))

    for component_index, (label, color) in enumerate(components):
        heights = [values[component_index] for values in scenario_values]

        ax.bar(
            x,
            heights,
            width=width,
            bottom=bottom,
            label=label,
            color=color,
            edgecolor="white",
            linewidth=0.8,
        )

        bottom += np.array(heights)

    ax.set_xticks(x)
    ax.set_xticklabels(
        scenario_labels,
        fontweight="bold",
    )

    ax.set_ylabel(
        r"Raw material contribution to LCOP (\$ t$^{-1}$)",
        fontweight="bold",
    )

    ax.set_title(
        "Raw Materials Contribution Breakdown",
        fontweight="bold",
        pad=15,
    )

    ax.legend(frameon=True)
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, max(bottom) * 1.15)

    fig.tight_layout()

    output_file = "electrosynthesis_raw_material_il_price_comparison.png"

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Saved Figure 5 to {output_file}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    plot_lcop_breakdown()
    plot_raw_material_breakdown()
