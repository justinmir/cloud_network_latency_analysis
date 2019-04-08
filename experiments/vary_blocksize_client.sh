HOST=$1
PORT=$2

BLOCK_SIZES=(1 10 100 1000 10000 100000 1000000 10000000 100000000)
# BLOCK_SIZES=(1 10)
for size in ${BLOCK_SIZES[*]}; do
	f_name=latency_${size}.txt
	python3 ../src/measure.py --client --host=$HOST --port=$PORT --block_size_b=$size --latency_fname=$f_name
done