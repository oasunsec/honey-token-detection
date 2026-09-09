# Local Word callback

[GIF preview](local-word-callback.gif) - [MP4 recording](local-word-callback.mp4)

I recorded this on 8 September 2026 UTC with Word 16, a loopback FastAPI receiver, SQLite, and console alerts. Opening `Financial_Records_CONFIDENTIAL.docx` produced a callback. The stored User-Agent identified Microsoft Office 16, the event severity was `high`, and the console alert was `sent`. The [saved event](local-word-event.json) contains the record.

The document uses synthetic financial data.

The clip shows the CLI creating the file, Word opening it, and the callback event. The callback token, addresses, paths, and personal details are not shown.

The [case study](../../CASE_STUDY.md) covers the separate Azure-to-Sentinel test.
