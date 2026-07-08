from sqlalchemy import text
from database import engine

def verify():
    with engine.connect() as conn:
        # --- menu 검증 ---
        menu_total = conn.execute(text("SELECT COUNT(*) FROM menu")).scalar()
        menu_bad_price = conn.execute(text(
            "SELECT COUNT(*) FROM menu WHERE 가격 <= 0"
        )).scalar()
        menu_null_name = conn.execute(text(
            "SELECT COUNT(*) FROM menu WHERE 메뉴명 IS NULL"
        )).scalar()

        # --- orders 검증 ---
        orders_total = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        orders_bad_qty = conn.execute(text(
            "SELECT COUNT(*) FROM orders WHERE 수량 <= 0"
        )).scalar()
        orders_unknown_menu = conn.execute(text("""
            SELECT COUNT(*) FROM orders
            WHERE 메뉴코드 NOT IN (SELECT 메뉴코드 FROM menu)
        """)).scalar()
        orders_dup = conn.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT 주문일시, 테이블번호, 메뉴코드, COUNT(*) AS cnt
                FROM orders
                GROUP BY 주문일시, 테이블번호, 메뉴코드
                HAVING COUNT(*) > 1
            ) t
        """)).scalar()

    print('==== menu 검증 ====')
    print(f'전체 건수 : {menu_total}')
    print(f'가격 이상값 : {menu_bad_price}')
    print(f'메뉴명 NULL : {menu_null_name}')

    print('==== orders 검증 ====')
    print(f'전체 건수 : {orders_total}')
    print(f'수량 이상값 : {orders_bad_qty}')
    print(f'존재하지 않는 메뉴코드 참조 : {orders_unknown_menu}')
    print(f'중복 키 건수 : {orders_dup}')

    ok = (
        menu_total > 0 and menu_bad_price == 0 and menu_null_name == 0
        and orders_total > 0 and orders_bad_qty == 0
        and orders_unknown_menu == 0 and orders_dup == 0
    )
    print(f'검증 결과 : {"PASS" if ok else "FAIL"}')
    return ok

if __name__ == '__main__':
    verify()