from flask import Blueprint, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import os

def get_search_title(x: pd.Series):
    x = x.str.lower()
    x = x.str.replace(" ", "")
    return x

### 영화 DB를 가져옴
movieDF = pd.read_csv('./data/processed/tmdb_4796.csv')
movieDF['search_title'] = movieDF[['title']].apply(get_search_title)

### top100 영화들의 인덱스 정보를 가져옴 (flask run 시에만 실행된다.)
top100_indices = np.load('./data/processed/top_100_indices.npy')

### top100 영화들만 필터링하여 저장
top100_moviesDF = movieDF.loc[top100_indices]
top100_moviesDF.reset_index(inplace=True)
top100_moviesDF['Ranking'] = top100_moviesDF.index + 1
top100_moviesDF['year'] = top100_moviesDF['release_date'].str[:4]

### 코사인 유사도 행렬 불러오기
cosine_sim1 = np.load('./data/processed/cosine_similarity1_4796.npy')
cosine_sim2 = np.load('./data/processed/cosine_similarity2_4796.npy')

def get_recommendations(movie_idx, cosine_sim, get_indices=False):
    ### 해당 영화와 모든 영화와의 유사도를 가져온다.
    sim_scores = list(enumerate(cosine_sim[movie_idx]))
    
    ### 유사도에 따라 영화들을 정렬한다.
    sim_scores.sort(key=lambda x: x[1], reverse=True)
    
    ### 가장 유사한 10개의 영화를 추출한다.
    sim_scores = sim_scores[1:11]
    
    ### 가장 유사한 10개 영화의 인덱스를 얻는다.
    movie_indices = [x[0] for x in sim_scores]
    
    if get_indices:
        ### 가장 유사한 10개 영화의 상대 인덱스(iloc)를 반환한다.
        return movie_indices
    else: 
        ### 가장 유사한 10개 영화의 제목, 포스터 링크를 리턴한다.
        return movieDF[['title', 'poster_path']].iloc[movie_indices].values


### __init__.py 의 app에 등록되는 객체
bp = Blueprint(name='RileyFilm', import_name=__name__, template_folder='templates',
               url_prefix='/')

@bp.route('/', methods=['GET', 'POST'])
def homepage():
    # return os.getcwd()    # C:\Users\kdp\PycharmProjects\KDT_13_Personal_Project
    return render_template("homepage.html")

@bp.route('/top100', methods=['GET', 'POST'])
def top100():
    # return f"{top100_indices.tolist()}"
    return render_template('top100.html', 
                           df=top100_moviesDF.to_html(columns=['Ranking', 'title', 'year', 'genres', 'original_language', 'vote_average', 'vote_count'], index=False, justify='center'))

@bp.route('/show_movie_info', methods=['GET', 'POST'])
def show_movie_info():
    if request.method == 'GET':
        ## input 태그의 값을 받아오고, 아무 값도 입력되어 있지 않을 경우 처리
        req_dict = request.args.to_dict()
        input_title = req_dict.get('input_title')
        if input_title == "":
            return "검색 결과 없음"
        
        ## 값이 있을 경우, 해당하는 제목의 영화 검색
        input_title = input_title.lower().replace(" ", "")
        search_indices = movieDF[movieDF['search_title'].str.contains(input_title)].index
        search_num = len(search_indices)
        
        if search_num == 0:
            return "검색 결과 없음"
        elif search_num == 1:
            search_idx = search_indices[0]
        else:
            ## 검색 결과가 여러 가지인 경우, 가장 유명한 영화를 보여준다.
            resultDF = movieDF.loc[search_indices]
            resultDF.sort_values(by='popularity', ascending=False, inplace=True)
            search_idx = resultDF.index[0]
        
        resultSR = movieDF.loc[search_idx]    # Series
        rec1 = get_recommendations(search_idx, cosine_sim1)
        rec2 = get_recommendations(search_idx, cosine_sim2)
        return render_template('show_movie_info.html', movie_info=resultSR.values.tolist(), rec1=rec1.tolist(), rec2=rec2.tolist())
    return "검색한 영화를 표시할 창"