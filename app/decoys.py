from __future__ import annotations

from html import escape
from pathlib import Path
import zipfile


TRANSPARENT_GIF_B64 = "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="


def validate_filename(filename: str) -> str:
    """Require a plain file name so decoy generation cannot escape its output directory."""
    if (
        not filename
        or "\x00" in filename
        or "/" in filename
        or "\\" in filename
        or Path(filename).name != filename
    ):
        raise ValueError("filename must be a plain file name without path components")
    return filename


def callback_url(base_url: str, token_id: str) -> str:
    return f"{base_url.rstrip('/')}/t/{token_id}/pixel.gif"


def create_html_decoy(output: Path, filename: str, url: str) -> Path:
    validate_filename(filename)
    output.mkdir(parents=True, exist_ok=True)
    path = output / filename
    html = f"""<!doctype html>
<html>
<head><meta charset=\"utf-8\"><title>Financial Records</title></head>
<body>
<h1>Financial Records</h1>
<p>CONFIDENTIAL</p>
<img src=\"{escape(url, quote=True)}\" alt=\"\" width=\"1\" height=\"1\" style=\"display:none\">
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def create_docx_decoy(output: Path, filename: str, url: str) -> Path:
    """Create a minimal DOCX containing an externally linked 1x1 image.

    Office/protected-view/network policy may block external content. That is a
    deliberate limitation of callback-based document canaries and should be
    validated in the target lab before relying on it.
    """
    validate_filename(filename)
    output.mkdir(parents=True, exist_ok=True)
    path = output / filename

    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>
</Types>"""

    root_rels = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>
</Relationships>"""

    doc_rels = f"""<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image\" Target=\"{escape(url, quote=True)}\" TargetMode=\"External\"/>
</Relationships>"""

    document_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>
<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"
 xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"
 xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\"
 xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\"
 xmlns:pic=\"http://schemas.openxmlformats.org/drawingml/2006/picture\">
 <w:body>
  <w:p><w:r><w:t>Financial Records</w:t></w:r></w:p>
  <w:p><w:r><w:t>CONFIDENTIAL</w:t></w:r></w:p>
  <w:p><w:r><w:drawing>
   <wp:inline distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\">
    <wp:extent cx=\"9525\" cy=\"9525\"/>
    <wp:docPr id=\"1\" name=\"Telemetry Pixel\"/>
    <a:graphic><a:graphicData uri=\"http://schemas.openxmlformats.org/drawingml/2006/picture\">
     <pic:pic>
      <pic:nvPicPr><pic:cNvPr id=\"0\" name=\"pixel\"/><pic:cNvPicPr/></pic:nvPicPr>
      <pic:blipFill><a:blip r:link=\"rId2\"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
      <pic:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/><a:ext cx=\"9525\" cy=\"9525\"/></a:xfrm><a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></pic:spPr>
     </pic:pic>
    </a:graphicData></a:graphic>
   </wp:inline>
  </w:drawing></w:r></w:p>
  <w:sectPr/>
 </w:body>
</w:document>"""

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
    return path
