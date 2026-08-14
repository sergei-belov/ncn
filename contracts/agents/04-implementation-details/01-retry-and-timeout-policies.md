# Retry и timeout policies

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:1519-1663 -->
<!-- SOURCE-CONTENT-START -->
## 50. Retry policies

### Model call

```text
initial_interval = 2 seconds
backoff_coefficient = 2
maximum_interval = 20 seconds
maximum_attempts = 3
```

### MCP read

```text
initial_interval = 1 second
backoff_coefficient = 2
maximum_interval = 10 seconds
maximum_attempts = 3
```

### Idempotent MCP write

```text
initial_interval = 2 seconds
backoff_coefficient = 2
maximum_interval = 15 seconds
maximum_attempts = 3
```

### Non-idempotent MCP write

```text
maximum_attempts = 1
```

### PostgreSQL persistence

```text
initial_interval = 500 milliseconds
backoff_coefficient = 2
maximum_interval = 5 seconds
maximum_attempts = 5
```

### Qdrant

```text
initial_interval = 1 second
backoff_coefficient = 2
maximum_interval = 10 seconds
maximum_attempts = 3
```

### MinIO

```text
initial_interval = 1 second
backoff_coefficient = 2
maximum_interval = 15 seconds
maximum_attempts = 3
```

### Embeddings

```text
initial_interval = 2 seconds
backoff_coefficient = 2
maximum_interval = 20 seconds
maximum_attempts = 3
```

---

## 51. Timeouts

### Model call

```text
connect_timeout = 10 seconds
read_timeout = 180 seconds
start_to_close = 200 seconds
```

### MCP read

```text
connect_timeout = 10 seconds
read_timeout = 60 seconds
start_to_close = 75 seconds
```

### MCP write

```text
connect_timeout = 10 seconds
read_timeout = 90 seconds
start_to_close = 105 seconds
```

### Coordinator invocation

```text
active_execution_timeout = 15 minutes
```

### Worker invocation

```text
active_execution_timeout = 30 minutes
```

Ожидание Approval, input и budget не входит в active execution timeout.

### Artifact extraction

```text
10 minutes
```

### Embedding batch

```text
2 minutes
```

### PostgreSQL

```text
15 seconds
```

### Qdrant

```text
30 seconds
```

### MinIO metadata

```text
30 seconds
```

---

