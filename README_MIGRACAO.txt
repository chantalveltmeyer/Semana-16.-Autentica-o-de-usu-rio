ATUALIZAÇÃO FLASKY - LOGIN E CONFIRMAÇÃO POR E-MAIL

1. Faça backup antes de substituir arquivos.
2. Copie os arquivos mantendo a estrutura de pastas.
3. Não altere os valores secretos no WSGI.
4. A aplicação usa o Mailgun configurado no WSGI.
5. Usuários não autenticados são redirecionados para /login.
6. Qualquer usuário autenticado pode visualizar a lista, conforme a transcrição da aula.
7. O cadastro público cria contas com função User e confirmed=0.
8. O link enviado pelo Mailgun confirma a conta.
9. O login é permitido mesmo antes da confirmação, e a coluna Confirmado informa Sim/Não, conforme a demonstração descrita na transcrição.
10. A confirmação por e-mail exige que o endereço do novo usuário seja destinatário autorizado no domínio sandbox do Mailgun. Em domínio sandbox, destinatários não autorizados podem receber erro 403.

IMPORTANTE SOBRE OS 13 USUÁRIOS:
O banco novo recebe a coluna confirmed com valor padrão 0. Depois de instalar os arquivos, execute o script de recuperação de confirmação fornecido separadamente para copiar os 13 valores do banco antigo data.sqlite, sem copiar novamente os usuários.
