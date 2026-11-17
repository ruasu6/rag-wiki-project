# 向量嵌入

## Embedding 是什麼？

Embedding 是文字的數值表示，用來表達文件內容的語意或脈絡。AWS 說明，若要進行相關性搜尋，需要把文件與使用者 query 轉成相容的表示形式。[S02，原文位置：主標題下四個編號步驟的步驟 1；原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## 核心概念

1. 文件先經過資料處理與 chunking。
2. Embedding model 把文件內容轉成數值表示。
3. Vector database 保存 embedding、對應文字與 metadata。
4. 查詢時，系統也把 query 轉成相容的表示，再用於相關性搜尋。[S02，原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## Embedding 與 Vector Database 不一樣

- **Embedding** 是內容的數值表示。
- **Vector database** 是保存 embedding、文字及 metadata，並支援搜尋與檢索的索引系統。

兩者合作，但不是同一個元件。[S02，原文位置：主標題下四個編號步驟的步驟 1；原文章節：Components of production-level RAG systems](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)

## 簡單範例

假設文件中有「如何申請年假」，而使用者詢問「休假申請方式」。系統可把文件與 query 轉成數值表示，再用相關性搜尋尋找候選內容。這是概念示意；本來源沒有提供向量距離公式、維度或特定 embedding model 的選擇方法。

## 本頁目前的範圍

目前只建立 embedding、query 與 vector database 的基礎關係。向量距離、模型差異、維度與 API 用法將留待 S04 補充。

## 相關 Wiki

- [RAG 架構與流程](02-architecture.md)
- [文件切分](03-chunking.md)
- [資訊檢索](05-retrieval.md)

## 來源

- **S02** — AWS Prescriptive Guidance, [Understanding Retrieval Augmented Generation](https://docs.aws.amazon.com/prescriptive-guidance/latest/retrieval-augmented-generation-options/what-is-rag.html)，擷取日期：2026-11-16。

## S04 補充：向量如何支援語意搜尋

Embedding 是浮點數組成的向量。兩個向量的距離可用來衡量文字相關程度：距離較小通常代表相關程度較高。[S04，原文章節：What are embeddings?](https://developers.openai.com/api/docs/guides/embeddings#what-are-embeddings)

在語意搜尋中，文件 chunk 與 query 都轉成向量，再依相似度排序候選內容。這讓系統能比較意思是否接近，而不只比對完全相同的關鍵字。[S04，原文章節：What are embeddings?；Use cases](https://developers.openai.com/api/docs/guides/embeddings#use-cases)

OpenAI 文件建議其 embeddings 使用 cosine similarity，並說明其向量已正規化為長度 1，因此 cosine similarity 與 Euclidean distance 會得到相同排序。這是 OpenAI embedding 的性質，不代表所有 embedding model 都有相同特性。[S04，原文章節：Which distance function should I use?](https://developers.openai.com/api/docs/guides/embeddings#which-distance-function-should-i-use)

### 來源補充

- **S04** — OpenAI, [Vector embeddings](https://developers.openai.com/api/docs/guides/embeddings)，擷取日期：2026-11-16。
