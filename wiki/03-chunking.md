# 文件切分

## Chunking 是什麼？

Chunking 是把較大的文件內容分成較小單位，讓後續模型與檢索系統能分段處理。它通常位於索引準備階段、建立 embedding 之前。這延伸了 S02 的基礎流程：文件先整理與切分，再把各 chunk 轉成 embedding 並存入索引。[S02，原文位置：主標題下四個編號步驟的步驟 1](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

Microsoft Learn 進一步說明，切分可以讓輸入維持在 chat completion 或 embedding model 的限制內，避免內容因截斷而遺失。即使文件沒有超過限制，如果一份文件混合許多子題、難以用單一向量良好表示，較細的切分仍可能更合適。[S03，原文位置：主標題下的導言；Common chunking techniques](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#common-chunking-techniques)

## 在 RAG 索引流程中的位置

```text
原始文件 → 資料處理 → Chunking → Embedding → Vector Database／搜尋索引
```

- **資料處理**：從 PDF、掃描影像、文件或簡報等來源擷取並準備內容。
- **Chunking**：把內容切成後續可處理與檢索的單位。
- **Embedding**：把每個內容單位轉成數值表示。
- **Vector database／搜尋索引**：保存 embedding、文字與 metadata，供搜尋與檢索使用。[S02，原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

大型文件可在 indexing 與 query workflow 中加入 chunking。實際工具可以是函式庫、自訂處理流程或受管服務；工具選擇不改變「先切分、再建立 embedding／索引」這個基本關係。[S03，原文章節：How chunking fits into the workflow](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#how-chunking-fits-into-the-workflow)

## 常見切分策略

| 策略 | 做法 | 適合情境與限制 |
|---|---|---|
| **固定長度切分** | 依固定字數、字元數或 token 數切分，可搭配 overlap。 | 規則簡單、容易重現；但固定邊界可能切開一段完整語意，因此大小仍要足以承載有意義的內容。 |
| **依結構切分** | 依句尾、換行、HTML／Markdown 標題或偵測到的文件結構切分。 | 適合標題與段落清楚的文件；chunk 大小可能不一致。原文稱為 variable-sized chunks based on content characteristics。 |
| **語意切分** | 把語意相關的句子與段落保留在同一單位，必要時跨越原始頁面邊界。 | 重視上下文連貫，不追求等長；需要能辨認語意單位的處理方式。 |
| **組合策略** | 混合固定長度與結構式方法，或在 chunk 中補入文件標題等上下文。 | 當單一策略不足時可調整，但規則較多，也需要用實際資料驗證。 |

以上分類與限制整理自 Microsoft Learn 的 Common chunking techniques；其中 Azure Text Split skill、Azure Content Understanding skill 等只屬產品實作例子，不是所有 RAG 系統的必要元件。[S03，原文章節：Common chunking techniques](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#common-chunking-techniques)

## Chunk Overlap

Overlap 是讓相鄰 chunk 重複少量文字。它的目的不是增加新資料，而是避免一個概念剛好被切分邊界拆開，讓下一個 chunk 仍保有部分前文。

Microsoft 文件提供 512 tokens、25% overlap 作為起始建議，同時明確指出最佳比例會依內容類型與使用情境改變：高度結構化內容可能需要較少 overlap，敘事或對話內容可能需要較多。因此這些數字不是通用最佳值。[S03，原文章節：Content overlap considerations](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#content-overlap-considerations)

Overlap 也會帶來重複內容，所以不是越大越好；文件的範例指出，參數要依資料的實際 token 分布調整，過大的 overlap 甚至可能無法產生預期效果。[S03，原文章節：LangChain data chunking example](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#langchain-data-chunking-example)

## 如何選擇 Chunk Size？

沒有脫離資料與任務的單一最佳大小。至少要一起考慮：[S03，原文章節：Factors for chunking data](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#factors-for-chunking-data)

1. **文件形態與密度**：是否需要保留完整段落或句子？內容是否很密集？
2. **預期查詢**：使用者通常尋找單一事實，還是需要較完整的上下文？
3. **模型限制**：embedding、摘要或生成模型能接受多少輸入？同一份 chunk 可能要同時符合多個模型。
4. **實際用途**：chunk 會拿來建立 embedding、做摘要，還是直接提供給模型？

較大的 chunk 能保存更多上下文，但可能混合多個主題；較小的 chunk 比較聚焦，卻可能失去前後關係。這是設計時需要用實際資料與查詢驗證的取捨，而不是只抄一組固定參數。[S03，原文章節：Common chunking techniques；Factors for chunking data](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents#common-chunking-techniques)

## 簡單範例

假設員工手冊依序有「請假」、「差旅」與「資訊安全」三個標題：

- 固定長度切分可能每 500 tokens 建立一個 chunk，規則簡單，但有機會從段落中間切開。
- 依結構切分可以把三個標題下的內容分開，讓每個 chunk 聚焦一個主題。
- 若一段差旅規則跨越數個段落，語意切分會嘗試把彼此相關的說明保留在一起。
- 如果邊界附近的句子需要前文才能理解，可以加入少量 overlap。

這是依來源原理製作的教學案例，不是 Microsoft 文件中的產品設定，也不表示每份文件都應採用相同參數。

## 通用原理與 Azure 功能的界線

固定長度、依結構、語意切分、overlap，以及依文件／查詢／模型限制調整大小，是可跨實作理解的 Chunking 原理。Azure AI Search indexers、skillsets、integrated vectorization、Text Split skill、Azure Content Understanding skill，以及 `textSplitMode`、`maximumPageLength`、`pageOverlapLength` 等名稱或參數，則是 Azure 環境的功能與例子，不是所有 RAG 系統都必須使用。[S03，原文位置：主標題下的導言；Common chunking techniques；How chunking fits into the workflow；Text Split skill example](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents)

## 相關 Wiki

- [RAG 架構與流程](02-architecture.md)
- [向量嵌入](04-embedding.md)
- [資訊檢索](05-retrieval.md)

## 來源

- **S02** — AWS Prescriptive Guidance, [Understanding Retrieval Augmented Generation](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)，擷取日期：2026-11-16。
- **S03** — Microsoft Learn, [Chunk large documents for RAG and vector search in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents)，頁面更新日期：2026-07-02；擷取日期：2026-11-16。
