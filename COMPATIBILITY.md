# Document viewer results

Word 16.0.20326.20132 opened the generated DOCX on Windows on 7 September 2026. It displayed the synthetic text and requested the loopback pixel at `2026-09-07T18:27:35.267154+00:00`. The event recorded the Office User-Agent, high severity, source metadata, and a sent console alert.

| Path | Result |
| --- | --- |
| Local DOCX → Word → loopback receiver | Callback observed and stored |
| Word → public Azure receiver → Sentinel | Observed on Word 16.0; the persisted event led to High incident 17 ([cloud evidence](docs/evidence/public/upgrade/README.md#word-to-sentinel)) |
| Protected View or downloaded document | Not tested |
| Separate Windows VM or USB copy | Not tested |
| LibreOffice or Word Mobile | Not tested |
| Offline open | Not tested; callback requires connectivity |

The tested file came from local disk without an Internet zone marker. Office and endpoint policies were left unchanged.

The cloud run opened `Synthetic_word_022.docx` from local disk at 00:29 UTC on 8 September 2026 (7 September locally). Word requested the external HTTPS image; event `762163e649744aa4bd129ef081e1db4d` reached the deployed 0.2.2 receiver and Sentinel. This run did not exercise Protected View, a downloaded attachment, another endpoint, or a mobile viewer.
