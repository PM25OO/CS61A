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

(define (my-filter pred s) 'YOUR-CODE-HERE)

(define (interleave lst1 lst2) 'YOUR-CODE-HERE)

(define (no-repeats s) 'YOUR-CODE-HERE)
