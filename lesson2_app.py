import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import geonamescache

st.title("Country Face-Off: Who Has a Giant City?")
st.write("Dot **size** = how many people live in the city. Dot **colour** = city class. "
         "Pick two countries, make a prediction, then let the data decide!")

# Step 1: load real cities (offline) and group them by country
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
by_country = {}
for c in gc.get_cities().values():
    if c["population"] >= 100_000:
        by_country.setdefault(c["countrycode"], []).append(c)
# keep only countries with at least 10 cities, then take each country's 10 biggest
top10 = {code: sorted(v, key=lambda c: c["population"], reverse=True)[:10]
         for code, v in by_country.items() if len(v) >= 10}
names = {countries[code]["name"]: code for code in top10}

# Step 2: the student picks two countries
left, right = st.columns(2)
name_a = left.selectbox("Country A", sorted(names), index=0)
name_b = right.selectbox("Country B", sorted(names), index=5)

# Step 3: the "giant city score" = biggest city's share of the top 10 (in %)
def giant_score(code):
    top = top10[code]
    return 100 * top[0]["population"] / sum(c["population"] for c in top)

# Step 4: draw one country (we use this function twice!)
def show(box, name):
    code = names[name]
    top = top10[code]
    box.subheader(name)
    m = folium.Map(tiles="Esri.WorldImagery")
    for c in top:
        colour = "red" if c["population"] >= 5_000_000 else "orange" if c["population"] >= 1_000_000 else "yellow"
        folium.CircleMarker([c["latitude"], c["longitude"]], radius=max(4, c["population"] ** 0.5 / 250),
                            color=colour, fill=True, fill_opacity=0.7,
                            tooltip=f"{c['name']}: {c['population']:,} people").add_to(m)
    m.fit_bounds([[min(c["latitude"] for c in top), min(c["longitude"] for c in top)],
                  [max(c["latitude"] for c in top), max(c["longitude"] for c in top)]])
    with box:
        st_folium(m, height=300, key=name, returned_objects=[])
        st.bar_chart(pd.DataFrame({"City": [c["name"] for c in top], "People living there": [c["population"] for c in top]}),
                     x="City", y="People living there", x_label="City (top 10)", y_label="People living there")

show(left, name_a)
show(right, name_b)
st.caption("Red = over 5 million people, orange = over 1 million, yellow = under 1 million.")

# Step 5: predict first, then reveal
st.subheader("Your prediction")
guess = st.radio("Which country depends more on ONE giant city?", [name_a, name_b], index=None)
if guess:
    a, b = giant_score(names[name_a]), giant_score(names[name_b])
    winner = name_a if a > b else name_b
    st.metric(f"{name_a}: biggest city = % of its top 10", f"{a:.0f}%")
    st.metric(f"{name_b}: biggest city = % of its top 10", f"{b:.0f}%")
    if guess == winner:
        st.success(f"You were right! {winner} is more top-heavy.")
    else:
        st.error(f"Surprise! It is {winner}. Look at the bar charts again.")
    st.info("Why do some countries have one giant city and others have many medium ones? "
            "Try new pairs, then look for a pattern. Next lesson: colour whole countries, not just dots!")
