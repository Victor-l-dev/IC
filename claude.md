# Regras Gerais de Desenvolvimento

## Autoridade

O usuário possui a decisão final sobre arquitetura,
escopo e implementação.

Nunca assumir decisões importantes sem aprovação.

## Análise antes da implementação

Antes de modificar qualquer código:

1. Entender a estrutura do projeto.
2. Identificar a tecnologia utilizada.
3. Identificar a arquitetura existente.
4. Localizar os arquivos relacionados à tarefa.
5. Verificar dependências entre Frontend e Backend.
6. Verificar se já existe uma implementação semelhante.

## Comunicação

Não apresentar informações irrelevantes.

Priorizar:

- problemas;
- inconsistências;
- dependências;
- riscos;
- decisões necessárias;
- arquivos afetados;
- próximos passos.
- otimizações

## Alterações

Não alterar código fora do escopo da tarefa.

Não criar novas abstrações ou dependências sem necessidade.

Não substituir tecnologias existentes sem aprovação.

## Aprovação

Sempre solicitar aprovação antes de:

- alterar arquitetura;
- alterar banco de dados;
- alterar contratos de API;
- alterar autenticação;
- adicionar dependências importantes;
- modificar partes não relacionadas à tarefa.
- modificar qualquer arquivo

## Qualidade

Após implementar:

- verificar erros;
- executar lint quando disponível;
- executar testes quando disponíveis;
- executar build quando apropriado.

Nunca afirmar que uma implementação está funcionando
sem verificar quando for possível verificá-la.


