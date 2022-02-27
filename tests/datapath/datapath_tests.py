import pytest



xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


from laza.common.datapath import DataPath





class BasicTests:

    def test_basic(self):

        class Foo:
            a = dict(list=list(range(10)), data=dict(bee='Im a bee'))

            class bar:
                
                @classmethod
                def run(cls, *args, **kwargs) -> None:
                    print(f'ran with({args=}, {kwargs=})')
                    return Foo


        p = DataPath().a['list'][2:-2]
        print(f'{p} --> {p.__eval__(Foo)!r}')

        p = DataPath().bar.run(1,2,3, k1=1, k2=2).a['list'][2:-2]
        print(f'{p} --> {p.__eval__(Foo)!r}')

        assert 0



