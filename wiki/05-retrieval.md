# 資訊檢索

## 檢索在 RAG 中做什麼？

RAG 必須先從外部資料找出與使用者問題相關的內容，再把內容交給 LLM。Google Cloud 的說明列舉網頁、知識庫與資料庫作為外部資料來源，也強調檢索內容的相關性會直接影響生成結果。[S01，原文章節：How does Retrieval-Augmented Generation work?；Relevance, accuracy, and quality](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 核心概念

### 向量搜尋

現代搜尋系統可以把文件表示為高維度向量，並依語意相似度尋找與查詢接近的內容。這使系統不必只依賴完全相同的關鍵字。[S01，原文章節：Search with vector databases and relevancy re-rankers](https://cloud.google.com/use-cases/retrieval-augmented-generation)

### Hybrid Search

進階搜尋系統可能同時使用關鍵字搜尋與語意搜尋，這種組合稱為 hybrid search。兩種方法可以提供不同的比對線索；但 hybrid search 是可選的進階做法，不是每個 RAG 系統都必然使用。[S01，原文章節：Search with vector databases and relevancy re-rankers](https://cloud.google.com/use-cases/retrieval-augmented-generation)

### Reranking

搜尋系統取得一批候選內容後，可以再由重新排序機制評分，讓較相關的結果排在前面。Google Cloud 以自家進階搜尋服務說明這種做法，因此此處只把 reranking 視為可能採用的檢索技術，不視為所有 RAG 的標準配備。[S01，原文章節：Search with vector databases and relevancy re-rankers](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 簡單範例

使用者搜尋「員工遠端工作的休假規則」時，關鍵字搜尋可以找出含有相同詞彙的段落；語意搜尋也可能找到使用「在家辦公」或「假勤政策」等不同用語但意思相關的內容。系統若採用 reranking，還可把最符合問題的候選段落排到前面。這是概念示意，不代表所有 RAG 實作都採用相同組合。

## 為什麼相關性重要？

模型可能忠實使用檢索結果，但如果結果與問題無關，回答仍會離題，甚至錯誤。因此，「有引用到檢索內容」和「檢索內容真的能回答問題」是兩項不同的檢查。[S01，原文章節：Relevance, accuracy, and quality](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 相關 Wiki

- [RAG 基本概念](01-introduction.md)
- [優勢、限制與品質檢查](06-evaluation.md)

## 來源

- **S01** — Google Cloud, [What is Retrieval-Augmented Generation (RAG)?](https://cloud.google.com/use-cases/retrieval-augmented-generation)，擷取日期：2026-11-16。

## S04 補充：Embedding 與檢索

語意搜尋會把 query 與候選文件表示成向量，再依距離或相似度排列結果。Embedding 提供的是可比較的表示；它本身不等於完整的 retriever，也不保證最前面的結果一定能回答問題。[S04，原文章節：What are embeddings?；Use cases](https://developers.openai.com/api/docs/guides/embeddings#use-cases)

### 來源補充

- **S04** — OpenAI, [Vector embeddings](https://developers.openai.com/api/docs/guides/embeddings)，擷取日期：2026-11-16。

## S05 補充：Hybrid Search 與檢索限制

Hybrid Search 會同時使用關鍵字搜尋與向量搜尋，再合併兩類候選結果。關鍵字保留精確字面線索，向量搜尋補充語意相近但用詞不同的內容；兩者結合可改善 recall，但仍需要檢查結果是否真的回答問題。[S05，原文章節：Solving query understanding challenges；Maximize relevance and recall](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview#maximize-relevance-and-recall)

Semantic ranking 可以依語意重新評估候選結果。它是可能的相關性改善步驟，不是所有 RAG 系統的必要元件。[S05，原文章節：Solving query understanding challenges](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview#solving-query-understanding-challenges)

### 來源補充
- **S05** — Microsoft Learn, [Retrieval-augmented generation (RAG) in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)，更新日期：2026-08-04；擷取日期：2026-11-16。
