import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime

class ArticleDB:
    def __init__(self, host, user, password, database, port=3306):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=True,
            connect_timeout=100
        )

    # ---------------------
    # Create (新增)
    # ---------------------
    def add_article(self, source, url, title, content,
                    publish_date=None, craw_date=None):
        sql = """
        INSERT INTO sf_article (source, url, title, content, publish_date, craw_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        publish_date = publish_date or datetime.now()
        craw_date = craw_date or datetime.now()

        with self.conn.cursor() as cursor:
            cursor.execute(sql, (source, url, title, content, publish_date, craw_date))
            return cursor.lastrowid   # 返回自增ID

    # ---------------------
    # Read (查询)
    # ---------------------
    def get_article_by_id(self, article_id):
        sql = "SELECT * FROM sf_article WHERE id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (article_id,))
            return cursor.fetchone()

    def get_articles(self, limit=100):
        sql = "SELECT * FROM sf_article ORDER BY id DESC LIMIT %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (limit,))
            return cursor.fetchall()

    def get_by_source(self, source):
        sql = "SELECT * FROM sf_article WHERE source = %s ORDER BY id DESC"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (source,))
            return cursor.fetchall()

    # ---------------------
    # Update (更新)
    # ---------------------
    def update_article(self, article_id, **fields):
        """
        用法：
        db.update_article(10, title="new title", content="abc")
        """
        if not fields:
            return False

        keys = ", ".join(f"{k} = %s" for k in fields.keys())
        values = list(fields.values())
        values.append(article_id)

        sql = f"UPDATE sf_article SET {keys} WHERE id = %s"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.rowcount > 0

    # ---------------------
    # Delete (删除)
    # ---------------------
    def delete_article(self, article_id):
        sql = "DELETE FROM sf_article WHERE id = %s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (article_id,))
            return cursor.rowcount > 0

    # ---------------------
    # Close
    # ---------------------
    def close(self):
        self.conn.close()
