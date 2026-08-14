# Artifact storage

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2750-2809 -->
<!-- SOURCE-CONTENT-START -->
## 101. MinIO

Используется MinIO.

Максимальный файл:

```text
50 MiB
```

MIME types:

```text
application/pdf
application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

Используется multipart upload.

Bucket не публичный.

Доступ через presigned URL.

Object key:

```text
projects/{project_id}/artifacts/{artifact_id}/source
```

---

## 102. PDF

Извлекается только текстовый слой.

Metadata:

```text
page_number
chunk_index
content_hash
```

OCR отсутствует.

---

## 103. DOCX

Извлекаются:

- headings;
- paragraphs;
- простой текст таблиц;
- порядок элементов.

---

# Часть XVI. Tracing и аудит

