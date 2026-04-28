# V2 Wiki-based Mini RAG

## 项目简介

本项目是在 V1 Mini RAG 的基础上升级得到的 Wiki 问答系统。

相比 V1 中将知识库内容写死在代码中，本版本支持从中文游戏 Wiki 页面 URL 中抓取网页内容，并基于抓取到的文本进行问答。

这个版本更接近真实 RAG 项目，因为实际项目中的知识来源通常不是手写文本，而是网页、文档、数据库或内部知识库。

## 核心流程

```text
用户输入 Wiki 页面 URL
↓
请求网页 HTML
↓
使用 BeautifulSoup 解析网页
↓
清洗 script / style / nav / footer 等无用内容
↓
提取页面文本
↓
切分为 chunks
↓
根据用户问题检索相关 chunks
↓
将检索结果拼接进 prompt
↓
调用大模型生成回答