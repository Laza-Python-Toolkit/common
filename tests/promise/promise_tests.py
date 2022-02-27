import pytest



xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


from laza.common.promises import Promise





class PromiseTests:

    def test_basic(self):
       
        pro = Promise()

        print(f'BEFORE: {pro!r}')

        # print(pro.cancel)
        p2 = pro.pipe(lambda v: Promise.cancelled(f'[PIPED][01] {v!r}'))
        
        p2.then(
            lambda v: print(f'[EMITTED] value    : {v!r}'),
            cancel=lambda v: print(f'[CANCELLED] reason : {v!r}'),
            fail  =lambda v: print(f'[ERRORED] reason   : {v!r}'),
        )
        
        pro.fulfil('There was a value')
        # cb[1]('Errrrorrrr')

        print(f'INNER : {p2!r}')
        print(f'AFTER : {pro!r}')

        assert 0


