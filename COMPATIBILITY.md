# Document viewer results

Word 16.0.20326.20132 opened the generated DOCX on Windows on 7 September 2026. It displayed the synthetic text and requested the loopback pixel at `2026-09-07T18:27:35.267154+00:00`. The event recorded the Office User-Agent, high severity, source metadata, and a sent console alert.

| Path | Result |
| --- | --- |
| Local DOCX → Word → loopback receiver | Callback observed and stored |
| Word → public Azure receiver | Not tested |
| Protected View or downloaded document | Not tested |
| Separate Windows VM or USB copy | Not tested |
| LibreOffice or Word Mobile | Not tested |
| Offline open | Not tested; callback requires connectivity |

The tested file came from local disk without an Internet zone marker. Office and endpoint policies were left unchanged.
