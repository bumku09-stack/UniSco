"""
장학 공고 첨부파일(HWP/HWPX/PDF/이미지)에서 텍스트를 뽑아내는 도구.

사용법:
    python extract_text.py <파일경로> [<파일경로2> ...]

지원 형식:
    .hwp   - 구버전 한글 바이너리 포맷 (pyhwp 사용)
    .hwpx  - 신버전 한글 포맷, zip+XML 구조 (표준 라이브러리만 사용)
    .pdf   - PDF (poppler의 pdftotext 사용, -layout으로 표 구조 최대한 보존)
    .png/.jpg/.jpeg/.bmp/.tif/.tiff - 이미지 OCR (Tesseract, 한국어+영어)
"""
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

# 기본값은 데이터 입력 담당자의 Windows 로컬 경로 그대로 유지(그 워크플로는 안 건드림) —
# env var로 오버라이드 가능하게만 열어둠. harness_nightly.yml(GitHub Actions, Linux)이
# apt로 설치한 tesseract를 쓰도록 TESSERACT_EXE=tesseract, TESSDATA_DIR=(미설정)을 넘김.
TESSERACT_EXE = os.environ.get("TESSERACT_EXE", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA_DIR = os.environ.get("TESSDATA_DIR", r"C:\Users\bumku\AppData\Local\tessdata")

# 2026-08-18 추가 — poppler(pdftotext). mac(brew install poppler)/GitHub Actions(apt install
# poppler-utils) 둘 다 설치하면 그냥 "pdftotext"로 PATH에서 찾음 — TESSERACT_EXE처럼 OS별
# 기본 경로를 하드코딩할 필요가 없음(poppler는 Windows 전용 고정 경로 관례가 없어서).
PDFTOTEXT_EXE = os.environ.get("PDFTOTEXT_EXE", "pdftotext")

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


def extract_pdf(path: Path) -> str:
    # -layout: 표/컬럼 구조를 공백으로 최대한 흉내내서 보존(장학금 공고문에 흔한 "구분/조건/
    # 지급액" 표 형태를 줄바꿈만으로 뭉개지 않기 위함) — 기본 모드는 컬럼이 섞여서 나옴.
    # "-": stdout으로 바로 받음(임시 출력파일 안 만듦).
    result = subprocess.run(
        [PDFTOTEXT_EXE, "-layout", str(path), "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext 실패: {result.stderr}")
    text = result.stdout
    if not text.strip():
        # 텍스트 레이어가 없는 스캔본(이미지로만 이루어진 PDF) — pdftotext는 에러 없이 빈
        # 문자열만 돌려주므로, 여기서 명시적으로 실패 처리해서 "빈 원문을 추출 성공"으로
        # 잘못 취급하지 않게 함. 이미지 PDF까지 지원하려면 페이지를 래스터화(pdftoppm 등)해서
        # extract_image()의 OCR 경로로 넘기는 방식이 필요한데, 아직 실제로 마주친 적이 없어서
        # (2026-08-18 기준) 안 만듦 — 필요해지면 여기에 추가.
        raise RuntimeError("텍스트 레이어 없음(스캔 이미지 PDF로 추정) — OCR 미지원")
    return text


def extract_image(path: Path) -> str:
    import pytesseract
    from PIL import Image

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    img = Image.open(path)
    # TESSDATA_DIR=""(빈 문자열)이면 --tessdata-dir을 아예 안 붙임 — apt로 설치한 tesseract는
    # 자기 기본 위치를 이미 알아서, 강제로 경로를 지정하는 쪽이 오히려 깨짐(GitHub Actions용).
    config = f"--tessdata-dir {TESSDATA_DIR}" if TESSDATA_DIR else ""
    return pytesseract.image_to_string(img, lang="kor+eng", config=config)


def extract(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".hwp":
        return extract_hwp(path)
    if ext == ".hwpx":
        return extract_hwpx(path)
    if ext == ".pdf":
        return extract_pdf(path)
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
