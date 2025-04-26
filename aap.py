from flask import Flask, request, render_template
import pandas as pd
import neattext.functions as nfx
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dashboard import getvaluecounts, getlevelcount, getsubjectsperlevel, yearwiseprofit

app = Flask(_name_)

# Clean course titles
def getcleantitle(df):
    df['Clean_title'] = df['course_title'].apply(nfx.remove_stopwords)
    df['Clean_title'] = df['Clean_title'].apply(nfx.remove_special_characters)
    return df

# Create CountVectorizer matrix
def getcosinemat(df):
    countvect = CountVectorizer()
    return countvect.fit_transform(df['Clean_title'])

# Calculate cosine similarity
def cosinesimmat(cv_mat):
    return cosine_similarity(cv_mat)

# Load the updated CSV file
def readdata():
    return pd.read_csv('aiCleanedTitle_updated.csv')  # Updated filename

# Recommend courses by exact title match
def recommend_course(df, title, cosine_mat, numrec):
    course_index = pd.Series(df.index, index=df['course_title']).drop_duplicates()
    if title in course_index:
        index = course_index[title]
        scores = list(enumerate(cosine_mat[index]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        selected_course_index = [i[0] for i in sorted_scores[1:numrec+1]]
        selected_course_score = [i[1] for i in sorted_scores[1:numrec+1]]
        rec_df = df.iloc[selected_course_index].copy()
        rec_df['Similarity_Score'] = selected_course_score
        return rec_df[['course_title', 'Similarity_Score', 'url', 'price', 'num_subscribers']]
    else:
        return pd.DataFrame()

# Fallback: search by partial title
def searchterm(term, df):
    result_df = df[df['course_title'].str.contains(term, case=False)]
    return result_df.sort_values(by='num_subscribers', ascending=False).head(6)

# Extract data to display
def extractfeatures(recdf):
    return list(recdf['url']), list(recdf['course_title']), list(recdf['price'])

# Home page route
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        titlename = request.form['course']
        try:
            df = readdata()
            df = getcleantitle(df)
            cvmat = getcosinemat(df)
            cosine_mat = cosinesimmat(cvmat)
            recdf = recommend_course(df, titlename, cosine_mat, 6)
            if not recdf.empty:
                course_url, course_title, course_price = extractfeatures(recdf)
                coursemap = dict(zip(course_title, course_url))
                return render_template('index.html', coursemap=coursemap, coursename=titlename, showtitle=True)
            else:
                raise Exception("Not found in title, falling back to search")
        except:
            df = readdata()
            resultdf = searchterm(titlename, df)
            if not resultdf.empty:
                course_url, course_title, course_price = extractfeatures(resultdf)
                coursemap = dict(zip(course_title, course_url))
                return render_template('index.html', coursemap=coursemap, coursename=titlename, showtitle=True)
            else:
                return render_template('index.html', showerror=True, coursename=titlename)

    return render_template('index.html')

# Dashboard route
@app.route('/dashboard', methods=['GET'])
def dashboard():
    df = readdata()
    valuecounts = getvaluecounts(df)
    levelcounts = getlevelcount(df)
    subjectsperlevel = getsubjectsperlevel(df)
    yearwiseprofitmap, subscriberscountmap, profitmonthwise, monthwisesub = yearwiseprofit(df)
    return render_template('dashboard.html',
                           valuecounts=valuecounts,
                           levelcounts=levelcounts,
                           subjectsperlevel=subjectsperlevel,
                           yearwiseprofitmap=yearwiseprofitmap,
                           subscriberscountmap=subscriberscountmap,
                           profitmonthwise=profitmonthwise,
                           monthwisesub=monthwisesub)

# Run the Flask app
if _name_ == '_main_':
    app.run(debug=True, use_reloader=False, port=5001)  # Avoid port conflict