
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Fonction utilitaire pour afficher joliment les figures ---
def display_figures_in_columns(figures, cols_per_row=2):
    for i in range(0, len(figures), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, fig in enumerate(figures[i:i+cols_per_row]):
            with cols[j]:
                st.pyplot(fig)

# --- Configuration de la page Streamlit ---
st.set_page_config(layout="wide", page_title="Analyse des Données de Joueuses 📊")
sns.set_theme(style="whitegrid", palette="viridis")

st.title("📊 Analyse des Données de Performance des Joueuses")
st.markdown("Cette application interactive vous permet d'explorer les relations entre les phases du cycle menstruel, la nutrition, les symptômes et les performances sportives de chaque joueuse.")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Jeu_Donnees_Cycle_Performance.xlsx')
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            df = df.sort_values(by=['Joueuse', 'Date']).reset_index(drop=True)
        else:
            st.error("La colonne 'Date' est manquante.")
            st.stop()
        required_columns = ['Joueuse', 'Phase_Cycle', 'Fer_mg', 'Hydratation_L',
                            'Sprints', 'Distance_km', 'Precision_Passes',
                            'Humeur', 'Crampes', 'Fatigue']
        for col in required_columns:
            if col not in df.columns:
                st.error(f"La colonne '{col}' est manquante.")
                st.stop()
        return df
    except FileNotFoundError:
        st.error("Le fichier Excel n'a pas été trouvé.")
        st.stop()
    except Exception as e:
        st.error(f"Erreur : {e}")
        st.stop()

df = load_data()

st.sidebar.header("⚙️ Options de l'Application")
if st.sidebar.checkbox("Afficher les données brutes", False):
    st.subheader("📋 Données Brutes")
    st.dataframe(df)

variables_nutrition = ['Fer_mg', 'Hydratation_L']
variables_performance = ['Sprints','Distance_km','Precision_Passes']
variables_symptomes = ['Humeur', 'Crampes', 'Fatigue']

# Section 1
st.header("1. 🌸 Phases du Cycle par Joueuse")
with st.container(border=True):
    phases_par_joueuse = df.groupby('Joueuse')['Phase_Cycle'].value_counts().unstack(fill_value=0)
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    phases_par_joueuse.plot(kind='bar', stacked=True, ax=ax1, cmap='Paired')
    ax1.set_title('Phases du Cycle pour Chaque Joueuse', fontsize=18, fontweight='bold')
    ax1.set_xlabel('Joueuse', fontsize=14)
    ax1.set_ylabel("Nombre d'Observations", fontsize=14)
    ax1.tick_params(axis='x', rotation=45, labelsize=12)
    ax1.legend(title='Phase du Cycle', title_fontsize='13', fontsize='11', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig1)

# Section 2.1
st.header("2. 💪 Corrélation entre Nutrition et Performance")
st.subheader("2.1. Corrélation Globale")
with st.container(border=True):
    df_correlation = df[variables_nutrition + variables_performance]
    corr_matrix = df_correlation.corr()
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax2, annot_kws={"size": 12})
    ax2.set_title("Corrélation Globale", fontsize=16)
    st.pyplot(fig2)

# Section 2.2
st.subheader("2.2. Corrélation par Phase de Cycle")
with st.expander("Voir les Heatmaps par Phase de Cycle"):
    phase_figures = []
    for phase in df['Phase_Cycle'].unique():
        df_phase = df[df['Phase_Cycle'] == phase]
        if len(df_phase) > 1:
            corr = df_phase[variables_nutrition + variables_performance].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            ax.set_title(f'Corrélation - {phase}')
            phase_figures.append(fig)
    display_figures_in_columns(phase_figures, cols_per_row=2)

# Section 2.3
st.subheader("2.3. Corrélation par Joueuse et Phase de Cycle")
with st.expander("Voir les Heatmaps par Joueuse et Phase"):
    grouped = df.groupby(['Joueuse', 'Phase_Cycle'])
    fig_list = []
    for (joueuse, phase), group in grouped:
        if len(group) > 1:
            corr = group[variables_nutrition + variables_performance].corr()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            ax.set_title(f'{joueuse} - {phase}')
            fig_list.append(fig)
    display_figures_in_columns(fig_list, cols_per_row=3)

# Section 3
st.header("3. 📈 Évolution des Variables par Joueuse")
with st.container(border=True):
    joueuses = sorted(df["Joueuse"].unique())
    variables = variables_nutrition + variables_performance + variables_symptomes
    col1, col2 = st.columns(2)
    with col1:
        selected_joueuse = st.selectbox('Joueuse', joueuses)
    with col2:
        selected_variable = st.selectbox('Variable', variables)
    if selected_joueuse and selected_variable:
        df_j = df[df["Joueuse"] == selected_joueuse].sort_values("Date")
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.lineplot(data=df_j, x="Date", y=selected_variable, hue="Phase_Cycle", marker="o", palette="Set2", ax=ax)
        ax.set_title(f"{selected_variable} - {selected_joueuse}")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

# Section 4.1
st.header("4. 🤕 Impact des Symptômes sur la Performance")
st.subheader("4.1. Corrélation Globale")
with st.container(border=True):
    df_corr = df[variables_symptomes + variables_performance]
    matrix = df_corr.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    ax.set_title("Corrélation Globale - Symptômes/Performance")
    st.pyplot(fig)

# Section 4.2
st.subheader("4.2. Corrélation Symptômes/Performance par Phase")
with st.expander("Voir les Heatmaps par Phase"):
    figs = []
    for phase in df['Phase_Cycle'].unique():
        group = df[df['Phase_Cycle'] == phase]
        if len(group) > 1:
            corr = group[variables_symptomes + variables_performance].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            ax.set_title(f'{phase} - Symptômes/Performance')
            figs.append(fig)
    display_figures_in_columns(figs, cols_per_row=2)

# Section 4.3
st.subheader("4.3. Corrélation Symptômes/Performance par Joueuse et Phase")
with st.expander("Voir les Heatmaps par Joueuse + Phase"):
    figs = []
    for (joueuse, phase), group in df.groupby(['Joueuse', 'Phase_Cycle']):
        if len(group) > 1:
            corr = group[variables_symptomes + variables_performance].corr()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            ax.set_title(f'{joueuse} - {phase}')
            figs.append(fig)
    display_figures_in_columns(figs, cols_per_row=3)

st.markdown("---")
