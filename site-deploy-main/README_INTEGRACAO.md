# Integração da estação meteorológica

## 1. Supabase
1. Crie um projeto gratuito no Supabase.
2. Abra SQL Editor e execute `docs/supabase.sql`.
3. Em Project Settings > API, copie a Project URL e a `service_role` key.

## 2. Vercel
Adicione estas variáveis de ambiente no projeto:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `INGEST_API_KEY`

Use uma chave longa e aleatória para `INGEST_API_KEY`.
Depois faça um novo deploy.

## 3. Computador da estação
Instale:
`python -m pip install -r requirements.txt`

Defina a chave usada na Vercel. No CMD do Windows:
`set ESTACAO_API_KEY=SUA_CHAVE`

Opcionalmente, para usar outra URL:
`set ESTACAO_API_URL=https://SEU-SITE.vercel.app/api/sensors`

Feche o MakeCode "Mostrar dispositivo" e execute:
`python capturar_estacao.py`

O micro:bit central deve enviar linhas neste formato:
`TEMP:26,UMI:77,VENTO:5,UV:145,PRESSAO:94390`

A pressão recebida em Pa é convertida para hPa antes de ser salva.
