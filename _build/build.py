# -*- coding: utf-8 -*-
"""
How-to-CS : 통합 빌드 (이거 하나만 실행하면 됨)
  python _build/build.py

순서 보장: convert(지식층 재생성) -> build_index(운영층 재생성).
convert만 단독 실행하면 MOC가 지워진 채로 남으므로, 항상 이 래퍼를 쓴다.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert, build_index

def main():
    print("[1/2] 지식층 변환 (convert.py)")
    convert.run()
    print("[2/2] 운영층 생성 (build_index.py)")
    build_index.run()
    print("\n[OK] 빌드 완료. Obsidian에서 이 폴더를 vault로 열면 된다.")

if __name__ == "__main__":
    main()
