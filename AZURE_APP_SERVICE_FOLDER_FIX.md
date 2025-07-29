# 🔧 Correção: Azure App Service - Problema de Pasta Backend

## 🚨 **Problema Identificado**

O Azure App Service está procurando `requirements.txt` na raiz do projeto, mas os arquivos estão na pasta `backend/`. Isso causa erro:

```
Could not find requirements.txt
```

## ✅ **Soluções Implementadas**

### **Solução 1: Arquivos de Redirecionamento (RECOMENDADO)**

Criei arquivos na raiz que redirecionam para o backend:

#### **1.1 requirements.txt (raiz)**
```txt
# GapHunter - Requirements para Azure App Service
# Este arquivo aponta para os requirements do backend

-r backend/requirements-prod.txt
```

#### **1.2 startup.py (raiz)**
```python
#!/usr/bin/env python3
"""
GapHunter - Startup script para Azure App Service
Este script inicia a aplicação FastAPI do backend
"""

import sys
import os

# Adicionar pasta backend ao Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Mudar diretório de trabalho para backend
os.chdir(backend_path)

# Importar e executar o startup do backend
if __name__ == "__main__":
    from startup import main
    main()
```

### **Solução 2: Configuração Manual no Portal Azure**

Se a Solução 1 não funcionar, configure manualmente:

#### **2.1 Configurar App Settings**
No Azure Portal → App Service → Configuration:

| Setting | Value |
|---------|-------|
| `PROJECT` | `backend` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |
| `ENABLE_ORYX_BUILD` | `true` |
| `PRE_BUILD_SCRIPT_PATH` | `backend/requirements-prod.txt` |

#### **2.2 Configurar Startup Command**
- **Startup Command**: `python startup.py`

### **Solução 3: Deployment Source Configuration**

#### **3.1 Via Azure CLI**
```bash
az webapp config appsettings set \
  --resource-group gaphunter-rg \
  --name gaphunter-backend \
  --settings PROJECT=backend
```

#### **3.2 Via Portal**
1. App Service → **Deployment Center**
2. **Settings** → **Build Configuration**
3. **App location**: `/backend`
4. **Save**

## 🔄 **Como Aplicar a Correção**

### **Método 1: Redeploy Automático**
1. Os arquivos já foram commitados no GitHub
2. O App Service fará redeploy automático
3. Aguarde 5-10 minutos

### **Método 2: Deploy Manual**
1. No App Service → **Deployment Center**
2. Clique **"Sync"** para forçar novo deploy
3. Acompanhe logs em **"Logs"**

### **Método 3: Restart App Service**
1. No App Service → **Overview**
2. Clique **"Restart"**
3. Aguarde reinicialização

## 🔍 **Verificar se Funcionou**

### **1. Logs de Deploy**
1. App Service → **Deployment Center** → **Logs**
2. Verifique se aparece:
   ```
   Looking for requirements.txt... Found
   Installing from requirements.txt...
   ```

### **2. Application Logs**
1. App Service → **Log stream**
2. Verifique se não há erros de import

### **3. Teste da API**
1. Acesse: `https://gaphunter-backend.azurewebsites.net/docs`
2. Deve carregar a documentação da API

## 🆘 **Troubleshooting**

### **Ainda não encontra requirements.txt:**
```bash
# Verificar estrutura no App Service
az webapp ssh --resource-group gaphunter-rg --name gaphunter-backend

# Dentro do SSH:
ls -la
cat requirements.txt
```

### **Erro de import do backend:**
1. Verifique se `startup.py` está na raiz
2. Confirme que `backend/startup.py` existe
3. Verifique logs de erro específicos

### **Build falha:**
1. App Service → **Development Tools** → **Console**
2. Execute manualmente:
   ```bash
   cd /home/site/wwwroot
   pip install -r requirements.txt
   python startup.py
   ```

## 📁 **Estrutura Final Esperada**

```
gaphunter/
├── requirements.txt          # ← NOVO (aponta para backend)
├── startup.py               # ← NOVO (redireciona para backend)
├── backend/
│   ├── requirements-prod.txt # ← Original
│   ├── startup.py           # ← Original
│   └── app/
│       └── ...
└── frontend/
    └── ...
```

## ✅ **Vantagens desta Solução**

- ✅ **Compatibilidade**: Funciona com deploy automático do GitHub
- ✅ **Simplicidade**: Não requer mudança de estrutura
- ✅ **Manutenção**: Fácil de entender e manter
- ✅ **Flexibilidade**: Permite diferentes configurações por ambiente

## 🎯 **Resultado Esperado**

Após aplicar a correção:
1. ✅ App Service encontra `requirements.txt`
2. ✅ Instala dependências corretamente
3. ✅ Inicia aplicação FastAPI
4. ✅ API fica disponível em `/docs`

---

**💡 Esta correção resolve o problema de estrutura de pastas mantendo a organização do projeto!**

