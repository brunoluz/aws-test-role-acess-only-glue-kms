**Projeto**

Este repositório contém exemplos Terraform (diretório `infra/`) e testes em Python (diretório `tests/`) para demonstrar um padrão de controle de acesso KMS. O objetivo principal é evidenciar que, usando a condição `kms:ViaService` com o valor `glue.sa-east-1.amazonaws.com`, é possível permitir que uma role só consiga descriptografar chaves KMS quando a chamada vier do serviço AWS Glue na região `sa-east-1`.

**Recursos Terraform (diretório `infra/`)**

- `data.tf`: contém data sources usados pelo conjunto de recursos (por exemplo `aws_caller_identity`).
- `glue.tf`: provê recursos relacionados ao AWS Glue (databases/tables usados nos testes).
- `kms.tf`: cria chaves KMS e aliases (por exemplo o alias usado por Glue no exemplo).
- `role_shoud_access_all_kms.tf`: define uma role e política que permite acesso KMS amplo (útil como referência/contraste).
- `role_shoud_access_only_glue_kms.tf`: define a role `role-should-access-only-glue-kms` e uma política que restringe `kms:Decrypt` de forma que somente chamadas originadas pelo serviço Glue na região `sa-east-1` e que apontem para o alias KMS correto sejam permitidas. Esta política contém:
  - Uma declaração `Allow` para `kms:Decrypt` com condições:
    - `StringEquals` `kms:ViaService = "glue.sa-east-1.amazonaws.com"`
    - `ForAnyValue:StringEquals` `kms:ResourceAliases = "${aws_kms_alias.kms_glue_catalog.name}"` (limita o alias)
  - Declarações `Deny` explícitas para bloquear `kms:Decrypt` quando `kms:ViaService` não for `glue.sa-east-1.amazonaws.com` ou quando o alias não for o alias do Glue catalog.
- `s3.tf`: contém o bucket/objeto S3 utilizado nos testes (objeto criptografado com a KMS key).
- `secrets_manager.tf`: cria um segredo em Secrets Manager que está criptografado pela KMS key de teste.
- `versions.tf`: define versões / provedores do Terraform.

**Comportamento esperado da política KMS**

No arquivo `role_shoud_access_only_glue_kms.tf` a política de IAM faz o seguinte:

- Permite acesso amplo a Glue, Lake Formation, S3 e SecretsManager para que a role possa interagir com os recursos (necessário para os testes de integração).
- Para `kms:Decrypt`, há uma `Allow` condicional que só concede a operação quando a chamada KMS contém o contexto `kms:ViaService` igual a `glue.sa-east-1.amazonaws.com` e quando a chave usada corresponde ao alias do Glue catalog (via `kms:ResourceAliases`).
- Há duas declarações `Deny` explícitas que garantem a negação de `kms:Decrypt` quando qualquer uma das condições não for satisfeita:
  - nega se `kms:ViaService` não for `glue.sa-east-1.amazonaws.com`;
  - nega se `kms:ResourceAliases` não corresponder ao alias do Glue.

Efeito prático: se a role tentar descriptografar (por exemplo, ao acessar um objeto S3 ou um segredo do Secrets Manager) e a solicitação KMS não vier via Glue (ou não usar o alias correto), a operação será negada explicitamente por política de identidade.

Este padrão demonstra como scoping baseado em `kms:ViaService` pode limitar as permissões KMS por origem de serviço.

**Testes (diretório `tests/`)**

- `test_role_should_access_all_kms.py`: conjunto de testes que assume a role `role-should-access-all-kms` (política permissiva) e valida que as operações com Glue, S3 e Secrets Manager funcionam conforme esperado.
- `test_role_should_access_only_glue_kms.py`: assume a role `role-should-access-only-glue-kms` (aquela com a política baseada em `kms:ViaService`) e valida que:
  - Acesso a Glue (`get_database`, `get_table`) tem sucesso.
  - Acesso ao objeto S3 (criptografado com KMS) falha com `AccessDenied` e mensagem indicando `kms:Decrypt` negado por identidade (explicit deny).
  - Acesso ao Secrets Manager (criptografado com KMS) falha com `AccessDeniedException` e mensagem "Access to KMS is not allowed".
- `utils.py`: utilitários de teste; fornece `assume_role()` que usa STS para assumir as roles e retornar credenciais temporárias. O `REGION` usado é `sa-east-1`.
- `requirements.txt`: dependências de teste — `pytest` e `boto3`.

Os testes operam assumindo as roles já criadas pelo Terraform e então realizando chamadas reais via `boto3` para verificar se KMS permite ou nega `Decrypt` conforme esperado.

**Como executar (resumo)**

1. Configure suas credenciais AWS (variáveis de ambiente `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` ou `~/.aws/credentials`) com permissão para aplicar o Terraform e criar recursos.

2. (Opcional) Crie um ambiente virtual Python e instale dependências de teste:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r tests/requirements.txt
```

3. Aplicar a infraestrutura (no diretório `infra`):

```bash
cd infra
terraform init
# ajuste a variável aws_region se necessário; os exemplos usam sa-east-1
terraform apply -var "aws_region=sa-east-1"
```

4. Executar os testes (a partir do root do repositório):

```bash
pytest -q
```

Observação: os testes assumem que as roles `role-should-access-all-kms` e `role-should-access-only-glue-kms` já existem e que os recursos (Glue database/table, bucket S3, segredo) estão presentes e configurados para usar a KMS key criada.

**Interpretação dos resultados**

- Se os testes em `test_role_should_access_only_glue_kms.py` mostrarem que as chamadas Glue foram bem-sucedidas e que S3/SecretsManager foram negados com mensagens relacionadas a KMS, então a política baseada em `kms:ViaService = glue.sa-east-1.amazonaws.com` funcionou como esperado.
- Se a role com acesso amplo (`role-should-access-all-kms`) conseguir acessar tudo, isso demonstra o comportamento de comparação entre políticas permissiva e restritiva.

**Avisos e recomendações**

- Testes/execução real irão criar recursos AWS reais e podem gerar custos; execute em conta/ambiente de teste.
- Valide sempre a região (`sa-east-1`) quando usar `kms:ViaService`, pois a string `glue.<region>.amazonaws.com` deve corresponder à região onde a chamada Glue ocorre.
