# Compatibility matrix

| Environment | Result | Notes |
|---|---|---|
| Microsoft Word Windows 16.0.20326.20132 | Passed for local generated DOCX, 2026-09-07 | Rendered synthetic content and fetched loopback pixel under existing settings; Office User-Agent persisted. |
| Word Protected View | Not Tested | Expected policy limitation is recorded if blocked. |
| Windows VM Word | Not Tested until a controlled VM is available | Separate endpoint proof. |
| USB copy to Word | Not Tested until physical USB test is available | Same DOCX should retain relationship. |
| LibreOffice Linux | Not Tested | Experimental viewer behavior. |
| Word Mobile | Not Tested | Experimental viewer behavior. |
| Offline open | Cannot remotely report | No network callback is expected. |

Observed Word callback at `2026-09-07T18:27:35.267154+00:00` with
`Mozilla/4.0 (compatible; ms-office; MSOffice 16)`. SQLite recorded a high-severity
`canary_trigger` and console alert status `sent`. The file was opened from local
disk, not downloaded with an Internet zone marker. This does not establish
Protected View, USB, mobile, separate-endpoint, or public HTTPS Word behavior.
