import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(
    page_title="Visualisasi Data Produksi Perkebunan 2023",
    page_icon="🌱",
    layout="wide"
)

# Function to load and preprocess data
@st.cache_data
def load_data():
    # Baca file dengan skiprows untuk melewati baris header yang tidak diperlukan
    df = pd.read_csv("Produksi Tanaman Perkebunan, 2023.csv", skiprows=3)
    
    # Rename columns
    df.columns = ['Provinsi', 'Kelapa_Sawit', 'Kelapa', 'Karet', 'Kopi', 'Kakao', 'Tebu', 'Teh', 'Tembakau']
    
    # Hapus baris yang semua kolomnya NaN
    df = df.dropna(how='all')
    
    # Reset index setelah menghapus baris
    df = df.reset_index(drop=True)
    
    # Konversi kolom numerik
    numeric_columns = df.columns.difference(['Provinsi'])
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Separate Indonesia data
    indonesia_data = df[df['Provinsi'] == 'INDONESIA'].iloc[0]
    df = df[df['Provinsi'] != 'INDONESIA'].copy()
    
    return df, indonesia_data

# Main function
def main():
    # Title
    st.title("📊 Visualisasi Data Produksi Tanaman Perkebunan 2023")
    st.markdown("---")

    # Load data
    try:
        df, indonesia_data = load_data()
        
        # Pilihan Komoditas di bagian atas
        komoditas_list = ['Kelapa_Sawit', 'Kelapa', 'Karet', 'Kopi', 'Kakao', 'Tebu', 'Teh', 'Tembakau']
        selected_komoditas = st.selectbox(
            "Pilih Komoditas untuk Visualisasi:",
            options=komoditas_list,
            format_func=lambda x: x.replace('_', ' ')
        )
        
        st.markdown("---")

        if selected_komoditas:
            # Layout dengan columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Grafik Produksi per Provinsi")
                # Sort data berdasarkan nilai produksi
                df_sorted = df.sort_values(by=selected_komoditas, ascending=True)
                
                fig_bar = px.bar(
                    df_sorted,
                    x=selected_komoditas,
                    y='Provinsi',
                    orientation='h',
                    title=f'Produksi {selected_komoditas.replace("_", " ")} per Provinsi'
                )
                fig_bar.update_layout(height=800)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.subheader("🥧 Pie Chart Distribusi Produksi")
                # Filter data untuk menampilkan hanya provinsi dengan kontribusi signifikan
                threshold = df[selected_komoditas].sum() * 0.01  # 1% threshold
                df_pie = df.copy()
                df_pie.loc[df_pie[selected_komoditas] < threshold, 'Provinsi'] = 'Lainnya'
                df_pie = df_pie.groupby('Provinsi')[selected_komoditas].sum().reset_index()
                
                fig_pie = px.pie(
                    df_pie,
                    values=selected_komoditas,
                    names='Provinsi',
                    title=f'Distribusi Produksi {selected_komoditas.replace("_", " ")}',
                )
                # Konfigurasi tampilan pie chart
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hole=0.3,
                    pull=[0.1 if x == df_pie[selected_komoditas].max() else 0 for x in df_pie[selected_komoditas]]
                )
                fig_pie.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="right",
                        x=1.1
                    ),
                    height=800
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # Informasi Total Produksi Indonesia
            st.markdown("---")
            st.subheader("📊 Total Produksi Indonesia")
            total_indonesia = float(indonesia_data[selected_komoditas])  # Convert to float
            
            # Format angka dengan pemisah ribuan
            formatted_total = "{:,.2f}".format(total_indonesia)
            
            # Tampilkan dengan style
            st.markdown(
                f"""
                <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <h3 style='text-align: center; color: #1f77b4;'>
                        Total Produksi {selected_komoditas.replace("_", " ")}
                    </h3>
                    <h2 style='text-align: center; color: #1f77b4;'>
                        {formatted_total} Ribu Ton
                    </h2>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Raw Data (excluding Indonesia)
            st.markdown("---")
            st.subheader("📝 Data per Provinsi")
            display_df = df[['Provinsi', selected_komoditas]].copy()
            display_df[selected_komoditas] = display_df[selected_komoditas].round(2)
            st.dataframe(
                display_df.sort_values(
                    by=selected_komoditas, 
                    ascending=False
                )
            )

    except Exception as e:
        st.error(f"Terjadi kesalahan dalam memproses data: {str(e)}")
        st.error("Stack trace:", stack_info=True)

if __name__ == "__main__":
    main()