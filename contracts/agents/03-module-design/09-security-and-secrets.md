# Безопасность и secrets

<!-- SOURCE: Контракт%20реализации%20мультиагентного%20ядра%20v1.3%20draft.md:2644-2749 -->
<!-- SOURCE-CONTENT-START -->
## 97. Пользовательская аутентификация

Используются Keycloak, единый realm, OAuth2 Proxy и `ncn-authz-api`.

Project roles хранятся в `ncn-authz-api`. Agent-core получает проверенный identity payload и самостоятельно проверяет `project_id`, actor identity и Project constraints.

Workload OAuth системного MCP не используется для пользовательского login flow и не передаётся агентам.

---

## 98. Machine-to-machine системного MCP

Применяется паттерн централизованной авторизации через доверенный `agent-core`.

```text
Keycloak
→ аутентифицирует workload agent-core
→ выдаёт service access token через client_credentials

OAuth2 Proxy
→ проверяет signature, issuer, audience, exp и nbf
→ разрешает доступ только доверенному agent-core

agent-core
→ является PDP и PEP для Agent permissions/Approval
→ формирует trusted execution context
→ вызывает разрешённый MCP tool

MCP
→ доверяет authorization decision agent-core
→ проверяет schema, Project scope, domain invariants и idempotency
```

Для каждого системного MCP используется отдельная audience. Один token не должен содержать audiences других системных MCP.

Service token может использоваться для нескольких MCP-вызовов до `exp`, хранится только в памяти и не передаётся в PostgreSQL, Temporal, Kafka, traces или logs. Рекомендуемый TTL — 1–5 минут, refresh margin — 30 секунд.

OAuth2 Proxy не должен перенаправлять API-клиента на interactive login, принимать arbitrary issuer, использовать trusted-IP bypass или пропускать authentication routes.

Входящие identity headers удаляются или перезаписываются. Проверенный bearer token не передаётся upstream MCP application.

Непосредственно перед MCP call agent-core проверяет Agent permission, Project constraints, tool risk policy, Approval policies/grants, payload constraints, Project isolation и idempotency key.

MCP использует только `execution_context.project_id`, сформированный backend-кодом, и не доверяет `arguments.project_id`.

Компрометация процесса agent-core или его client credentials признаётся компрометацией доступных ему системных MCP. Если эта доверительная граница перестаёт быть допустимой, требуется per-call capability token, online PDP/introspection или mTLS + отдельный PDP.

---

## 99. Secrets

Используются:

```text
Secret
└── SecretVersion
```

SecretVersion immutable и имеет статус:

```text
active
superseded
revoked
destroyed
```

Project secrets включают MCP API keys, Basic Auth и другие Project integration credentials.

Bootstrap/platform secrets включают PostgreSQL, Kafka, Temporal, Keycloak service-account credentials, model provider credentials и master-key ring.

Plaintext secret API отсутствует. Доступны create, replace/rotate, revoke и metadata.

---

## 100. Encryption и master-key rotation

Для каждого SecretVersion создаётся отдельный случайный DEK.

```text
plaintext
→ AES-256-GCM with DEK
→ ciphertext

DEK
→ AES-256-GCM with active master key
→ encrypted_dek
```

PostgreSQL хранит ciphertext, nonce/tag, encrypted_dek, master_key_id/version и metadata. Master keys в PostgreSQL не хранятся.

Для обычного Docker/deployment bootstrap secrets и key ring передаются через environment variables, `.env` вне Git или mounted secret. Для Kubernetes — через Kubernetes Secrets; дополнительные требования к Kubernetes hardening определяются отдельно.

Ротация master key:

1. добавить новый key version;
2. сделать его active;
3. новые SecretVersion шифровать новым key;
4. перешифровать только DEK существующих записей;
5. проверить отсутствие ссылок на старый key;
6. удалить старый key из deployment secret.

Расшифрованный Project secret существует только на время Invocation. Для model provider credentials допускается отдельный TTL cache до пяти минут.

# Часть XV. Artifact storage

