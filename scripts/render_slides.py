"""Actual LibreOffice conversion, PDF rendering and geometry checks."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pymupdf
from PIL import Image, ImageOps, ImageDraw
from pptx import Presentation

from common import ROOT, write_json, sha256


def render():
    executable=Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
    if not executable.is_file():
        raise FileNotFoundError("LibreOffice executable not available; H12 PDF fallback required")
    out=ROOT/"outputs/draft"
    profile=(ROOT/"outputs/qa/lo_profile").as_uri()
    diagnostics=[]
    for name,expected in [("apresentacao_esg",9),("apoio_tecnico",7)]:
        ppt=out/(name+".pptx")
        result=subprocess.run([str(executable),f"-env:UserInstallation={profile}","--headless","--convert-to","pdf:impress_pdf_Export","--outdir",str(out),str(ppt)],capture_output=True,text=True,timeout=90,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        pdf=out/(name+".pdf")
        if result.returncode or not pdf.is_file():
            raise RuntimeError(f"PDF export failed: {result.stdout} / {result.stderr}")
        document=pymupdf.open(pdf)
        if len(document)!=expected:
            raise ValueError(f"Unexpected PDF page count {name}: {len(document)}")
        pictures=[]
        folder=ROOT/"outputs/qa/rendered"/name;folder.mkdir(parents=True,exist_ok=True)
        for i,page in enumerate(document):
            image_path=folder/f"slide_{i+1:02}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(image_path)
            pictures.append(image_path)
        cols=3;thumb_w=600;thumb_h=338;pad=18
        sheet=Image.new("RGB",(cols*(thumb_w+pad)+pad,((len(pictures)+cols-1)//cols)*(thumb_h+38+pad)+pad),"#edf4f6")
        draw=ImageDraw.Draw(sheet)
        for i,path in enumerate(pictures):
            im=Image.open(path).convert("RGB");im.thumbnail((thumb_w,thumb_h))
            x=pad+(i%cols)*(thumb_w+pad);y=pad+(i//cols)*(thumb_h+38+pad)
            draw.text((x,y),f"{name}  {i+1}",fill="#09283d")
            sheet.paste(im,(x,y+26))
        sheet.save(ROOT/"outputs/qa"/(name+"_contact_sheet.png"))
        presentation=Presentation(ppt)
        outside=[]
        for i,slide in enumerate(presentation.slides):
            for shape in slide.shapes:
                if shape.left<0 or shape.top<0 or shape.left+shape.width>presentation.slide_width+20 or shape.top+shape.height>presentation.slide_height+20:
                    outside.append(dict(slide=i+1,shape=shape.name))
        diagnostics.append(dict(name=name,pages=len(document),converter="LibreOffice headless isolated profile",shapes_outside_slide=outside,visual_review="pending_agent_image_inspection",pptx_sha256=sha256(ppt),pdf_sha256=sha256(pdf),pdf_path=pdf.relative_to(ROOT).as_posix(),log=result.stdout[-1000:]))
        print(name,"PDF pages",len(document),"outside",len(outside),flush=True)
    write_json("outputs/qa/rendering.json",diagnostics)


if __name__=="__main__":render()
