(define (ascending? s)
    (if (null? s)
        true
        (if (null? (cdr s))
            true
            (if (<= (car s) (car (cdr s)))
                (ascending? (cdr s))
                false
            )
        )
    )
)

(define (my-filter pred s)
    (if (null? s)
        nil
        (if (pred (car s))
            (cons (car s) (my-filter pred (cdr s)))
            (my-filter pred (cdr s))
        )
    )
)

(define (interleave lst1 lst2)
    (if (null? lst1)
        lst2
        (if (null? lst2)
            lst1
            (cons (car lst1) (cons (car lst2) (interleave (cdr lst1) (cdr lst2))))
        )
    )
)

(define (no-repeats s) 'YOUR-CODE-HERE)
