from flask import Flask, render_template, request
import pandas as pd
import difflib
import importlib
import dashboard  # Custom dashboard functions

# Force reload to ensure the latest changes in dashboard.py
importlib.reload(dashboard)

app = Flask(__name__)

# Load data
df = pd.read_csv('aiCleanedTitle.csv')
df['Clean_title'] = df['Clean_title'].fillna('')  # Moved this after loading the CSV

# Course Recommendation
@app.route("/", methods=['GET', 'POST'])
def index():
    showtitle = False
    showerror = False
    coursemap = {}
    coursename = ""

    if request.method == 'POST':
        coursename = request.form.get("course")
        titlelist = df['Clean_title'].tolist()
        match = difflib.get_close_matches(coursename, titlelist, n=5)

        if match:
            resultdf = df[df['Clean_title'].isin(match)]
            for _, row in resultdf.iterrows():
                coursemap[row['course_title']] = row['url']
            showtitle = True
        else:
            showerror = True

    return render_template("index.html", showtitle=showtitle, showerror=showerror,
                           coursemap=coursemap, coursename=coursename)

# Dashboard route
@app.route("/dashboard")
def dashboard_route():
    valuecounts = dashboard.getvaluecounts(df)
    levelcounts = dashboard.getlevelcount(df)
    subjectsperlevel = dashboard.getsubjectsperlevel(df)

    # Ensure yearwiseprofit() returns all required variables
    profitmap, subscribersmap, profitmonthwise, monthwisesub = dashboard.yearwiseprofit(df)

    return render_template("dashboard.html", valuecounts=valuecounts,
                           levelcounts=levelcounts, subjectsperlevel=subjectsperlevel,
                           yearwiseprofitmap=profitmap, subscriberscountmap=subscribersmap,
                           profitmonthwise=profitmonthwise, monthwisesub=monthwisesub)

if __name__ == '__main__':
    app.run(debug=True)
