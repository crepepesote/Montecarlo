from data_models import *
from scipy.stats import chi2, norm
import math
import numpy as np
import pandas as pd
import json

ACCEPTABLE_ERROR = 0.05 # alfa
ACCEPTABLE_PERCENT = 0.95 # aceptation percent
ks_values = None

def generate_numbers(conf):
    a = 1 + 2*conf['k']
    m = 2**conf['g']
    numbers = []
    X_i_minus_1 = conf['X0']
    for i in range(1, (m//2)+1):
        X_i = ((a * X_i_minus_1) + conf['c']) % m
        X_i_minus_1 = X_i
        R_i = X_i / (m - 1)
        numbers.append(R_i)
    return numbers

def test_numbers(numbers):
    return averages_test(numbers) and variance_test(numbers) and chi_2_test(numbers) and ks_test(numbers) and poker_test(numbers)

def averages_test(nums):
    n = len(nums)
    r = sum(nums) / n
    one_min_alfa_mid = 1 - (ACCEPTABLE_ERROR / 2)
    z = float(norm.ppf(one_min_alfa_mid))
    li = 0.5 - z * (1 / math.sqrt(12 * n))
    ls = 0.5 + z * (1 / math.sqrt(12 * n))
    return li <= r <= ls

def variance_test(nums):
    n = len(nums)
    r = sum(nums) / n
    variance = sum((x - r) ** 2 for x in nums) / n
    alfa_mid = ACCEPTABLE_ERROR / 2
    one_min_alfa_mid = 1 - alfa_mid
    gl = n - 1
    chi_2_alfa_mid = float(chi2.ppf(1 - alfa_mid, gl))
    chi_2_one_min_alfa_mid = float(chi2.ppf(1 - one_min_alfa_mid, gl))
    li = chi_2_alfa_mid / (12 * (n-1))
    ls = chi_2_one_min_alfa_mid / (12 * (n-1))
    return li >= variance >= ls

def chi_2_test(nums):
    n = len(nums)
    data = generate_intervals(nums)
    intervals = data["Inters"]
    frecuencies = data["Frecs"]
    expected_frecuencies = [n / len(intervals) for i in range(0, len(intervals))]
    chi_2_values = [
        ((frecuencies[i] - expected_frecuencies[i]) ** 2) / expected_frecuencies[i]
        for i in range(len(intervals))
    ]
    chi_2_statistic = sum(chi_2_values)
    gl = len(intervals) - 1
    chi_inv_value = float(chi2.ppf(1-ACCEPTABLE_ERROR, gl))
    return chi_2_statistic <= chi_inv_value

def ks_test(nums):
    n = len(nums)
    data = generate_intervals(nums)
    intervals = data["Inters"]
    F_observed = data["Frecs"]
    F_obt_acum = [sum(F_observed[0:i+1] if i < len(F_observed) -1 else F_observed) for i in range(0, len(F_observed))]
    P_obt = [F_obt_acum[i] / n for i in range(0, len(F_obt_acum))]
    frec_exp = n / len(intervals)
    F_expected_acum = [frec_exp * (i+1) for i in range(0, len(F_observed))]
    P_expected_acum = [F_expected_acum[i] / n for i in range(0, len(F_expected_acum))]
    differences = [abs(P_obt[i] - P_expected_acum[i]) for i in range(0, len(P_obt))]
    D_max = max(differences)
    D_critical = get_ks_value(n) if n <= 50 else 1.36 / math.sqrt(n)
    return D_max <= D_critical

def poker_test(nums):
    n = len(nums)
    str_nums = [f'{int(num * 100000):05}' for num in nums]
    categories = {"TD": 0, "1P": 0, "2P": 0, "1T": 0, "F": 0, "P": 0, "Q": 0}
    for num in str_nums:
        counts = {digit: num.count(digit) for digit in set(num)}
        count_values = sorted(counts.values(), reverse=True)
        if count_values == [1, 1, 1, 1, 1]:
            categories["TD"] += 1  # Todos diferentes
        elif count_values == [2, 1, 1, 1]:
            categories["1P"] += 1  # Un par
        elif count_values == [2, 2, 1]:
            categories["2P"] += 1  # Dos pares
        elif count_values == [3, 1, 1]:
            categories["1T"] += 1  # Un trío
        elif count_values == [3, 2]:
            categories["F"] += 1  # Full
        elif count_values == [4, 1]:
            categories["P"] += 1  # Póker
        elif count_values == [5]:
            categories["Q"] += 1  # Quintilla
    expected_probs = {"TD": 0.3024, "1P": 0.5040, "2P": 0.1080, "1T": 0.0720, "F": 0.0090, "P": 0.0045, "Q": 0.0001}
    expected_freqs = {cat: expected_probs[cat] * n for cat in categories}
    error_values = [(categories[cat] - expected_freqs[cat])**2 / expected_freqs[cat] for cat in categories]
    errors_sum = sum(error_values)
    gl = len(categories) - 1
    chi_inv_value = chi2.ppf(1 - ACCEPTABLE_ERROR, gl)
    return errors_sum <= chi_inv_value

def get_ks_value(n):
    if not ks_values:
        with open('ks_values.json', 'r') as f:
            ks_values = json.load(f)
    for value in ks_values:
        if value["n"] == n:
            return value["value"]
    return None

def generate_intervals(nums):
    k = int(1 + 3.322 * np.log10(len(nums)))
    lims = np.linspace(min(nums), max(nums), k + 1)
    intervs = pd.cut(nums, bins=lims, include_lowest=True)
    table = pd.DataFrame({
        "Inters": intervs.value_counts().index,
        "Frecs": intervs.value_counts().values
    }).reset_index(drop=True)
    frecs = table["Frecs"].astype(int).to_list()
    inters = [[float(intervalo.left), float(intervalo.right)] for intervalo in table["Inters"]]
    return { "Inters": inters, "Frecs": frecs }