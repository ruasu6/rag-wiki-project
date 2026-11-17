# 優勢、限制與品質檢查

## RAG 的入門優勢

### 取得較新的資訊

LLM 的預訓練資料有時間範圍，可能無法涵蓋近期資訊。RAG 可以在回答時取得外部內容，補充模型原本沒有的新資料。[S01，原文章節：Access to fresh information](https://cloud.google.com/use-cases/retrieval-augmented-generation)

### 讓回答有資料依據

把相關事實加入模型脈絡，有助於讓模型依據指定資料回答，而不是完全依賴訓練時學到的內容。這種做法稱為 grounding。[S01，原文章節：Factual grounding](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 重要限制

Grounding 不等於保證正確。Google Cloud 指出，如果檢索到的資訊不相關，即使生成內容以那些資訊為依據，回答仍可能離題或錯誤。因此，RAG 的品質不只取決於 LLM，也取決於檢索機制和知識來源。[S01，原文章節：Relevance, accuracy, and quality](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 初學者品質檢查

1. **有找到資料嗎？** 檢查系統是否真的取得外部內容。
2. **資料與問題相關嗎？** 有取回資料不代表資料能回答問題。
3. **回答有依據資料嗎？** 比較回答與取回內容，確認沒有偏離資料。
4. **資料夠新嗎？** 若問題涉及近期狀態，檢查來源日期或更新狀態。
5. **回答真的解決問題嗎？** 即使內容有依據，也要確認沒有離題。[S01，原文章節：Access to fresh information；Factual grounding；Relevance, accuracy, and quality](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 簡單範例

假設問題是「今年的退費期限」，系統卻取回去年的政策。回答可能完全符合取回文件，卻仍不符合使用者需要。品質檢查因此要同時確認來源新舊、檢索相關性與回答是否有依據。這是用來解釋檢查方法的假設案例。

## 產品功能與通用原則的界線

Google Cloud 原頁面另提到自家搜尋、重新排序與模型評估功能。這些是產品或進階系統的實作例子，不代表所有 RAG 系統都自動具備相同功能。本頁只採用「新鮮度、grounding 與相關性」作為通用的入門檢查方向。

## 相關 Wiki

- [RAG 基本概念](01-introduction.md)
- [資訊檢索](05-retrieval.md)

## 來源

- **S01** — Google Cloud, [What is Retrieval-Augmented Generation (RAG)?](https://cloud.google.com/use-cases/retrieval-augmented-generation)，擷取日期：2026-11-16。

## S05 補充：實作限制檢查

RAG 實作常同時面對查詢意圖、多來源資料、token 限制、回應時間及安全治理。初學者檢查品質時，不只要問「找到了嗎」，還要問：結果是否精簡且相關、是否在模型輸入限制內、回應是否及時，以及使用者是否有權讀取該內容。[S05，原文章節：The challenges of RAG](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview#the-challenges-of-rag)

Microsoft 文件指出，好的 grounding data 是適當內容、查詢設計與能找出最佳 chunk 的 query logic 共同作用的結果。因此 hybrid search 或 reranking 只能改善流程，不能單獨保證答案正確。[S05，原文章節：Maximize relevance and recall](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview#maximize-relevance-and-recall)

### 來源補充
- **S05** — Microsoft Learn, [Retrieval-augmented generation (RAG) in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)，更新日期：2026-08-04；擷取日期：2026-11-16。

## S06 補充：以證據規則檢查回答

進階流程可以先檢索證據並產生草稿，再由 grader 依 rubric 檢查回答是否以來源為依據；不通過時修訂，但必須設定 iteration cap，避免無限循環。[S06，原文章節：RAG patterns，Rubric-checked grounding](https://docs.langchain.com/oss/python/deepagents/rag#rag-patterns)

實務上也應保留可觀測紀錄，檢查實際檢索結果、工具呼叫與模型回答。LangSmith 是原文使用的特定追蹤產品；通用原則是讓流程可追查，而不是所有系統都必須採用 LangSmith。[S06，原文章節：Setup](https://docs.langchain.com/oss/python/deepagents/rag#setup)

### 初學者檢查
1. 回答中的重要說法能否指向實際取回的內容？
2. Grader 的規則是否明確，而不是只回報模糊的「看起來正確」？
3. 修訂是否有最多次數，且每次失敗原因都有紀錄？
4. Trace 是否能看出檢索、工具與生成在哪一步出錯？

### 來源補充
- **S06** — LangChain, [Retrieval Augmented Generation (RAG) with Deep Agents](https://docs.langchain.com/oss/python/deepagents/rag)，擷取日期：2026-11-16。
