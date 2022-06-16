# Read in packages
import pandas as pd
import streamlit as st
import plotly.express as px
import datetime

# Set up webpage
st.set_page_config(page_title="CS4337 Covid-19 Data Analysis")
st.header("CS4337 Covid-19 Data Analysis")
st.subheader("By Aisling Smyth 18233511")

# Read in Data
confirmed_data = 'https://github.com/Aisling-Smyth/COVID-19-Data-Analysis/blob/main/time_series_covid19_confirmed_global.xlsx?raw=true'
deaths_data = 'https://github.com/Aisling-Smyth/COVID-19-Data-Analysis/blob/main/time_series_covid19_deaths_global.xlsx?raw=true'
recovered_data = 'https://github.com/Aisling-Smyth/COVID-19-Data-Analysis/blob/main/time_series_covid19_recovered_global.xlsx?raw=true'

# Let user choose which dataset they want in a sidebar
st.sidebar.title("Dataset Options:")
st.sidebar.markdown(
    """Please note that recovered cases are only recorded until
    04/08/2020, and some countries (such as Ireland, UK, Spain)
     stopped recording this sooner, therefore recovery analysis is not
      entirely accurate due to an incomplete dataset."""
)
choose_dataset = st.sidebar.selectbox(
    "Which Global Dataset's Analytics Would You Like To View?",
    ("Confirmed", "Deaths", "Recovered"),
)

# Set dataset based on user's choice
if choose_dataset == "Confirmed":
    df = pd.read_excel(confirmed_data)
    set = "Confirmed"
if choose_dataset == "Deaths":
    df = pd.read_excel(deaths_data)
    set = "Deaths"
if choose_dataset == "Recovered":
    df = pd.read_excel(recovered_data)
    set = "Recovered"

# Rename columns (from datetime to date)
for n in df:
    if isinstance(n, datetime.datetime):
        df = df.rename(columns={n: n.date()})

# Plot where I have data for on map
st.map(df)

# Remove now unnecessary latitude and longitude columns
df = df.drop(columns=["lat", "lon"])

# Leave gap before next section
st.text(" ")
st.text(" ")

st.subheader(
    "Please note that only the worst 9 European countries (as of"
    " 22/12/21 - United Kingdom, Russia, Turkey, France, Germany,"
    " Spain, Italy, Poland, Ukraine) plus Ireland are included"
    " in this analysis"
)

# Subset data to include 9 worst European Countries (as of 22/12 -
# https://www.statista.com/statistics/1104837/
# coronavirus-cases-europe-by-country/)
# plus Ireland
included_countries = [
    "Ireland",
    "United Kingdom",
    "Russia",
    "Turkey",
    "France",
    "Germany",
    "Spain",
    "Italy",
    "Poland",
    "Ukraine",
]
included_rows = df["Country/Region"].isin(included_countries)
df = df[included_rows]

# Combine all rows for each country into one
agg = {}
for date in df.columns[1:]:
    agg[date] = "sum"
df = df.groupby(df["Country/Region"]).aggregate(agg)

# Give each column optimal type
df = df.convert_dtypes()

# Print out dataset
st.dataframe(df)

st.text(" ")
st.text(" ")

# Begin showing data
st.subheader("Data Analytics of {} Cases:".format(set))

# Print out a summary of dataset
st.write(df.describe())

# Create variables of important date column names for use later
last_date = df.columns[df.shape[1] - 1]
second_last_date = df.columns[df.shape[1] - 2]
first_date = df.columns[0]
second_date = df.columns[1]
first_jan = datetime.date(2021, 1, 1)

# Add in a total column for a neater name
total = df[last_date]
df["Total"] = total

st.text(" ")
st.text(" ")

# Graph Total cases
st.subheader("Graphing the Total Number of {} Cases per Country".format(set))
choose_total_plot = st.selectbox(
    "How Would You Like To See Total {} Cases Plotted?".format(set),
    ("Bar Chart", "Scatter Plot"),
)

# Bar Chart
if choose_total_plot == "Bar Chart":
    bar_chart = px.bar(
        df,
        x=df.index,
        y="Total",
        color="Total",
        labels={"Total": "Total Cases"},
        title="Total {} Cases Per Country".format(set),
    ).update_layout(
        xaxis={"categoryorder": "total ascending"}
    )  # order by total cases

    st.plotly_chart(bar_chart)

# Scatter Chart
if choose_total_plot == "Scatter Plot":
    scatter_chart = (
        px.scatter(
            df,
            x=first_jan,
            y="Total",
            color=df.index,
            labels=dict(Total="Total Cases (2020-12-22)"),
            title="Total {} Cases Per Country Relative to January 1st, 2021".format(
                set
            ),
        )
        .update_traces(marker=dict(size=13))
        .update_xaxes(title_text="Total Cases (2021-1-1)")
    )  # make markers bigger and relabel x-axis

    st.plotly_chart(scatter_chart)

st.text(" ")
st.text(" ")

# Graph Total cases - relative
st.subheader(
    "Graphing the Total Number of {} Cases in 10 Worst European Countries Relative to Each Other".format(
        set
    )
)

# Pie Chart
pie_chart = px.pie(
    df,
    values="Total",
    names=df.index,
    labels={"Total": "Total Cases"},
    title="Breakdown of Total {} Cases in 10 Worst European Countries".format(set),
)

st.plotly_chart(pie_chart)

st.text(" ")
st.text(" ")

# Graph Cases Over Time
st.subheader("Graphing the Number of {} Cases Over Time".format(set))
choose_time_plot = st.selectbox(
    "How Would You Like To See {} Cases Plotted Over Time?".format(set),
    ("Line Graph", "Stacked Density Chart"),
)

# Want to make wide df long (so I can utilise dates and relevant no. of
# cases as axes)
df_t = df.T
df_stacked = df_t.stack().reset_index()
df_long = df_stacked.rename(columns={"level_0": "Date", 0: "Cases"})
df_long = df_long.convert_dtypes()

countries = st.multiselect(
    "What Countries Do You Want to See?",
    (
        "All",
        "Ireland",
        "United Kingdom",
        "Russia",
        "Turkey",
        "France",
        "Germany",
        "Spain",
        "Italy",
        "Poland",
        "Ukraine",
    ),
)

if "All" in countries:
    plot_df = df_long  # include all countries
else:
    # subset to their choice
    plot_df = df_long[df_long["Country/Region"].isin(countries)]

# Density chart
if choose_time_plot == "Stacked Density Chart":
    density_chart = px.area(
        plot_df,
        x="Date",
        y="Cases",
        color="Country/Region",
        title="Number of {} Cases Per Country by Date".format(set),
    )

    st.plotly_chart(density_chart)

# Line graph
if choose_time_plot == "Line Graph":
    line_chart = px.line(
        plot_df,
        x="Date",
        y="Cases",
        color="Country/Region",
        title="Number of {} Cases Per Country by Date".format(set),
    )

    st.plotly_chart(line_chart)

st.text(" ")
st.text(" ")

# Comparative Bar Chart
st.subheader("Graphing the Total Number of {} Cases by Date".format(set))

date1 = st.date_input(
    "Please Choose a Start Date:",
    value=first_date,
    min_value=first_date,
    max_value=second_last_date,
)

date2 = st.date_input(
    "Please Choose an End Date:",
    value=last_date,
    min_value=second_date,
    max_value=last_date,
)

df_dates = df_long.loc[df_long["Date"].isin([date1, date2])]
stacked_bar = px.bar(
    df_dates,
    x="Country/Region",
    y="Cases",
    color="Date",
    title="Comparison of Total {} Cases on {} and {}".format(set, date1, date2),
    barmode="group",
).update_layout(
    xaxis={"categoryorder": "total ascending"}
)  # order axis by total cases

st.plotly_chart(stacked_bar)
