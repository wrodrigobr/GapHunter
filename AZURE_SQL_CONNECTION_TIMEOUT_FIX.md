# 🚨 Correção: Azure SQL Database - Timeout de Conexão

## 📋 **Problema Identificado**

```
sqlalchemy.exc.OperationalError: (pyodbc.OperationalError) 
('HYT00', '[HYT00] [Microsoft][ODBC Driver 18 for SQL Server]Login timeout expired (0) (SQLDriverConnect)')
```

**Causa**: O App Service não consegue conectar ao Azure SQL Database devido a:
1. **Firewall do SQL Server** bloqueando conexões
2. **Connection string** incorreta
3. **Configurações de rede** restritivas
4. **Driver ODBC** não configurado corretamente

## ✅ **Soluções Implementadas**

### **Solução 1: Configurar Firewall do SQL Server**

#### **1.1 Via Portal Azure**
1. Vá para **"gaphunter-sql-server"** (SQL Server)
2. Menu lateral → **"Networking"**
3. **Firewall rules**:
   - ✅ Marque **"Allow Azure services and resources to access this server"**
   - ✅ Adicione regra: **"AllowAppService"**
     - **Start IP**: `0.0.0.0`
     - **End IP**: `0.0.0.0`
4. Clique **"Save"**

#### **1.2 Via Azure CLI**
```bash
# Permitir serviços Azure
az sql server firewall-rule create \
  --resource-group gaphunter-rg \
  --server gaphunter-sql-server \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Permitir todos os IPs (temporário para teste)
az sql server firewall-rule create \
  --resource-group gaphunter-rg \
  --server gaphunter-sql-server \
  --name AllowAll \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

### **Solução 2: Corrigir Connection String**

#### **2.1 Connection String Correta**
```
mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes&Connection+Timeout=30
```

#### **2.2 Configurar no App Service**
1. **gaphunter-backend** → **Configuration**
2. **Application settings** → Editar **DATABASE_URL**
3. **Value**: (usar connection string acima com sua senha)
4. **Save**

### **Solução 3: Connection String Alternativa (pymssql)**

Se pyodbc não funcionar, use pymssql:
```
mssql+pymssql://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?charset=utf8&timeout=30
```

### **Solução 4: Configurações Adicionais no App Service**

#### **4.1 Variáveis de Ambiente Extras**
No App Service → Configuration → Application settings:

| Name | Value |
|------|-------|
| `SQLALCHEMY_ENGINE_OPTIONS` | `{"pool_timeout": 30, "pool_recycle": 300}` |
| `DB_CONNECTION_TIMEOUT` | `30` |
| `ODBCSYSINI` | `/opt/microsoft/msodbcsql18/etc` |

#### **4.2 Configuração de Rede**
```bash
# No App Service Configuration
WEBSITE_VNET_ROUTE_ALL=1
WEBSITE_DNS_SERVER=168.63.129.16
```

## 🔧 **Implementação Passo a Passo**

### **Passo 1: Configurar Firewall (CRÍTICO)**
1. Portal Azure → **"gaphunter-sql-server"**
2. **Networking** → **Firewall rules**
3. ✅ **"Allow Azure services"** = ON
4. Adicionar regra **"AllowAll"**:
   - Start: `0.0.0.0`
   - End: `255.255.255.255`
5. **Save**

### **Passo 2: Atualizar Connection String**
1. **gaphunter-backend** → **Configuration**
2. Editar **DATABASE_URL**:
```
mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes&Connection+Timeout=30&Login+Timeout=30
```
3. **Save**

### **Passo 3: Restart App Service**
1. **gaphunter-backend** → **Overview**
2. **Restart**
3. Aguardar 2-3 minutos

### **Passo 4: Verificar Logs**
1. **gaphunter-backend** → **Log stream**
2. Verificar se conexão funciona

## 🔍 **Diagnóstico e Teste**

### **Teste 1: Connection String Manual**
```python
# Teste no console do App Service
import pyodbc

conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=gaphunter-sql-server.database.windows.net;DATABASE=gaphunter;UID=gaphunter;PWD=SuaSenhaSegura123!;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"

try:
    conn = pyodbc.connect(conn_str)
    print("✅ Conexão OK!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
```

### **Teste 2: Telnet/Ping**
```bash
# No console do App Service
telnet gaphunter-sql-server.database.windows.net 1433
# Deve conectar se firewall estiver OK
```

### **Teste 3: SQLAlchemy**
```python
from sqlalchemy import create_engine

engine = create_engine(
    "mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes&Connection+Timeout=30"
)

try:
    conn = engine.connect()
    print("✅ SQLAlchemy OK!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
```

## 🆘 **Troubleshooting Avançado**

### **Erro: "Login timeout expired"**
- ✅ Verificar firewall do SQL Server
- ✅ Confirmar que "Allow Azure services" está habilitado
- ✅ Testar connection string manualmente

### **Erro: "SSL Provider: No credentials are available"**
- ✅ Adicionar `TrustServerCertificate=yes`
- ✅ Verificar se `Encrypt=yes` está presente

### **Erro: "Cannot open database"**
- ✅ Verificar se database "gaphunter" existe
- ✅ Confirmar permissões do usuário
- ✅ Testar com master database primeiro

### **Erro: "Driver not found"**
- ✅ Verificar se `pyodbc` está em requirements.txt
- ✅ Tentar `pymssql` como alternativa
- ✅ Verificar logs de build do App Service

## 📊 **Connection Strings Testadas**

### **Opção 1: pyodbc (Recomendado)**
```
mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes&Connection+Timeout=30
```

### **Opção 2: pymssql (Alternativa)**
```
mssql+pymssql://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?charset=utf8&timeout=30
```

### **Opção 3: pyodbc com parâmetros extras**
```
mssql+pyodbc://gaphunter:SuaSenhaSegura123!@gaphunter-sql-server.database.windows.net:1433/gaphunter?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=yes&Connection+Timeout=30&Login+Timeout=30&ConnectRetryCount=3&ConnectRetryInterval=10
```

## ✅ **Checklist de Verificação**

- [ ] **Firewall configurado**: Allow Azure services = ON
- [ ] **Regra de firewall**: 0.0.0.0 - 255.255.255.255 adicionada
- [ ] **Connection string**: Atualizada com timeouts
- [ ] **App Service**: Reiniciado após mudanças
- [ ] **Database**: Existe e está acessível
- [ ] **Logs**: Verificados para novos erros

## 🎯 **Resultado Esperado**

Após aplicar as correções:
1. ✅ App Service conecta ao SQL Database
2. ✅ Backend inicia sem erros
3. ✅ API fica disponível em `/docs`
4. ✅ Migrações podem ser executadas

---

**💡 O problema mais comum é o firewall do SQL Server. Configurar "Allow Azure services" resolve 90% dos casos!**

