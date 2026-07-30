"""
장학 공고 첨부파일(HWP/HWPX/이미지)에서 텍스트를 뽑아내는 도구.

사용법:
    python extract_text.py <파일경로> [<파일경로2> ...]

지원 형식:
    .hwp   - 구버전 한글 바이너리 포맷 (pyhwp 사용)
    .hwpx  - 신버전 한글 포맷, zip+XML 구조 (표준 라이브러리만 사용)
    .png/.jpg/.jpeg/.bmp/.tif/.tiff - 이미지 OCR (Tesseract, 한국어+영어)
"""
import re
import subprocess
import sys
import zipfile
from pathlib import Path

TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_DIR = r"C:\Users\bumku\AppData\Local\tessdata"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def extract_hwp(path: Path) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "hwp5.hwp5txt", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"hwp5txt 실패: {result.stderr}")
    return result.stdout


def extract_hwpx(path: Path) -> str:
    texts = []
    with zipfile.ZipFile(path) as z:
        section_names = sorted(
            n for n in z.namelist() if re.match(r"Contents/section\d+\.xml$", n)
        )
        for name in section_names:
            xml = z.read(name).decode("utf-8", errors="replace")
            # <hp:t>...</hp:t> 태그 안의 텍스트만 뽑아냄 (본문 텍스트 런)
            texts.extend(re.findall(r"<hp:t[^>]*>(.*?)</hp:t>", xml, re.DOTALL))
    plain = "\n".join(texts)
    # 남은 HTML 엔티티 정도만 간단히 복원
    return plain.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def extract_image(path: Path) -> str:
    import pytesseract
    from PIL import Image

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    img = Image.open(path)
    return pytesseract.image_to_string(
        img, lang="kor+eng", config=f"--tessdata-dir {TESSDATA_DIR}"
    )


def extract(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".hwp":
        return extract_hwp(path)
    if ext == ".hwpx":
        return extract_hwpx(path)
    if ext in IMAGE_EXTS:
        return extract_image(path)
    raise ValueError(f"지원하지 않는 형식: {ext}")


def _print(text: str) -> None:
    # 콘솔 코드페이지(cp949 등)가 못 그리는 문자가 있어도 죽지 않게 안전하게 출력
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for arg in sys.argv[1:]:
        path = Path(arg)
        _print(f"===== {path.name} =====")
        try:
            _print(extract(path))
        except Exception as e:
            _print(f"[추출 실패] {e}")
        _print("")


if __name__ == "__main__":
    main()
