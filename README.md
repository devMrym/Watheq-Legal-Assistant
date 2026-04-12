## 💻 How to Use

1.  **Run the script:**
    ```bash
    python legal_chunker.py
    ```
2.  **Paste the text:** Copy the legal text from your source and paste it into the terminal.
3.  **Finalize:** Type **`done`** or **`تم`** and press Enter to start processing.
4.  **Check Output:** Your structured JSON will be available in the `output_chunks` folder.

## 📄 Output JSON Schema

Data is stored in a format optimized for searchability and AI context:

```json
{
  "system_info": {
    "system_name": "نظام_التوثيق",
    "issue_date": "١٩ ذو القِعدة ١٤٤١",
    "last_update_decree": "المرسوم الملكي رقم م/164",
    "related_regulations": [
      "اللائحة التنفيذية لنظام التوثيق"
    ]
  },
  "articles": [
    {
      "chunk_id": "نظام_التوثيق_Art_1",
      "hierarchy": {
        "part": "الباب الأول",
        "chapter": "الفصل الأول",
        "article_number": "المادة الأولى",
        "article_index": 1
      },
      "content": {
        "text": "Legal text content here..."
      }
    }
  ]
}