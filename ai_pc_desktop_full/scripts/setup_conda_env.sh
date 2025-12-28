#!/bin/bash

echo "========================================"
echo "AI PC 아나콘다 가상환경 설정"
echo "========================================"
echo ""

# 아나콘다가 설치되어 있는지 확인
if ! command -v conda &> /dev/null; then
    echo "오류: 아나콘다가 설치되어 있지 않거나 PATH에 추가되지 않았습니다."
    echo "아나콘다를 설치하거나 PATH를 설정해주세요."
    exit 1
fi

# 현재 디렉토리로 이동
cd "$(dirname "$0")/.."

# 가상환경 이름
ENV_NAME="ai_pc"

echo "1. 기존 가상환경 확인..."
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "기존 가상환경 '${ENV_NAME}'이 존재합니다."
    read -p "덮어쓰시겠습니까? (y/N): " OVERWRITE
    if [[ "$OVERWRITE" == "y" || "$OVERWRITE" == "Y" ]]; then
        echo "기존 가상환경 삭제 중..."
        conda env remove -n ${ENV_NAME} -y
    else
        echo "취소되었습니다."
        exit 0
    fi
fi

echo ""
echo "2. 새 가상환경 생성 중 (Python 3.10)..."
conda create -n ${ENV_NAME} python=3.10 -y
if [ $? -ne 0 ]; then
    echo "오류: 가상환경 생성 실패"
    exit 1
fi

echo ""
echo "3. 가상환경 활성화 중..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ${ENV_NAME}

echo ""
echo "4. pip 업그레이드 중..."
python -m pip install --upgrade pip

echo ""
echo "5. 필요한 라이브러리 설치 중..."
echo "(이 작업은 시간이 걸릴 수 있습니다)"
pip install -r requirements.txt

echo ""
echo "6. sentence-transformers 모델 다운로드 (선택사항)..."
echo "모델은 첫 실행 시 자동으로 다운로드됩니다."

echo ""
echo "========================================"
echo "설정 완료!"
echo "========================================"
echo ""
echo "가상환경 활성화 방법:"
echo "  conda activate ${ENV_NAME}"
echo ""
echo "실행 방법:"
echo "  python run_web.py        (웹 UI)"
echo "  python run_desktop.py    (데스크톱 앱)"
echo ""

