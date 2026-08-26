# Todo_project에 ML 기능 붙이기

> 기존 Todo_project(FastAPI + JWT + PostgreSQL + CRUD + Streamlit) 에 "할 일 제목을 보고
> 카테고리(업무/개인/긴급)를 자동으로 분류"해주는 ML 기능을 단계별로 얹는 실습

## 이번 실습에서 배우는 것

1. 학습(training)과 서빙(serving)의 분리
    - 실무 MLOps의 가장 기본 원칙
2. 계층형 구조에 ML을 "부가 기능"으로 끼워넣는 법
    - 기존 프로젝트를 갈아엎지 않고 확장
3. 모델 예측값과 사람이 고친 값을 분리 저장
    - 나중에 정확도를 계산하고 재학습하기 위한 것
4. 정확도 모니터링 + 재학습(retrain) 흐름
    - "배포하고 끝"이 아니라 "계속 지켜본다"는 개념

## 1단계 - 시나리오 설명 및 설계 결정

- 왜 "완료 예측"이 아니라 "카테고리 자동분류"인가?
    - 완료 예측은 실제 사용 이력(며칠 뒤에 완료했는지 등)이 쌓여야 의미가 있는데, Todo_project는
      방금 만든 프로젝트라 데이터가 아직 준비되지 않았다.
    - 반면 카테고리 분류는 제목 텍스트만 있으면 바로 학습/시연이 가능하다.
- 카테고리는 3개로 단순화 : 업무 / 개인 / 긴급
- 모델이 예측한 값 / 사람이 나중에 확인·수정한 값을 분리해서 저장
    - 모델이 얼마나 자주 맞았는지 계산할 수 있고, 사람이 고친 값만 모아서 재학습 데이터로
      재사용할 수 있는 장점이 있다.

## 2단계 - 학습용 데이터 준비 (`ml/sample_labeled_data.csv`)

- `title`, `category` 두 컬럼의 CSV를 직접 생성해본다.

```csv
title,category
분기 보고서 작성하기,업무
팀 회의 자료 준비,업무
장보기 (우유, 계란, 빵),개인
빨래 돌리기,개인
서버 장애 즉시 확인,긴급
고객 컴플레인 응대,긴급
```

- 카테고리별로 10개 안팎, 최대한 골고루 섞어서 만든다.
- 실무에서는 이 "라벨링" 작업 자체가 가장 비용이 큰 작업이라는 걸 기억하자.

## 3단계 - 모델 학습 스크립트 (`ml/train_model.py`)

- FastAPI 서버와 완전히 분리된 별도 스크립트로 작성한다. **서버 코드 안에서 학습하지 않는다.**
  학습은 몇 초~몇 분 걸릴 수 있는 무거운 작업이라, API 요청 흐름 안에 넣으면 그동안 서버 전체가
  멈추기 때문이다.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
import pandas as pd

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])

if __name__ == "__main__":
    df = pd.read_csv(Path(__file__).resolve().parent / "sample_labeled_data.csv")
    X_train, X_test, y_train, y_test = train_test_split(
        df["title"], df["category"],
        test_size=0.2, random_state=42, stratify=df["category"],
    )
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    joblib.dump(pipeline, ARTIFACTS_DIR / "model_v1.pkl")
    joblib.dump(pipeline, ARTIFACTS_DIR / "latest.pkl")   # FastAPI는 이 파일만 봄
    print("학습 완료! latest.pkl 저장됨")
```

실행:
```bash
uv add scikit-learn pandas joblib
uv run python ml/train_model.py
```

⚠️ **반드시 서버를 켜기 전에 먼저 실행해야 한다.** `latest.pkl`이 없으면 서버는 정상적으로
켜지지만 카테고리 예측 기능만 계속 비활성화 상태(`None`)로 동작한다.

## 4단계 - DB 모델 확장 (`models.py`)

`Todo`에 컬럼 두 개를 추가한다. **하나가 아니라 둘로 나누는 이유**가 이 단계의 핵심이다.

```python
predicted_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
final_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
```

| 컬럼 | 채워지는 시점 | 의미 |
|---|---|---|
| `predicted_category` | 할 일 생성 시 자동 | "모델이 뭐라고 예측했는가" — 절대 덮어쓰지 않음 |
| `final_category` | 사용자가 확인/수정할 때만 | "사람이 최종 확인한 값" — 처음엔 비어있음 |

컬럼 추가 후 기존 테이블에는 이 컬럼이 없어서 에러가 날 수 있다. 가장 간단한 해결은
기존 `todo` 테이블을 지우고 서버를 다시 실행해 `create_all()`이 새로 만들도록 하는 것이다
(실습용 데이터라 유실 부담이 적다는 전제).

## 5단계 - 예측 전용 서비스 계층 (`services/category_service.py`)

이 서비스는 **DB에 전혀 접근하지 않는다.** router-service-repository 구조에서
repository가 없는 서비스도 있을 수 있다는 좋은 예시다.

```python
class CategoryPredictionService:
    def __init__(self, model):
        self.model = model  # main.py에서 미리 로드해둔 모델을 주입받음

    def predict(self, title: str) -> str:
        prediction = self.model.predict([title])  # sklearn은 항상 리스트로 입출력
        return prediction[0]
```

## 6단계 - 서버 시작 시 모델 로딩 (`main.py`의 `lifespan`)

무거운 모델 로딩은 요청마다가 아니라 **서버가 켜질 때 딱 한 번만** 수행해서
`app.state`에 보관한다.

```python
from pathlib import Path
import joblib
from contextlib import asynccontextmanager
from fastapi import FastAPI

MODEL_PATH = Path(__file__).resolve().parent / "ml" / "artifacts" / "latest.pkl"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    if MODEL_PATH.exists():
        app.state.category_model = joblib.load(MODEL_PATH)
        print(f"[INFO] 카테고리 예측 모델 로드 완료! : {MODEL_PATH}")
    else:
        # 모델 파일이 없어도 서버가 안 켜지게 막지 않는다.
        # 회원가입/로그인/Todo CRUD는 ML과 무관하게 항상 정상 동작해야 하기 때문이다.
        app.state.category_model = None
        print(f"[WARN] 모델 파일이 없습니다. ({MODEL_PATH})")

    yield

app = FastAPI(lifespan=lifespan)
```

## 7단계 - `schema/request.py`, `schema/response.py` 반영

요청(Request)과 응답(Response)의 역할이 다르다는 걸 기억하자.

```python
# schema/request.py
class TodoCreateRequest(BaseModel):
    title: str
    is_done: bool = False
    # predicted_category, final_category는 절대 여기 넣지 않는다!
    # 클라이언트가 직접 값을 지정할 수 있게 되면 "모델의 예측"이라는 의미가 깨진다.

class TodoUpdateRequest(BaseModel):
    title: str | None = None
    is_done: bool | None = None
    # 카테고리는 여기서도 다루지 않는다. 아래 CategoryUpdateRequest 전용 경로로만 수정한다.

class CategoryUpdateRequest(BaseModel):
    category: str = Field(..., description="사용자가 직접 확정한 카테고리 (업무/개인/긴급)")
```

```python
# schema/response.py
class TodoResponse(BaseModel):
    id: int
    title: str
    is_done: bool
    user_id: int | None
    predicted_category: str | None = None
    final_category: str | None = None
```

## 8단계 - TodoService에 예측 연결 (`services/todo_service.py`)

```python
class TodoService:
    def __init__(self, repository, category_service: CategoryPredictionService | None = None):
        self.repository = repository
        self.category_service = category_service   # 모델이 없으면 None

    def create_todo(self, body, user_id):
        predicted_category = None
        if self.category_service is not None:
            predicted_category = self.category_service.predict(body.title)
        todo = Todo(
            title=body.title, is_done=body.is_done,
            user_id=user_id, predicted_category=predicted_category,
        )
        return self.repository.save(todo)

    def update_category(self, todo_id, category, user_id):
        # 사용자가 예측 결과를 "맞다/틀리다"로 확인·수정하는 지점
        todo = self.get_todo(todo_id, user_id)
        todo.final_category = category
        return self.repository.save(todo)
```

## 9단계 - 라우터 반영 (`routers/todo.py`)

⚠️ **이 단계에서 실수가 가장 많이 나온다. 꼭 아래 두 가지를 확인하자.**

**① `get_todo_service`가 모델을 실제로 꺼내서 넘겨주고 있는가?**

```python
from fastapi import Request
from services.category_service import CategoryPredictionService

def get_todo_service(request: Request, session=Depends(get_session)) -> TodoService:
    category_model = getattr(request.app.state, "category_model", None)
    category_service = CategoryPredictionService(category_model) if category_model else None
    return TodoService(TodoRepository(session), category_service)
```

`request: Request`를 받지 않으면 `app.state.category_model`에 접근할 방법이 없다.
이걸 빠뜨리면 모델은 잘 로드됐는데도 `predicted_category`가 계속 `None`으로 저장된다.

**② 카테고리 엔드포인트 경로에 다른 엔드포인트와 같은 prefix가 붙어 있는가?**

```python
from schema.request import CategoryUpdateRequest  # import 빠뜨리지 않기!

@router.patch("/todos/{todo_id}/category", response_model=TodoResponse)
def update_todo_category_handler(
    todo_id: int,
    request: CategoryUpdateRequest,
    todo_service: TodoService = Depends(get_todo_service),
    user_id: int = Depends(get_current_user_id),
):
    return todo_service.update_category(todo_id, request.category, user_id)
```

다른 엔드포인트가 `/todos/{todo_id}`처럼 경로에 `/todos`를 직접 쓰는 스타일이라면,
새로 추가하는 이 엔드포인트도 반드시 `/todos`를 똑같이 붙여야 한다. 빠뜨리면
`/todos/1/category`가 아니라 `/1/category`로 등록되어 404가 난다.

## 10단계 - 모니터링 엔드포인트 (`routers/ml.py`)

```python
router = APIRouter(prefix="/admin", tags=["ML Monitoring"])

@router.get("/model-accuracy", response_model=ModelAccuracyResponse)
def get_model_accuracy_handler(session=Depends(get_session)):
    total_labeled = ...  # final_category가 채워진(=사람이 확인한) 개수
    correct = ...         # predicted_category == final_category인 개수
    accuracy = correct / total_labeled if total_labeled > 0 else None
    return ModelAccuracyResponse(total_labeled=total_labeled, correct=correct, accuracy=accuracy)
```

`GET /admin/model-accuracy`로 지금까지 모델이 얼마나 정확했는지 실시간으로 확인할 수 있다.

## 11단계 - Streamlit 프론트 반영 (`streamlit_app.py`)

- 할 일 카드에 `predicted_category` 뱃지 표시
- 카테고리 확인/수정용 selectbox 추가

```python
CATEGORY_OPTIONS = ["업무", "개인", "긴급"]

predicted = todo.get("predicted_category")
final = todo.get("final_category")

if predicted:  # 모델이 없어서 예측이 안 된 Todo는 이 영역 자체를 표시하지 않는다.
    current_value = final if final else predicted
    selected = st.selectbox(
        "카테고리 확인/수정",
        CATEGORY_OPTIONS,
        index=CATEGORY_OPTIONS.index(current_value) if current_value in CATEGORY_OPTIONS else 0,
        key=f"category_{todo['id']}",
    )
    if selected != current_value:
        requests.patch(
            f"{API_BASE}/todos/{todo['id']}/category",
            json={"category": selected},
            headers=get_headers(),
        )
        st.rerun()
```

> 참고: selectbox 초기값이 이미 예측값과 같기 때문에, "모델이 맞았다"는 걸 확정하려면
> 사용자가 값을 한 번 바꿨다가 다시 원래 값으로 되돌려야 `final_category`가 채워진다.
> 시간 여유가 있다면 "이대로 확정" 버튼을 추가해 이 부분을 개선해봐도 좋다.

## 12단계 - 재학습 스크립트 (`ml/retrain.py`)

사용자가 실제로 확인/수정한 `final_category` 데이터를 모아서 모델을 다시 학습한다.

```python
combined_df = pd.concat([original_df, corrected_df]).drop_duplicates(subset=["title"], keep="last")
pipeline = build_pipeline()
pipeline.fit(X_train, y_train)
joblib.dump(pipeline, ARTIFACTS_DIR / "latest.pkl")
```

실행: `uv run python ml/retrain.py`

⚠️ 재학습해도 예측이 바로 바뀌지 않는다. `lifespan`은 서버 켤 때 딱 한 번만 모델을
메모리에 올리기 때문에, `latest.pkl`이 바뀌어도 이미 떠 있는 서버는 모른다.
**서버를 재시작**해야 새 모델이 반영된다.

## 13단계 - 통합 시연 순서

1. `uv run python ml/train_model.py` 실행 → 정확도 로그 확인
2. `uv run uvicorn main:app --reload` 서버 기동 → 콘솔에 `[INFO] 카테고리 예측 모델 로드 완료` 확인
3. Swagger(`/docs`)에서 `POST /todos`로 할 일 생성 → 응답에 `predicted_category` 채워지는지 확인
4. `PATCH /todos/{id}/category`로 확정 → `final_category` 채워지는지 확인
5. `GET /admin/model-accuracy` 호출 → 정확도 확인
6. Streamlit 실행(`uv run streamlit run streamlit_app.py`) → 뱃지/selectbox 동작 확인
7. (선택) `uv run python ml/retrain.py` → 서버 재시작 → 예측이 바뀌는지 재확인

---

# 🔥 트러블슈팅 — 자주 발생하는 오류

## 1. `predicted_category`가 계속 `null`로만 나와요

**원인**: `routers/todo.py`의 `get_todo_service()`가 `category_service`를 `TodoService`에
넘기지 않고 있을 가능성이 가장 큽니다.

```python
# 원인이 되는 코드
def get_todo_service(session=Depends(get_session)) -> TodoService:
    return TodoService(TodoRepository(session))   # category_service가 빠짐
```

서버 로그에 `[INFO] 카테고리 예측 모델 로드 완료!`가 찍혔는지 먼저 확인하고,
찍혔는데도 `null`이라면 위 함수를 9단계의 완성 코드와 다시 비교해보세요.

## 2. `PATCH /todos/{id}/category`를 호출하면 404가 떠요

**원인**: Swagger의 curl 명령을 확인했을 때 `/todos/1/category`가 아니라
`/1/category`처럼 `/todos`가 빠진 상태로 등록됐을 가능성이 있습니다.
`routers/todo.py`의 다른 엔드포인트와 똑같이 경로 앞에 `/todos`가 붙어 있는지
확인하세요.

## 3. `NameError: CategoryUpdateRequest`가 떠요

**원인**: `schema/request.py`에는 정의했지만 `routers/todo.py` 상단에서
import를 안 한 경우입니다.

```python
from schema.request import TodoCreateRequest, TodoUpdateRequest, CategoryUpdateRequest
```

## 4. 카테고리를 입력하는 칸을 못 찾겠어요

`predicted_category`는 사람이 직접 입력하는 필드가 아닙니다. `title`만 넣고
`POST /todos`를 호출하면 서버가 자동으로 예측해서 채워줍니다.

`final_category`는 `TodoCreateRequest`나 `TodoUpdateRequest`가 아니라
**`PATCH /todos/{id}/category`라는 별도 엔드포인트**로만 입력합니다.
Swagger의 Todo 그룹 안에 이 엔드포인트가 따로 있는지 확인하세요.

## 5. 서버는 잘 켜지는데 모델이 로드가 안 돼요 (`[WARN]` 로그)

**원인**: `ml/train_model.py`를 아직 실행하지 않아서 `ml/artifacts/latest.pkl`
파일 자체가 없는 상태입니다. 서버를 켜기 **전에** 먼저 학습 스크립트를 실행하세요.

```bash
uv run python ml/train_model.py
```

## 6. Todo 생성/수정 시 `predicted_category`, `final_category`를 요청에 넣었더니 에러가 나요

`TodoCreateRequest`, `TodoUpdateRequest`에는 이 두 필드를 추가하지 않습니다.
`predicted_category`는 서버가 자동으로 채우는 값이고, `final_category`는
`CategoryUpdateRequest`(`PATCH /todos/{id}/category`)로만 입력받습니다.
요청 모델에 이 필드들을 넣으면 설계 원칙(예측값은 서버만 채운다)이 깨집니다.

## 7. 재학습(`ml/retrain.py`)을 했는데 예측이 그대로예요

`latest.pkl`은 갱신됐지만, 서버는 시작할 때 딱 한 번만 모델을 메모리에 올려두기
때문입니다. **서버를 재시작**해야 새 모델이 반영됩니다.