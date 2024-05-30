function print_float(val n: float);

function main() {
  print_float(sqrt(5.0));
}

function sqrt(val n: float): float {
  var guess: float := 1.0;
  while !good_enough(guess, n) {
    guess := improve(guess, n);
  }

  sqrt := guess;
}

function good_enough(val guess: float, val x: float): bool {
  if abs(guess*guess - x) < 0.001 {
    good_enough := true;  
  }  else {
    good_enough := false;
  }
}

function abs(val n: float): float {
  if n < 0.0 {
    abs := -n;
  } else {
    abs := n;
  }
}

function improve(val guess: float, val x: float): float {
  improve := (guess + (x / guess)) / 2.0;
}
