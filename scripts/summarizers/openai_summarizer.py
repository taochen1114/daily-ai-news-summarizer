"""
使用OpenAI API生成內容摘要
"""
import os
import json
import datetime
from openai import OpenAI

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, DATA_DIR


class OpenAISummarizer:
    """使用OpenAI API生成內容摘要"""
    
    def __init__(self, model="gpt-3.5-turbo", temperature=0.3):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.temperature = temperature
    
    def summarize_article(self, article):
        """對單篇文章進行摘要"""
        content_type = article.get("content_type", "news")
        
        if content_type == "academic":
            return self._summarize_academic(article)
        else:
            return self._summarize_news(article)
    
    def _summarize_academic(self, article):
        """摘要學術論文"""
        title = article.get("title", "")
        content = article.get("content", "")
        authors = article.get("authors", "")
        
        prompt = f"""
請對以下AI領域學術論文進行口語化摘要：

標題: {title}
作者: {authors}
摘要: {content}

要求：
1. 簡潔總結這篇論文的核心創新點和價值
2. 使用口語化、通俗易懂的表達方式，適合收聽
3. 避免使用過於專業的術語，如需使用專業術語，請簡明解釋
4. 總字數控制在100-200字之間
5. 必須使用台灣繁體中文及台灣用語習慣來表達

摘要:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位專業的AI研究摘要員，負責將學術論文轉化為通俗易懂的口語內容。請使用台灣繁體中文及台灣用語習慣來輸出。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            return {"summary": summary, "model": self.model}
            
        except Exception as e:
            print(f"摘要生成失敗: {e}")
            return {"summary": "", "error": str(e)}
    
    def _summarize_news(self, article):
        """摘要新聞文章"""
        title = article.get("title", "")
        content = article.get("content", "")
        
        # 如果內容過長，截取前3000個字元
        if len(content) > 3000:
            content = content[:3000] + "..."
        
        prompt = f"""
請對以下AI領域新聞進行口語化摘要：

標題: {title}
內容: {content}

要求：
1. 用1-2句話簡潔總結這篇新聞的核心內容和價值
2. 使用口語化、通俗易懂的表達方式，適合收聽
3. 避免使用過於專業的術語，如需使用專業術語，請簡明解釋
4. 總字數控制在100-150字之間
5. 必須使用台灣繁體中文及台灣用語習慣來表達

摘要:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位專業的AI新聞摘要員，負責將AI領域新聞轉化為通俗易懂的口語內容。請使用台灣繁體中文及台灣用語習慣來輸出。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            return {"summary": summary, "model": self.model}
            
        except Exception as e:
            print(f"摘要生成失敗: {e}")
            return {"summary": "", "error": str(e)}
    
    def batch_summarize(self, source_name, date=None):
        """批次處理指定日期的文章"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        source_dir = os.path.join(DATA_DIR, source_name.lower().replace(" ", "_"))
        file_path = os.path.join(source_dir, f"{date}.json")
        
        if not os.path.exists(file_path):
            print(f"找不到檔案: {file_path}")
            return []
            
        # 載入文章
        with open(file_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
            
        updated_articles = []
        
        for article in articles:
            # 檢查是否已處理
            if article.get("processed") and "summary" in article:
                updated_articles.append(article)
                continue
                
            try:
                # 生成摘要
                summary_result = self.summarize_article(article)
                
                # 更新文章
                article["summary"] = summary_result.get("summary", "")
                article["summary_model"] = summary_result.get("model", self.model)
                article["processed"] = True
                article["processed_date"] = datetime.datetime.now().isoformat()
                
                if "error" in summary_result:
                    article["error"] = summary_result["error"]
                
                updated_articles.append(article)
                print(f"已處理: {article['title']}")
                
            except Exception as e:
                print(f"處理文章時出錯: {e}")
                article["error"] = str(e)
                updated_articles.append(article)
        
        # 儲存更新後的文章
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_articles, f, ensure_ascii=False, indent=2)
            
        return updated_articles 