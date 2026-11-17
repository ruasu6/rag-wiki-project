# RAG 基本概念

## RAG 是什麼？

RAG 是「檢索增強生成」（Retrieval-Augmented Generation）的縮寫。它把資訊檢索系統與生成式大型語言模型（LLM）結合：系統先找出與問題相關的外部內容，再把內容交給模型作為回答時的參考依據。[S01，原文章節：What is Retrieval-Augmented Generation (RAG)?](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 和一般 LLM 有什麼不同？

一般 LLM 主要依靠訓練時學到的資訊回答，可能不知道訓練資料之後發生的事情，也不一定掌握某個組織的專門資料。RAG 在回答問題時額外查找外部資料，讓模型能使用較新或更符合當前需求的內容。不過，RAG 只是增加可參考的依據，並不保證答案一定正確。[S01，原文章節：Access to fresh information；Factual grounding](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 核心流程

1. **Retrieval（檢索）**：到網頁、知識庫或資料庫尋找與問題相關的內容。
2. **Pre-processing（前處理）**：整理取回的內容，使它適合交給模型使用。
3. **Grounded generation（依據資料生成）**：把整理後的內容加入模型脈絡，讓模型依據它產生回答。[S01，原文章節：How does Retrieval-Augmented Generation work?](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 簡單範例

假設使用者詢問：「公司今年的請假規定是什麼？」一般 LLM 可能只能根據訓練時學到的通用資訊回答。RAG 系統則可以先查找公司的最新規章，再把相關段落交給模型整理成回答。這是流程示意；實際答案是否可靠，仍取決於取回資料是否正確且相關。

## 核心概念

- **外部知識**：回答時另外取得的網頁、知識庫或資料庫內容。
- **Freshness**：外部來源可以補充模型預訓練資料之後的新資訊。
- **Grounding**：讓回答以取回的內容為依據，而不是只依靠模型參數中的知識。
- **相關性**：如果取回內容不相關，最終回答仍可能離題或錯誤。[S01，原文章節：Relevance, accuracy, and quality](https://cloud.google.com/use-cases/retrieval-augmented-generation)

## 相關 Wiki

- [資訊檢索](05-retrieval.md)
- [優勢、限制與品質檢查](06-evaluation.md)

## 來源

- **S01** — Google Cloud, [What is Retrieval-Augmented Generation (RAG)?](https://cloud.google.com/use-cases/retrieval-augmented-generation)，擷取日期：2026-11-16。

## S02 補充：從生命週期看 RAG

Google Cloud 的三段概念流程著重「檢索、前處理、依據資料生成」；AWS 則把完整生命週期拆成四步：先建立文件向量索引，再由使用者提出 query，接著檢索並把相關內容加入 prompt，最後由 LLM 使用 query 與 context 生成回答。兩種說法沒有矛盾：前者是概念流程，後者把離線索引與每次線上查詢分開說明。[S02，原文位置：主標題下的四個編號步驟](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

### AWS 四步驟摘要

1. 清理、格式化並切分文件，建立 embedding 並存入 vector database。
2. 使用者以自然語言提出 query。
3. 系統檢索相關資料，把它當作 context 加入 prompt。
4. LLM 使用 query 與 context 產生回答。[S02，原文位置：主標題下的四個編號步驟](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

深入的元件關係請見 [RAG 架構與流程](02-architecture.md)。

### S02 來源補充

- **S02** — AWS Prescriptive Guidance, [Understanding Retrieval Augmented Generation](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)，擷取日期：2026-11-16。
