import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style for seaborn
sns.set(style='dark')

# Load dataframe
day_df = pd.read_csv("day.csv")

# pastikan kolom dteday bertipe datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Ubah nilai season menjadi nama musim
day_df['season'] = day_df['season'].replace({
    1:'Springer',
    2:'Summer',
    3:'Fall',
    4:'Winter'
})

# Ubah nilai mnth menjadi nama bulan
day_df['mnth'] = day_df['mnth'].replace({
    1:'Januari', 2:'Februari', 3:'Maret', 4:'April',
    5:'Mei', 6:'Juni', 7:'Juli', 8:'Agustus',
    9:'September', 10:'Oktober', 11:'November', 12:'Desember'
})

# Fungsi berdasarkan musim
def create_day_df(df):
    season_summary = df.groupby('season').agg({
        'cnt' : 'sum',
        'casual' : 'sum',
        'registered' : 'sum'
    }).sort_values(by='cnt', ascending=False).reset_index()

    return season_summary

# Fungsi untuk menampilkan season dengan penggunaan tertinggi
def create_top_season(season_summary):
    top_season = season_summary['cnt'].idxmax()

    top_season_details = {
        'season' : season_summary.loc[top_season, 'season'],
        'cnt' : season_summary.loc[top_season,  'cnt'],
        'casual' : season_summary.loc[top_season, 'casual'],
        'registered' : season_summary.loc[top_season, 'registered']
    }

    return top_season_details

# Fungsi pengelompokkan data berdasarkan bulan
def create_mnth_summary(df):
    mnth_summary = df.groupby('mnth').agg({
    'cnt' : 'sum',
    'casual' : 'sum',
    'registered' : 'sum',
    'weathersit' : 'mean',
    'temp' : 'mean',
    'hum' : 'mean',
    'windspeed' : 'mean'
    }).sort_values(by='cnt', ascending=False)

    return mnth_summary

def create_top_month_details(mnth_summary):
    ## Bagian top month
    top_month = mnth_summary['cnt'].idxmax() # Bulan dengan nilai tertinggi
    top_month_details = {
        'month': top_month,
        'cnt' : mnth_summary.loc[top_month, 'cnt'],
        'casual' : mnth_summary.loc[top_month, 'casual'],
        'registered' : mnth_summary.loc[top_month, 'registered']
    }

    # Statistik rata-rata untuk top_month
    top_month_stats = {
        'month' : top_month,
        'weathersit' : mnth_summary.loc[top_month, 'weathersit'],
        'temp' : mnth_summary.loc[top_month, 'temp'] * 47,
        'hum' : mnth_summary.loc[top_month, 'hum'],
        'windspeed' : mnth_summary.loc[top_month, 'windspeed']
    }

    return top_month_details, top_month_stats


# Membuat komponen filter dashboard
with st.sidebar:
    st.image("logo.png") # Menambahkan logo
    
# Pemanggilan fungsi
season_summary = create_day_df(day_df)
top_season_details = create_top_season(season_summary)
mnth_summary = create_mnth_summary(day_df)
top_month_details, top_month_stats = create_top_month_details(mnth_summary)

# Header dashboard
st.title('Dashboard Bike Sharing')

st.write('Jumlah penggunaan sepeda')
col1, col2 = st.columns(2)
with col1:
    total_cnt = season_summary['cnt'].sum()
    st.metric("Total Pengguna", value=total_cnt)

with col2:
    total_casual = season_summary['casual'].sum()
    total_reg = season_summary['registered'].sum()
    st.metric("Tidak Registrasi", value=total_casual)
    st.metric("Sudah Registrasi", value=total_reg)

###
# Penggunaan sepeda berdasarkan musim
st.subheader('Penggunaan Sepeda Harian Berdasarkan Musim')
st.table(season_summary.set_index('season'))

col1, col2 = st.columns(2)
with col1:
    st.metric("Season dengan penggunaan terbanyak adalah: ", top_season_details['season'])
    st.metric("Jumlah Pengguna: ", top_season_details['cnt'])

with col2:
    st.metric("Pengguna Tidak Registrasi", top_season_details['casual'])
    st.metric("Pengguna Sudah Registrasi", top_season_details['registered'])

# Visualisasi penggunaan sepeda per musim
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
plt.figure(figsize=(10,5))

sns.barplot(
    x="season",
    y="cnt",
    data=season_summary,
    palette=colors_
)

plt.title("Penggunaan Sepeda per Musim")
plt.xlabel("Season")
plt.ylabel('Total Penggunaan Sepeda')
st.pyplot(plt)

### Bagian penggunaan sepeda berdasarkan bulan
st.subheader('Penggunaan Sepeda Harian Berdasarkan Bulan')
st.table(mnth_summary)

col1, col2 = st.columns(2)
with col1:
    st.metric("Bulan dengan penggunaan terbanyak adalah: ", top_month_details['month'])
    st.metric("Jumlah Pengguna: ", top_month_details['cnt'])

with col2:
    st.metric("Pengguna Tidak Registrasi", top_month_details['casual'])
    st.metric("Pengguna Sudah Registrasi", top_month_details['registered'])

# Data bulan Agustus
august_data = day_df[day_df['mnth'] == top_month_details['month']]
august_summary = august_data.agg({
    'weathersit' : ['mean', 'max', 'min'],
    'temp' : ['mean', 'max', 'min'],
    'hum' : ['mean', 'max', 'min'],
    'windspeed' : ['mean', 'max', 'min']
})
# Tampilkan tabel bulan Agustus
st.subheader('Data kondisi di bulan Agustus')
st.table(august_summary)

# Create subplots
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Plot weather situation
sns.histplot(august_data['weathersit'], kde=True, ax=ax[0])
ax[0].set_title('Weather Situation in August')
ax[0].set_xlabel('Weather Situation')
ax[0].set_ylabel('Frequency')

# Plot temperature
sns.histplot(august_data['temp'], kde=True, ax=ax[1])
ax[1].set_title('Temperature Distribution in August')
ax[1].set_xlabel('Normalized Temperature')
ax[1].set_ylabel('Frequency')

fig2, ax2 = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Plot humidity
sns.histplot(august_data['hum'], kde=True, ax=ax2[0])
ax2[0].set_title('Humidity Distribution in August')
ax2[0].set_xlabel('Normalized Humidity')
ax2[0].set_ylabel('Frequency')

# Plot wind speed
sns.histplot(august_data['windspeed'], kde=True, ax=ax2[1])
ax2[1].set_title('Wind Speed Distribution in August')
ax2[1].set_xlabel('Normalized Wind Speed')
ax2[1].set_ylabel('Frequency')

plt.tight_layout()

# Display the plot in Streamlit
st.pyplot(fig)
st.pyplot(fig2)

# Tampilkan suhu rata-rata per bulan
st.subheader ("Kondisi pada Bulan Januari - Desember")
# ubah data
month_condition = day_df.melt(id_vars=['mnth'], value_vars=['weathersit', 'temp', 'hum', 'windspeed'], var_name='Variable', value_name='Value')

# Membuat grafik weathersit per bulan
plt.figure(figsize=(12, 6))
sns.lineplot(x='mnth', y='Value', hue='Variable', data=month_condition, markers='o')

# Menambahkan judul dan label
plt.title('Distribusi Weather, Temperature, Humidity, and Windspeed Situation per Bulan')
plt.xlabel('Bulan')
plt.ylabel('Situation')
plt.xticks(rotation=45)  # Memutar label bulan agar lebih mudah dibaca

# Menampilkan grafik di Streamlit
st.pyplot(plt)
