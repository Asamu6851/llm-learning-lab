# V1 Hardcoded Document Mini RAG

## 项目简介

本项目是一个从零实现的最小版 RAG（Retrieval-Augmented Generation）示例。

在这个版本中，知识库内容直接写死在 Python 代码中，不依赖外部文档、向量数据库或 LangChain。项目的主要目的是帮助理解 RAG 的基础流程，而不是追求复杂功能。

## 核心流程

```text
用户问题
↓
读取代码中写死的文档
↓
将文档切分成 chunks
↓
根据关键词匹配检索相关 chunks
↓
将检索结果拼接进 prompt
↓
调用大模型生成回答