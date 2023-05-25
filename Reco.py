from sklearn.decomposition import TruncatedSVD
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
import warnings
import matplotlib.pyplot as plt
import time
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
from streamlit_star_rating import st_star_rating
import os
import datetime


st.set_page_config(
    page_title="Recommandation",
    page_icon="👋",
)

st.title('Recommandation de films')

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Affichage de l'animation Lottie
lottie_animation = "https://assets3.lottiefiles.com/packages/lf20_cUG5w8.json"
lottie_animate_json = load_lottieurl(lottie_animation)

st_lottie(lottie_animate_json, key="CineHackers")

def load_data():
    # Chargement des données à partir d'un fichier CSV
    df = pd.read_csv('https://raw.githubusercontent.com/VictoriaGaullier/reco-sigmoide/main/df%20(3).csv')
    return df

def preprocess_data(df):
    # Concaténation des colonnes en une seule chaîne de caractères
    df['concatenated'] = (df['rated']).astype(str) + ' ' + df['genre_1'] + ' ' + df['actor_1'] + ' ' + df['plot']
    return df

@st.cache_data
def calculate_similarity_matrix(df):
    tfv = TfidfVectorizer(min_df=3, max_features=None, strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}', ngram_range=(1, 3), stop_words=[" ", ".", ",", 'and', 'the', 'a', 'an', 'in', 'of', 'to', 'is', 'it', 'that', "A", "An", 'The', 'Of'])
    tfv_matrix = tfv.fit_transform((8 * df['genre_1']) +df['genre_2']+df['genre_3'])
    sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
    return sig

def give_rec(title, sig, indices, df):
    df = df[df['title'] != title]
    if title not in indices:
        return pd.Series()
    idx = indices[title]
    sig_scores = list(enumerate(sig[idx]))
    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
    sig_scores = sig_scores[1:6]
    movies_indices = [i[0] for i in sig_scores]
    return df['title'].iloc[movies_indices]

def main():
    df = load_data()
    df = preprocess_data(df)
    sig = calculate_similarity_matrix(df)
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()

    st.subheader("Quels films avez-vous aimés ?")
    selected_films = st.selectbox(' ', options=['Choisissez un film'] + df['title'].tolist(), key='movie_input', format_func=lambda x: x)
    
    if selected_films:
        film = selected_films
    else:
        film = None

        
    rec_movies = give_rec(film, sig, indices, df)
    
    if not rec_movies.empty:
        st.write('Films recommandés :')
        num_cols = 5
        num_rows = -(-len(rec_movies) // num_cols)  # Ceil division for number of rows
        
        # Calculer la largeur et l'écart entre les images
        image_width = 100
        spacing = 200
        col_width = image_width + spacing
        
        cols = st.columns(num_cols)
        
        for i, movie in enumerate(rec_movies):
            col_index = i % num_cols
            row_index = i // num_cols
            
            with cols[col_index]:
                movie_poster = df.loc[df['title'] == movie, 'poster'].iloc[0]
                movie_title = df.loc[df['title'] == movie, 'title'].iloc[0]
                movie_rated = df.loc[df['title'] == movie, 'rated'].iloc[0]
                movie_rating = df.loc[df['title'] == movie, 'averageRating'].iloc[0]
                movie_year = pd.to_datetime(df.loc[df['title'] == movie, 'startYear'], format='%Y').dt.year.iloc[0]
                # Créer le lien IMDb avec le titleId correspondant
                imdb_link = f"https://www.imdb.com/title/{df.loc[df['title'] == movie, 'titleId'].iloc[0]}/"
                
                # Écarter les images en ajoutant des colonnes vides
                col_space = col_width - image_width
                st.write("")  # Colonne vide
                st.image(movie_poster, width=image_width, use_column_width=False)
                st.write("")  # Colonne vide
                
                # Afficher le titre
                st.markdown(f"**Titre:** {movie_title}")

                # Aligner l'average note avec le titre
                st.text(" " * len(movie_title))

                # Afficher l'average note sur la même ligne que le titre
                st.write(f"**Note moyenne:** {movie_rating}")
                st.write(" ")
                st.write(f"**Année:** {movie_year}")

                # Aligner le lien IMDb avec le titre
                st.text(" " * len(movie_title))

                # Afficher le lien IMDb sur la même ligne que le titre
                markdown_link = f"[![Cliquez ici pour accéder à IMDb](https://www.imdb.com/favicon.ico)]({imdb_link})"
                st.markdown(markdown_link, unsafe_allow_html=True)

                
                if row_index < num_rows - 1:
                    st.text("")
    else:
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write('Aucun film recommandé.')

if __name__ == '__main__':
    main()

# Évaluation du site
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(" ")
st.write(' ')
st.subheader("Notez votre expérience !")
st.write('Pour améliorer la qualité de notre service et offrir la meilleure expérience possible, nous souhaiterions avoir votre avis. Nous vous remercions par avance de votre participation!')
col1, col2 = st.columns(2)


with col1:
    email = st.text_area('Adresse e-mail')
    stars = st_star_rating("", maxValue=5, defaultValue=3, key="rating")


with col2:
    # Espace pour le commentaire des utilisateurs
    comment = st.text_area("Commentaire")

    # Obtenir le chemin absolu vers le dossier de stockage des commentaires
comment_folder = r"C:\Users\lemai\Desktop\commentaire"

def sauvegarder_commentaire(stars, commentaire, email):
    # Générer un nom de fichier unique basé sur la date et l'heure actuelles
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"commentaire_{timestamp}.txt"

    # Créer le chemin absolu vers le fichier de commentaire
    filepath = os.path.join(comment_folder, filename)

    # Écrire le commentaire et la note dans le fichier
    with open(filepath, "w") as f:
        f.write(f"Note : {stars}\n")
        f.write(f"Commentaire : {commentaire}\n")
        f.write(f"email :{email}")

# Lorsque l'utilisateur clique sur le bouton "Ajouter mon commentaire"
with col2 : 
    if st.button('Ajouter mon commentaire', key='ajouter_commentaire'):
        commentaire_utilisateur = comment
        sauvegarder_commentaire(stars, commentaire_utilisateur, email)
        st.write("Le commentaire a été ajouté avec succès.")
        st.write("Merci de nous aider à améliorer notre site")

        # Effacer le contenu de la colonne col2
        col2.empty()

        # JavaScript pour effacer la valeur de la zone de texte
        st.markdown("<script>document.getElementById('commentaire_input').value=''</script>", unsafe_allow_html=True)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# URL de l'animation Lottie du panda
lottie_url_panda = "https://assets9.lottiefiles.com/packages/lf20_puwecidm.json"
lottie_panda = load_lottieurl(lottie_url_panda)

# Configuration de la sidebar
with st.sidebar:
    # Ajouter un espace vertical pour centrer l'animation Lottie
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")

    
    # Afficher l'animation Lottie du panda
    st_lottie(lottie_panda, width=400, height=400, key="panda", loop=True)

