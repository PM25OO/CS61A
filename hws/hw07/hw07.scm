(define (square n) (* n n))

(define (pow base exp)
  (if (odd? exp)
      (* base (pow base (- exp 1)))
      (if (= exp 0)
          1
          (pow (square base) (/ exp 2))
      )
  )
)

(define (repeatedly-cube n x)
  (if (zero? n)
      x
      (let ((y (repeatedly-cube (- n 1) x)))
        (* y y y)
      )
  )
)

(define (cddr s) (cdr (cdr s)))

(define (cadr s) 'YOUR-CODE-HERE)

(define (caddr s) 'YOUR-CODE-HERE)
