# Память, артефакты и lifecycle

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:3632-3733 -->
<!-- SOURCE-CONTENT-START -->
## 155. ProjectState pipeline

Не определены:

- источники фактов;
- частота расчёта;
- инициатор расчёта;
- model prompt;
- structured schema;
- confidence;
- stale-state rules;
- повторная генерация;
- storage table.

---

## 156. RAG ingestion

Необходимо определить:

- Kafka events для индексации;
- reindex commands;
- batching;
- failure queue;
- tombstones;
- duplicate chunks;
- content version;
- stale chunks;
- поиск по нескольким типам источников;
- ranking и reranking.

---

## 157. RAG ACL future model

В MVP секретные данные не индексируются.

Для будущего необходимо решить:

- private Session;
- закрытые задачи;
- CRM ACL;
- department-level access;
- user-level access;
- metadata filters;
- reindex при смене ACL.

---

## 158. Artifact processing

Не выбраны конкретные библиотеки для:

- PDF extraction;
- DOCX extraction;
- MIME detection;
- token counting;
- chunking.

Не определены:

- malware scanning;
- encrypted PDF;
- corrupted files;
- password-protected DOCX;
- extraction retry;
- quarantine.

---

## 159. Session deletion

Нужно определить точную реализацию удаления:

- Temporal Workflow termination;
- Temporal history retention;
- удаление Search Attributes;
- Qdrant consistency;
- MinIO shared artifacts;
- audit anonymization;
- recovery window.

---

## 160. Retention

Автоматическая business retention отсутствует.

Позднее необходимо определить:

- Session retention;
- RunEvent retention;
- AuditEvent retention;
- Artifact retention;
- Qdrant retention;
- Kafka retention;
- Temporal retention;
- backup retention;
- deleted secret retention.

---

