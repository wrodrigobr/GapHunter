# Configuração de Variáveis de Ambiente

## Visão Geral

O projeto usa variáveis de ambiente para configurar diferentes URLs da API para desenvolvimento e produção.

## Arquivos de Environment

### Development (`src/environments/environment.ts`)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'  // Backend local
};
```

### Production (`src/environments/environment.prod.ts`)
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://gaphunter-backend.azurewebsites.net'  // Backend Azure
};
```

## Como Usar

### Desenvolvimento
```bash
npm start
# ou
ng serve --configuration=development
```

### Produção
```bash
npm run build:prod
# ou
ng build --configuration=production
```

### Builds Disponíveis
```bash
npm start                    # Desenvolvimento (serve)
npm run build:dev          # Build desenvolvimento
npm run build:prod         # Build produção
npm run build              # Build padrão (produção)
```

## Configuração no angular.json

O arquivo `angular.json` está configurado para:
- **Development**: Usa `environment.ts`
- **Production**: Substitui automaticamente `environment.ts` por `environment.prod.ts`

## Como Alterar URLs

### Para Desenvolvimento
Edite `src/environments/environment.ts`:
```typescript
apiUrl: 'http://localhost:8000'  // Altere para sua URL local
```

### Para Produção
Edite `src/environments/environment.prod.ts`:
```typescript
apiUrl: 'https://sua-url-de-producao.com'  // Altere para sua URL de produção
```

## Vantagens

1. **Flexibilidade**: Fácil alteração entre ambientes
2. **Segurança**: URLs sensíveis não ficam hardcoded
3. **Automatização**: Build automático para cada ambiente
4. **Manutenibilidade**: Configuração centralizada

## Alternativas Consideradas

- **Variáveis de ambiente do sistema**: Mais complexo para Angular
- **Arquivo de configuração**: Menos flexível que environments
- **Hardcoding**: Não recomendado para produção

**Variáveis de environment são a melhor opção para Angular!** ✅ 