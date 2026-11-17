# RAG 架構與流程

## 先分成兩個階段

初學者可以把 RAG 看成「先準備知識，再用知識回答」：

- **離線索引階段**：整理文件、切分內容、建立 embedding，並存入 vector database。
- **線上查詢階段**：接收 query、檢索 context、把 context 加入 prompt，再由 LLM 生成回答。

AWS 將建立索引描述為前期活動，將後三步描述為每次查詢時重複的流程。[S02，原文位置：主標題下的四個編號步驟](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## 四步驟流程

1. **建立文件索引**：文件經過清理、格式化與 chunking；embedding model 把內容轉成數值表示，再存入 vector database。
2. **提出 Query**：使用者以自然語言提出問題。
3. **檢索與補充 Context**：orchestrator 執行相似度搜尋，retriever 取得相關資料，再把資料作為 context 加到包含 query 的 prompt。
4. **Generation**：orchestrator 把 query 與 context 送給 LLM，由模型利用額外 context 產生回答。[S02，原文位置：主標題下的四個編號步驟](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

```text
文件 → 清理／格式化／切分 → Embedding → Vector Database
                                            ↑
使用者 Query → Retriever／相似度搜尋 → Context → Prompt → LLM → 回答
                         ↑
              Orchestrator 管理整體流程
```

這張文字圖是依 AWS 四步驟製作的教學整理，不是 AWS 原圖的複製。

## Production-level RAG 的主要元件

| 元件 | 初學者解釋 |
|---|---|
| Connectors | 把不同資料來源連接到索引流程。 |
| Data processing | 從 PDF、掃描影像、文件或簡報中擷取並準備內容。 |
| Embeddings | 把文件與 query 轉成可用於相關性搜尋的數值表示。 |
| Vector database | 保存 embedding、原文與 metadata，支援搜尋與檢索。 |
| Retriever | 根據 query 找出並排序相關 context。 |
| Foundation model | 通常是 LLM，利用 prompt 與 context 產生回答。 |
| Guardrails | 對 query、prompt、context 與 response 的準確性、責任性、倫理及偏誤風險進行控制。 |
| Orchestrator | 排程並管理端到端工作流程。 |
| User experience | 提供對話、歷史紀錄或回饋等互動能力。 |
| Identity and user management | 控制誰能存取哪些資料與功能。 |

這是 production-level 系統需要思考的能力清單，不表示每個入門範例都必須一次實作全部元件。[S02，原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## Orchestrator 與 Guardrails

- **Orchestrator** 像流程協調者，負責安排檢索、組合 prompt，以及把資料交給模型等步驟。
- **Guardrails** 是風險控制設計，用來約束流程各階段的準確性、責任性、倫理與偏誤問題；它們不等於能保證每個回答都正確。[S02，原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## 簡單範例

假設公司要建立內部政策問答系統。離線階段先處理政策文件並建立向量索引；員工提問後，retriever 找出相關段落，orchestrator 把段落加入 prompt，LLM 再整理成回答。這是架構示意，並不代表特定產品實作。

## 通用原理與 AWS 服務的界線

四步驟、retriever、vector database、orchestrator 與 guardrails 是文件提出的概念性 RAG 架構。AWS Identity and Access Management（IAM）、Amazon Bedrock 與 Amazon Q Business 是 AWS 環境中的權限或受管服務例子，不是所有 RAG 系統的必要元件。[S02，原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## 相關 Wiki

- [RAG 基本概念](01-introduction.md)
- [文件切分](03-chunking.md)
- [向量嵌入](04-embedding.md)
- [資訊檢索](05-retrieval.md)
- [優勢、限制與品質檢查](06-evaluation.md)

## 來源

- **S02** — AWS Prescriptive Guidance, [Understanding Retrieval Augmented Generation](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)，擷取日期：2026-11-16。

## S06 補充：進階 RAG 工作流程

較複雜的 RAG 可以把工作拆成「檢索證據、分析各份證據、綜合答案」三類任務；也可先建立待辦搜尋項目，或把大型檢索結果暫存後交給不同分析單元，再由主流程整合。這些是進階設計，不是入門 RAG 的必要步驟。[S06，原文章節：RAG patterns；What you will build](https://docs.langchain.com/oss/python/deepagents/rag#rag-patterns)

LangChain 教學以 Index、Search、Analyze、Synthesize 描述範例：先建立索引，查詢時檢索 chunk，再分析與綜合。Deep Agents、filesystem backend、skills 與 subagents 是 LangChain 特定實作，不應泛化成所有 RAG 都必備。[S06，原文章節：What you will build](https://docs.langchain.com/oss/python/deepagents/rag#what-you-will-build)

### 來源補充
- **S06** — LangChain, [Retrieval Augmented Generation (RAG) with Deep Agents](https://docs.langchain.com/oss/python/deepagents/rag)，擷取日期：2026-11-16。
