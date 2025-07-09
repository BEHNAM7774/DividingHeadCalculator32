
import streamlit as st
from fractions import Fraction
from math import gcd
import pandas as pd

def calculate_indexing(N, plates, worm_teeth=40, diff_a=0, diff_b=1, max_error=100):
    base_turns = Fraction(worm_teeth, N)
    full_turns = base_turns.numerator // base_turns.denominator
    frac_part = base_turns - full_turns
    results = []

    for mode, frac in [('Simple', frac_part),
                       ('Differential +', frac_part + Fraction(diff_a, diff_b)),
                       ('Differential -', frac_part - Fraction(diff_a, diff_b)) if diff_a != 0 else (None, None)]:
        if mode is None:
            continue
        for plate in plates:
            b = round(frac * plate)
            if b == 0 or b >= plate:
                continue
            actual_frac = Fraction(b, plate)
            error = abs(float(actual_frac - frac)) * 100
            if error <= max_error:
                results.append((mode, plate, b, str(actual_frac), error, full_turns))

    return sorted(results, key=lambda x: x[4])

st.title("Dividing Head Calculator - Streamlit Version")

st.sidebar.header("Settings")

N = st.sidebar.number_input("Number of Divisions (N)", min_value=1, max_value=1000, value=73)
worm_teeth = st.sidebar.number_input("Worm Gear Teeth", min_value=1, max_value=100, value=40)
diff_a = st.sidebar.number_input("Differential a", min_value=0, max_value=100, value=0)
diff_b = st.sidebar.number_input("Differential b", min_value=1, max_value=100, value=1)
max_error = st.sidebar.slider("Max Error (%)", min_value=0.0, max_value=5.0, value=0.5, step=0.01)

standard_plates = [15, 16, 18, 20, 21, 24, 27, 28, 30, 33, 36, 37, 39, 40,
                   41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]

plates_selected = st.sidebar.multiselect("Select Plates", standard_plates, default=standard_plates)

if st.sidebar.button("Calculate"):
    if not plates_selected:
        st.error("Please select at least one plate.")
    else:
        results = calculate_indexing(N, plates_selected, worm_teeth, diff_a, diff_b, max_error)
        if not results:
            st.warning("No results found with the given error threshold.")
        else:
            df = pd.DataFrame(results, columns=["Mode", "Plate", "b", "Fraction", "Error (%)", "Full Turns"])
            st.dataframe(df)

            # Show best result
            best = results[0]
            st.markdown(f"### Best Result:\n- Mode: **{best[0]}**\n- Plate: **{best[1]} holes**\n- b: **{best[2]}**\n- Fraction: **{best[3]}**\n- Error: **{best[4]:.4f}%**\n- Full Turns: **{best[5]}**")

            # Export CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download CSV", data=csv, file_name="dividing_head_results.csv", mime="text/csv")
