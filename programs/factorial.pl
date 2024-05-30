function print_int(val n: int);

function fac(var n : int) : int {
	if n = 0 {
		fac := 1;
	}

	else {

		var res : int := 1;
		while n > 1 {
			res := res * n;
			n := n - 1;
		}

		fac := res;
	}
}

function main(val args : [string]) {
	val result : int := fac(4);
	print_int(result);
}
