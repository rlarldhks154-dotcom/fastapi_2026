import os
import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database import engine
from models import Menu, Order

BASE_DIR = os.getcwd()
MENU_PATH = os.path.join(BASE_DIR, 'input', 'menu.csv')
ORDERS_PATH = os.path.join(BASE_DIR, 'input', 'orders.csv')


def load_menu(path: str = MENU_PATH) -> dict:
    """
    menu는 메뉴코드가 자연키이므로, 버스 방식처럼 merge()로 적재해도 되고
    ON CONFLICT DO UPDATE로 최신 가격을 반영해도 된다.
    여기서는 버스와 동일하게 merge() 방식을 사용한다.
    """
    df = pd.read_csv(path, encoding='utf-8-sig')

    from database import get_session
    db = get_session()
    success, failed = 0, 0

    for _, row in df.iterrows():
        try:
            m = Menu(
                메뉴코드=str(row['메뉴코드']),
                메뉴명=str(row['메뉴명']),
                가격=int(row['가격']),
            )
            db.merge(m)
            db.commit()
            success += 1
        except Exception as e:
            db.rollback()
            failed += 1
            print(f'menu 적재 실패 - {row.get("메뉴코드")} / {e}')

    db.close()
    print(f'[loader] menu 적재 완료 - 성공 {success}건 / 실패 {failed}건')
    return {'success': success, 'failed': failed}


def load_orders(path: str = ORDERS_PATH) -> dict:
    """
    orders는 자연키가 없으므로, 지하철 방식처럼 대체키(id) + UNIQUE 제약 +
    ON CONFLICT DO NOTHING으로 적재한다.
    """
    df = pd.read_csv(path, encoding='utf-8-sig')
    df['주문일시'] = pd.to_datetime(df['주문일시'], errors='coerce')
    df = df.dropna(subset=['주문일시', '테이블번호', '메뉴코드', '수량'])

    records = df[['주문일시', '테이블번호', '메뉴코드', '수량']].to_dict(orient='records')

    if not records:
        return {'success': 0, 'skipped_duplicate': 0, 'failed': 0}

    try:
        with engine.begin() as conn:
            stmt = pg_insert(Order).values(records)
            stmt = stmt.on_conflict_do_nothing(constraint='uq_orders_key')
            result = conn.execute(stmt)

        inserted = result.rowcount if result.rowcount is not None else 0
        skipped = len(records) - inserted

        print(f'[loader] orders 적재 완료 - 신규 {inserted}건 / 중복스킵 {skipped}건')
        return {'success': inserted, 'skipped_duplicate': skipped, 'failed': 0}

    except Exception as e:
        print(f'orders 적재 실패: {e}')
        return {'success': 0, 'skipped_duplicate': 0, 'failed': len(records)}


if __name__ == '__main__':
    load_menu()
    load_orders()