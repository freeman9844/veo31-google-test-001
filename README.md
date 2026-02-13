# Veo 3.1 4K 비디오 생성 및 확장 데모

[English Version](README.en.md)

이 프로젝트는 Google Cloud Vertex AI의 **Veo 3.1** 모델을 사용하여 4K 해상도의 비디오를 생성하고, 생성된 비디오를 다시 4K 해상도로 확장(Extension)하는 Python 예제 코드입니다.

## 주요 기능

- **4K 비디오 생성 (Generation)**: 텍스트 프롬프트를 기반으로 4K 해상도의 고화질 비디오를 생성합니다.
- **4K 비디오 확장 (Extension)**: 생성된 비디오의 마지막 부분을 이어받아 새로운 내용으로 4K 해상도를 유지하며 비디오를 확장합니다.
- **자동 재시도 및 에러 처리**: API 호출 실패 시 지수 백오프(Exponential Backoff)를 사용한 자동 재시도 로직이 포함되어 있습니다.

## 사전 준비 사항 (Prerequisites)

이 코드를 실행하기 위해서는 다음 사항들이 준비되어야 합니다.

1.  **Google Cloud Project**: Veo 3.1 모델 사용이 가능한 Google Cloud 프로젝트.
2.  **Vertex AI API 활성화**: 해당 프로젝트에서 Vertex AI API가 활성화되어 있어야 합니다.
3.  **Google Cloud Storage (GCS) 버킷**: 생성된 비디오를 저장할 GCS 버킷.
4.  **Python 환경**: Python 3.9 이상 권장.
5.  **`uv` 패키지 매니저**: 빠르고 효율적인 의존성 관리를 위해 `uv` 사용을 권장합니다.

## 설치 및 환경 설정

### 1. 프로젝트 클론

```bash
git clone https://github.com/freeman9844/veo31-google-test-001.git
cd veo31-google-test-001
```

### 2. 의존성 설치 (Using `uv`)

`uv`를 사용하여 가상환경을 생성하고 필요한 패키지를 설치합니다.

```bash
# 가상환경 생성 (없는 경우)
uv venv

# 패키지 설치
uv pip install google-genai
```

### 3. Google Cloud 인증

로컬 환경에서 실행 시, Google Cloud SDK를 사용하여 인증합니다.

```bash
gcloud auth application-default login
```

### 4. 코드 설정

`veo_demo.py` 파일을 열어 다음 변수들을 본인의 환경에 맞게 수정해야 합니다. (또는 환경 변수로 설정)

```python
# veo_demo.py

# 1. Project ID & Location
# 환경 변수 GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION 으로 설정하거나 코드 직접 수정
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# 2. GCS Bucket URI (필수 수정)
OUTPUT_GCS_URI = "gs://your-bucket-name" 
```

## 사용 방법 (Usage)

### 스크립트 실행

`uv`를 통해 스크립트를 실행합니다.

```bash
uv run veo_demo.py
```

또는 일회성으로 의존성을 포함하여 바로 실행할 수도 있습니다.

```bash
uv run --with google-genai veo_demo.py
```

### 실행 결과

스크립트가 정상적으로 실행되면 콘솔에 다음과 같은 로그가 출력됩니다.

1.  **Video Generation**: 4K 비디오 생성 시작 및 진행 상황.
2.  **Video Extension**: 생성된 비디오를 기반으로 4K 확장 진행.
3.  **Result**: 최종 생성된 비디오의 GCS URI 출력.

```text
--- Generating video with model veo-3.1-generate-preview ---
Prompt: A cinematic drone shot...
...
Video generation successful!
Video URI: gs://your-bucket-name/.../sample_0.mp4

--- Extending video ---
Input Video: gs://your-bucket-name/.../sample_0.mp4
...
Video extension successful!
Extended Video URI: gs://your-bucket-name/.../sample_0.mp4
```

## 문제 해결 (Troubleshooting)

### Internal Error (Code 13)

4K 생성 또는 확장 시 `Internal error. Please try again later.` (Code 13) 에러가 발생할 수 있습니다.

-   **원인**: Veo 3.1 모델의 4K 생성은 높은 리소스를 요구하며, 특정 리전(us-central1 등)의 일시적인 리소스 부족이나 서비스 상태에 따라 간헐적으로 발생할 수 있습니다.
-   **해결 방법**:
    1.  잠시 후 다시 시도합니다. (스크립트에 재시도 로직이 포함되어 있습니다.)
    2.  지속적으로 실패할 경우, 해상도를 `1080p`로 낮추어 테스트해 보시기 바랍니다.

### Quota Error (Code 8)

-   **원인**: API 호출 할당량(Quota)을 초과했을 때 발생합니다.
-   **해결 방법**: 스크립트에 포함된 지수 백오프 로직이 자동으로 재시도합니다. 만약 계속 실패한다면 GCP 콘솔에서 Quota를 확인하고 상향 요청해야 합니다.

