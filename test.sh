./tests/prepare_db.sh;
python3 main.py --init < tests/test_init.in.json | diff tests/test_init.out.json - ;
python3 main.py < tests/test1.in.json | diff tests/test1.out.json - ;
python3 main.py < tests/test_update_last_activity.in.json | diff tests/test_update_last_activity.out.json - ;
python3 main.py < tests/test_password_validation.in.json | diff tests/test_password_validation.out.json -;
./tests/prepare_db.sh;
python3 main.py --init < tests/test_init2.in.json | diff tests/test_init2.out.json - ;
python3 main.py < tests/test_random.in.json | diff tests/test_random.out.json - ;
