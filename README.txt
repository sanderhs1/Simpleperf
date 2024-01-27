How to run simpleperf and tests to generate data:
Run server:
simpleperf.py -s
simpleperf.py -s -b (ip address) select ip address
simpleperf.py -s -p (Port number)
simpleperf.py -s -f (format: B, KB, MB)
Run client:
simpleperf.py -c
simpleperf.py -c -I (Server ip) select server ip address
simpleperf.py -c -p (select port)
simpleperf.py -c -t (time duration)
simpleperf.py -c -f (format)
simpleperf.py -c -i (interval)
simpleperf.py -c - P (Parallell connections)
simpleperf.py -c -n (Number of bytes)
