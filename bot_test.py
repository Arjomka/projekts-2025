
test_code = [
    "import pytest",
    "from math import isclose",
    "",
    "#",
    "def calculate_targets(weight, fat_percent, lifestyle_factor, goal_modifier):",
    "    lean_mass = weight * (1 - fat_percent / 100)",
    "    bmr = 370 + 21.6 * lean_mass",
    "    tdee = bmr * lifestyle_factor + goal_modifier",
    "    protein = lean_mass * 2.2",
    "    fat = lean_mass * 1.0",
    "    kcal_from_pf = protein * 4 + fat * 9",
    "    carbs = (tdee - kcal_from_pf) / 4",
    "    return round(tdee), round(protein), round(fat), round(carbs)",
    "",
    "# --- Veiksmes scenāriji ---",
    "def test_success_normal_input():",
    "    kcal, p, f, c = calculate_targets(80, 20, 1.55, 0)",
    "    assert kcal > 0 and p > 0 and f > 0 and c > 0",
    "",
    "def test_success_cutting():",
    "    kcal, p, f, c = calculate_targets(75, 15, 1.7, -300)",
    "    assert kcal < 3000",
    "",
    "# --- Lietošanas scenāriji ---",
    "def test_goal_maintenance():",
    "    kcal, p, f, c = calculate_targets(65, 18, 1.375, 0)",
    "    assert isclose(kcal, 2200, abs_tol=300)",
    "",
    "def test_goal_bulk():",
    "    kcal, p, f, c = calculate_targets(70, 15, 1.7, 300)",
    "    assert kcal > 2500",
    "",
    "def test_high_activity():",
    "    kcal, p, f, c = calculate_targets(90, 25, 1.9, 0)",
    "    assert p > 100 and c > 200",
    "",
    "def test_low_bodyfat():",
    "    kcal, p, f, c = calculate_targets(60, 5, 1.55, 0)",
    "    assert p > 100 and f > 50",
    "",
    "# --- Robežscenāriji ---",
    "def test_edge_zero_weight():",
    "    kcal, p, f, c = calculate_targets(0, 10, 1.55, 0)",
    "    assert kcal == 370 and p == 0 and f == 0 and c == 0",
    "",
    "def test_edge_100_percent_fat():",
    "    kcal, p, f, c = calculate_targets(100, 100, 1.55, 0)",
    "    assert kcal == 370 and p == 0 and f == 0 and c == 0",
]


test_file_path = "BOT.py"
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write("\n".join(test_code))

test_file_path
