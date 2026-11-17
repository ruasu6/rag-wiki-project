# S04–S06 Batch Ingestion 摘要

## 結果

| Source | Run ID | 狀態 | Repair | Wiki 更新 |
|---|---|---|---:|---|
| S04 | S04-20261116T182258+0800 | INGESTED | 0 | 04-embedding、05-retrieval |
| S05 | S05-20261116T182434+0800 | INGESTED | 0 | 05-retrieval、06-evaluation |
| S06 | S06-20261116T182542+0800 | INGESTED | 0 | 02-architecture、06-evaluation |

S04 的第一次 stage 檔案建立呼叫因 JavaScript template 中未跳脫的反引號而在工具執行前失敗，沒有建立或修改檔案；修正呼叫格式後成功。這不是 validator、內容、citation 或 metadata Repair。三篇均未發生 VALIDATION_INTERNAL_ERROR 或 COMMIT_TOOL_ERROR。

## 來源與整合重點

- **S04 / OpenAI**：補充 embedding 是浮點數向量、向量距離與語意搜尋；OpenAI 向量正規化及距離函數說明明確保留為產品／模型特性。
- **S05 / Microsoft Learn**：補充 hybrid search、semantic ranking、RAG 的 query、token、延遲及安全限制；Azure agentic retrieval 與相關元件未泛化。
- **S06 / LangChain**：補充檢索／分析／綜合分工、rubric grounding、iteration cap 與 trace；Deep Agents、subagents、filesystem、RubricMiddleware、LangSmith 均標示為 LangChain 實作。

## 全 Wiki 整合驗證

- 六筆來源 registry/raw SHA-256：PASS。
- 六個 Wiki 頁面存在、非空且有章節：PASS。
- Markdown 內部連結：6 檔、18 links、0 broken：PASS。
- S01–S06 均可在各自 raw 筆記與至少一個 Wiki 頁面找到：PASS。
- 主要主張均附 source ID、原文章節與 URL；語意抽查：PASS。
- 產品特定功能界線：PASS。
- Validator self-check：10/10，Exit Code 0。

## 用 Wiki 回答三個初學者問題

### 1. RAG 是什麼，與一般 LLM 有何不同？

RAG 會先從外部來源找出與問題相關的內容，再把內容提供給 LLM 作為回答依據；一般 LLM 主要依賴訓練時學到的資訊。RAG 可補充較新或組織內部資料，但不保證答案必然正確。  
Wiki：[RAG 基本概念](../wiki/01-introduction.md)；來源：S01、S02。

### 2. 為什麼文件要 Chunking，Embedding 又做什麼？

Chunking 把大型或多主題文件切成較小單位，避免超過模型限制並讓檢索更聚焦；Embedding 再把 chunk 轉成可比較的數值向量，使 query 能依語意相似度尋找候選內容。  
Wiki：[文件切分](../wiki/03-chunking.md)、[向量嵌入](../wiki/04-embedding.md)；來源：S02、S03、S04。

### 3. 如何檢查 RAG 回答品質？

先確認知識來源可追溯、檢索內容真的相關且足以回答問題，再檢查回答是否忠於證據、是否超出 token／權限限制。進階流程可用明確 rubric 檢查 grounding、設定修訂上限並保留 trace，但特定 grader 或 tracing 產品不是必要條件。  
Wiki：[資訊檢索](../wiki/05-retrieval.md)、[優勢、限制與品質檢查](../wiki/06-evaluation.md)；來源：S01、S05、S06。

## 尚需人工持續檢查

- 來源網站未來更新後，章節錨點、產品狀態與建議參數可能改變。
- 自動 link/hash 檢查不能取代「引用是否真正支持該句」的語意審查。
- S05 的 agentic retrieval 與 S06 的 Deep Agents 功能演進快速；製作簡報前應再確認產品特定敘述仍符合來源。
