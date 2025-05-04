(define (over-or-under num1 num2)
  (if (> num1 num2)
      1
      (if (= num1 num2)
          0
          -1)))

(define (make-adder num)
  (lambda (inc) (+ num inc)))

(define (composed f g)
  (lambda (x) (f (g x))))

(define (repeat f n)
  (if (= n 1)
      (lambda (x) (f x))
      (lambda (x) ((repeat f (- n 1)) (f x)))))

(define (max a b)
  (if (> a b)
      a
      b))

(define (min a b)
  (if (> a b)
      b
      a))

(define (gcd a b)
  (define Max (max a b))
  (define Min (min a b))
  (if (= (modulo Max Min) 0)
      Min
      (gcd Min (modulo Max Min))
  )
)
