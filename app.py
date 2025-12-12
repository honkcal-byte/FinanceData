from flask import Flask, render_template, redirect, url_for
from Dboperation import ArticleDB

app = Flask(__name__)

# 初始化数据库连接
# db = ArticleDB(
#     host="127.0.0.1",
#     user="your_user",
#     password="your_pass",
#     database="your_database",
#     port=3306
# )

db=  ArticleDB("207.148.127.78","haawjkxnuy","QbeufDdc59","haawjkxnuy")


# -------------------------
# 首页：展示数据库里的所有数据
# -------------------------
@app.route("/")
def index():
    articles = db.get_articles(limit=200)
    return render_template("index.html", articles=articles)


# -------------------------
# 点击处理单条数据
# -------------------------
@app.route("/process/<int:article_id>")
def process_item(article_id):
    """
    这里写你对这个数据的后续逻辑：
    比如：标记处理、更新字段、抓取全文、再次分析、推到AI处理等
    """
    db.update_article(article_id, content="【已处理】" )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
