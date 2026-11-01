"""Overlay genuine participant clips on slides. Missing clips stop production."""
from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
import pymupdf

from common import ROOT, read_json, write_json


def ffmpeg(args,check=True):
    result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner',*map(str,args)],
        capture_output=True,text=True,encoding='utf-8',errors='replace',check=False,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if check and result.returncode:raise RuntimeError('FFmpeg: '+result.stderr[-2500:])
    return result


def probe(path):
    result=ffmpeg(['-i',path],check=False)
    log=result.stderr
    hit=re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)',log)
    if not hit or 'Video:' not in log or 'Audio:' not in log:
        raise ValueError(f'Cannot establish finite duration, video and audio tracks: {path.name}')
    h,m,s=map(float,hit.groups())
    return h*3600+m*60+s


def overlay(slide,clip,target,duration):
    filters='[0:v]scale=1920:1080,setsar=1[bg];[1:v]scale=252:448:force_original_aspect_ratio=decrease,pad=252:448:(ow-iw)/2:(oh-ih)/2:black,setsar=1[cam];[bg][cam]overlay=1644:540:shortest=1[v]'
    ffmpeg(['-y','-loop','1','-framerate','30','-i',slide,'-i',clip,
        '-filter_complex',filters,'-map','[v]','-map','1:a:0','-t',duration,
        '-r','30','-c:v','libx264','-preset','fast','-crf','20','-threads','4',
        '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2',
        '-movflags','+faststart',target])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--self-test',action='store_true',help='Synthetic 0.6s technical fixture in temporary directory, not a group video')
    args=p.parse_args()
    if args.self_test:
        with tempfile.TemporaryDirectory(prefix='safra_video_qa_') as tmp:
            folder=Path(tmp);clip=folder/'synthetic_test_fixture.mp4';out=folder/'test_output.mp4'
            ffmpeg(['-y','-f','lavfi','-i','color=c=teal:s=180x320:r=30',
                '-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','0.6',
                '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',clip])
            slide=folder/'slide.png'
            with pymupdf.open(ROOT/'outputs/draft/apresentacao_esg.pdf') as doc:
                doc[0].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(slide)
            overlay(slide,clip,out,.6)
            duration=probe(out)
            if not .55<=duration<=.75:raise ValueError('Synthetic assembly duration mismatch')
        write_json('outputs/qa/video_pipeline_test.json',dict(status='passed',fixture='synthetic_color_and_tone_0.6s_in_temporary_directory_deleted',
            tested='real encoder, slide rendering, overlay, H264/AAC and duration probe',group_video_created=False))
        print('Synthetic technical fixture passed. No group video produced.')
        return 0
    config=read_json('config/video_segments.json')
    missing=[r['path'] for r in config['segments'] if not (ROOT/r['path']).is_file()]
    if missing:
        write_json('outputs/qa/video_readiness.json',dict(status='awaiting_real_clips',missing=missing,video_created=False))
        print('Real clips required; no video created:\n'+'\n'.join(missing))
        return 2
    durations=[probe(ROOT/r['path']) for r in config['segments']]
    if sum(durations)>600:raise ValueError('Actual clips exceed 10 minutes. Edit/rehearse with participants; no automatic speech acceleration.')
    write_json('outputs/qa/video_readiness.json',dict(status='clips_present_unreviewed',duration_seconds=sum(durations),video_created=False))
    if args.check:
        print('Actual total seconds',sum(durations),'; human review still pending.')
        return 0
    folder=ROOT/'outputs/qa/video_parts';folder.mkdir(parents=True,exist_ok=True)
    with pymupdf.open(ROOT/'outputs/draft/apresentacao_esg.pdf') as doc:
        for i,(segment,duration) in enumerate(zip(config['segments'],durations),1):
            slide=folder/f'slide_{segment["slide"]:02}.png'
            doc[segment['slide']-1].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(slide)
            overlay(slide,ROOT/segment['path'],folder/f'part_{i:02}.mp4',duration)
            print('Encoded genuine clip',i,flush=True)
    listing=folder/'concat.txt'
    listing.write_text(''.join(f"file 'part_{i:02}.mp4'\n" for i in range(1,len(durations)+1)),encoding='utf-8')
    target=ROOT/'outputs/draft/video_esg_rascunho.mp4'
    ffmpeg(['-y','-f','concat','-safe','1','-i',listing,'-c','copy','-movflags','+faststart',target])
    measured=probe(target)
    if measured>600:raise ValueError('Rendered duration exceeds limit; human edit required.')
    write_json('outputs/qa/video_readiness.json',dict(status='draft_video_awaiting_full_human_review',
        duration_seconds=measured,video_created=True,path=target.relative_to(ROOT).as_posix(),submitted=False))
    print('Draft created. Watch whole file and verify H07 before submission.')
    return 0


if __name__=='__main__':raise SystemExit(main())
