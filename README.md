# Digitalizacja ustrukturyzowanych dokumentów z pismem odręcznym - studium przypadku

Aby uruchomić aplikację należy:\
-utworzyć projekt w Google Cloud,\
-dodać procesor Document OCR w usłudze Google Cloud,\
-po wejściu w zakładkę moje procesory w usłudze Google Cloud należy kliknąć na nazwę utworzonego procesora i skopiować jego identyfikator, \
![image](https://github.com/user-attachments/assets/dc498205-7d67-4fae-ac29-b05097968d44)

-dodać klucz API (https://cloud.google.com/api-keys/docs/get-started-api-keys), \
-do zmiennej **json_credentials** dodać scieżkę do swojego klucza API następnie w kodzie aplikacji w funkcji **process_document_ai**,  \
-do zmiennej **processor_id** należy dodać identyfikator swojego procesora, \
-w terminalu przejść do folderu z aplikacją i uruchomić ją komendą ,,python main.py"
