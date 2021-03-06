from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

def get_title_from_index(df,index):
    return df[df.index == index]["title"].values[0]


def get_index_from_title(df,title):
    return df[df.title == title]["index"].values[0]


def combine_features(row):
    try:
        return row['keywords'] + " " + row['cast'] + " " + row["genres"] + " " + row["director"]
    except:
        print("Error:", row)


def calcsim():
    df = pd.read_csv("dataset.csv")

    features = ['keywords', 'cast', 'genres', 'director']

    for feature in features:
        df[feature] = df[feature].fillna('')

    x = df.apply(combine_features, axis=1)

    cv = CountVectorizer()

    count_matrix = cv.fit_transform(x)

    cosine_sim = cosine_similarity(count_matrix)

    return df,cosine_sim



def fuzzy_matching(mapper, fav_movie, verbose=True):

    match_tuple = []

    for i in mapper:
        ratio = fuzz.ratio(i.lower(),fav_movie.lower())
        if ratio>=60:
            match_tuple.append((i,ratio))

    match_tuple = sorted(match_tuple, key=lambda x: x[1])[::-1]
    if not match_tuple:
        return "00"
    if verbose:
        return match_tuple[0][0]


def suggest(movie_user_likes):
    try:
        df.head()
        cosine_sim.shape
    except:
        df,cosine_sim = calcsim()


    movie_user_like = fuzzy_matching(df['title'],movie_user_likes)
    print("movie likes = ",movie_user_like)

    movie_index = get_index_from_title(df,movie_user_like)

    similar_movies = list(enumerate(cosine_sim[movie_index]))

    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)

    movies = []

    i = 0
    for element in sorted_similar_movies:
        # print(get_title_from_index(element[0]))
        movies.append(get_title_from_index(df,element[0]))
        i = i + 1
        if i > 50:
            break

    return movies



app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = [str(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    print(*final_features[0])

    try:
        list = []
        res = suggest(*final_features[0])
        for i in res:
            list.append(i)

        return ("<p>" + "</p><p>".join(list) + "</p>")
    except:
        return "Movie not found"


if __name__ == "__main__":
    app.run(debug=True)
