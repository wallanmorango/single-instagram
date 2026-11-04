"""Monta um Reel (MP4 1080x1920, H.264 + AAC) a partir de quadros JPEG.

Cada quadro aparece por alguns segundos com um leve zoom, e a troca entre
quadros usa transição suave. Áudio opcional: só trilhas livres de direitos.

Uso:
  python scripts/reel.py posts/2026-11-10 --quadros quadro01.jpg quadro02.jpg quadro03.jpg \
      --duracoes 3 4 4 --audio trilhas/leve.mp3
"""
import argparse
import subprocess
from pathlib import Path

FPS = 30
TRANSICAO = 0.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--quadros", nargs="+", required=True)
    ap.add_argument("--duracoes", nargs="+", type=float)
    ap.add_argument("--audio")
    ap.add_argument("--saida", default="video.mp4")
    args = ap.parse_args()

    pasta = Path(args.pasta)
    duracoes = args.duracoes or [3.5] * len(args.quadros)
    if len(duracoes) != len(args.quadros):
        raise SystemExit("Informe uma duração por quadro.")

    cmd = ["ffmpeg", "-y"]
    for quadro, d in zip(args.quadros, duracoes):
        cmd += ["-loop", "1", "-t", str(d + TRANSICAO), "-i", str(pasta / quadro)]
    if args.audio:
        cmd += ["-i", args.audio]

    filtros = []
    for i, d in enumerate(duracoes):
        frames = int((d + TRANSICAO) * FPS)
        filtros.append(
            f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.0006,1.06)':d={frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}]"
        )
    atual, offset = "v0", 0.0
    for i in range(1, len(duracoes)):
        offset += duracoes[i - 1]
        filtros.append(f"[{atual}][v{i}]xfade=transition=fade:duration={TRANSICAO}:offset={offset:.2f}[x{i}]")
        atual = f"x{i}"
    total = sum(duracoes) + TRANSICAO

    cmd += ["-filter_complex", ";".join(filtros), "-map", f"[{atual}]"]
    if args.audio:
        a = len(args.quadros)
        cmd += ["-map", f"{a}:a", "-af", f"afade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-movflags", "+faststart", str(pasta / args.saida)]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Reel gerado: {pasta / args.saida} ({total:.1f}s)")


if __name__ == "__main__":
    main()
