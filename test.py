from Dboperation import ArticleDB

db=  ArticleDB("207.148.127.78","haawjkxnuy","QbeufDdc59","haawjkxnuy")

# 新增
new_id = db.add_article(
    source="Reuters",
    url="https://example.com",
    title="Market News",
    content="Today the market went up..."
)
print("Inserted ID:", new_id)

# 查询
item = db.get_article_by_id(new_id)
print("Fetched:", item)

# 更新
db.update_article(new_id, title="Updated Title")

# 删除
# db.delete_article(new_id)

db.close()
