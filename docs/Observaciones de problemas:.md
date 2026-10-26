Observaciones de problemas:
- AI SAST (qwiet scan) demora mas de 15min
- Traceable no envia notificacion via webhook 
- SCS no hace correlacion de artifacts deployed
- SCS no hace correlacion de vuln identified por otro pipeline execution
- Traceable external vs internal endpoints no son identificados correctamente por el eBPF (ingress pod siempre es internal)
- Traceable blocking WAAP policies ?


Observaciones a complementar:
- Feature Flag en el componente del Chat
- Habilitar el chat post canary
- Apagar el Chat via FF y bloquear en Traceable