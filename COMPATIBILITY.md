# Document viewer results

Opened a generated DOCX in Word 16.0.20326.20132 on Windows on 7 September 2026. Word displayed the synthetic text and requested the loopback pixel at `2026-09-07T18:27:35.267154+00:00`. The stored User-Agent was `Mozilla/4.0 (compatible; ms-office; MSOffice 16)`; the event had high severity and a sent console alert.

| Path | Coverage |
| --- | --- |
| Local DOCX -> Word -> loopback receiver | Observed callback |
| Word -> public Azure receiver | Not tested |
| Protected View or downloaded document | Not tested |
| Separate Windows VM or USB copy | Not tested |
| LibreOffice or Word Mobile | Not tested |
| Offline open | Not tested; remote reporting requires connectivity |

The tested file came from local disk without an Internet zone marker. Office and endpoint policies were not changed.
