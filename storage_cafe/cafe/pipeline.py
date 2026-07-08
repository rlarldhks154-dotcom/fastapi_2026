from database import init_db
from loader import load_menu, load_orders
from verify import verify

def main():
    print('1) 저장 구조 준비 (menu: 자연키 / orders: 대체키+UNIQUE)')
    init_db()

    print()
    print('2) menu.csv 적재 (merge upsert)')
    load_menu()

    print()
    print('3) orders.csv 적재 (배치 insert + ON CONFLICT DO NOTHING)')
    load_orders()

    print()
    print('4) 적재 검증')
    verify()

if __name__ == '__main__':
    main()